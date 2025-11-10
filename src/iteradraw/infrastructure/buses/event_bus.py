import threading
import weakref
from typing import Callable, Any, Type

from iteradraw.domain.events.domain_events import Event

"""
Implements the event bus pub/sub system for Draw-This.

Purpose:
The event bus implements a centralized publishing and subscribing system to
facilitate intermodule communication and datatransfer, and allow a clear
chronological structure for event pipelines.

Implementation:
The module revolves around a dict with key : list[Callable, ...],
in which events (keys) index a list of methods or callables tied to
subscribers of the event.
Essentially, when an event gets emitted, the bus seeks its index in the dict,
and calls the methods in the list either in the order they were added, FIFO,
or sorted by priority values.
Some events are tied to payloads and/or metadata, which are data specifically
tied to that event, and are defined by the receivers necessity/expectation.

Assumptions:
  - Events and payloads are identical in structure across iterations
  - Dataclasses for payloads are immutable and explicitly defined

Guarantees:
  - Data is not mutated in transport
  - All subscribers in the list get called (no call method interrupts this)
  - Errors must not disrupt the bus' function
  - No single-event-side-effects cascades where each callable edits the
    payload directly until the final subscriber's callable.
    Instead: each modification/verification has its own event and emits
    well defined events and payloads in sychronous form, defining a pipeline.
"""


class EventBus:
    def __init__(self):
        self.listeners: dict[Type[Event], list[Callable]] = {}
        self._lock = threading.Lock()
        self._middleware: list[Callable[[Event, str, Any], None]] = []

    def publish(self, event: Event):
        with self._lock:
            listeners = list(self.listeners.get(type(event), []))
        for subscriber in listeners:
            try:
                subscriber(event)
                self._notify_middleware(event, "subscriber_notified", None)
            except Exception as e:
                self._notify_middleware(
                    event, "error", {"error": e, "subscriber": subscriber}
                )

                continue
        self._notify_middleware(event, "publish", None)

    def subscribe(
        self, event_type: Type[Event], listener: Callable, weak: bool = False
    ):
        with self._lock:
            if event_type not in self.listeners:
                self.listeners[event_type] = []

            ref = weakref.ref(listener) if weak else listener
            if ref not in self.listeners[event_type]:
                self.listeners[event_type].append(ref)
        self._notify_middleware(
            None, "subscribe", {"event_type": event_type, "listener": listener}
        )

    def unsubscribe(self, event_type: Type[Event], listener: Callable):
        with self._lock:
            if (
                event_type in self.listeners
                and listener in self.listeners[event_type]
            ):
                self.listeners[event_type].remove(listener)
        self._notify_middleware(
            None,
            "unsubscribe",
            {"event_type": event_type, "listener": listener},
        )

    def reset(self):
        """Clear event bus dicts"""
        with self._lock:
            self.listeners.clear()

    def add_middleware(self, function: Callable[[Event, str, Any], None]):
        if not function in self._middleware:
            self._middleware.append(function)

    def _notify_middleware(self, event, event_name, data):
        for function in self._middleware:
            function(event, event_name, data)
