import threading
import weakref
from enum import StrEnum
from typing import Callable, Any

# """ TODO
# Logger _.
#
# This module defines the logger and it's functionality.
# It has one class:
#
# - Logger:
# Rotates a file based on file size, logs to stream also.
#
# Usage
# -----
# This file is imported by Viewmodel as a package according to the following:
#     from drawthis import Logger
# """
#
# logger = logging.getLogger("drawthis")
# logger.setLevel(logging.DEBUG)
#
# file_handler = RotatingFileHandler(LOG_FOLDER, encoding="utf-8")
# file_handler.setLevel(level=logging.DEBUG)
# file_handler.setFormatter(
#     fmt=logging.Formatter(
#         "%(asctime)s [%(levelname)s] (%(name)s): (%(message)s)"
#     )
# )
# stream_handler = logging.StreamHandler()
# stream_handler.setLevel(level=logging.WARNING)
# stream_handler.setFormatter(
#     fmt=logging.Formatter("[%(levelname)s] (%(name)s): (%(message)s)")
# )
#
# if not logger.handlers:
#     logger.addHandler(file_handler)
#     logger.addHandler(stream_handler)


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


class EVENTS(StrEnum):
    """All event names, used for indexing in EventBus"""

    ADD_FOLDER = "add_folder"
    FOLDER_ADDED = "folder_added"
    REMOVE_FOLDER = "remove_folder"
    FOLDER_REMOVED = "folder_removed"
    ADD_TIMER = "add_timer"
    TIMER_ADDED = "timer_added"
    REMOVE_TIMER = "remove_timer"
    TIMER_REMOVED = "timer_removed"
    REQUEST_SESSION = "request_session"
    SESSION_VERIFIED = "session_verified"
    START_SESSION = "start_session"
    SESSION_STARTED = "session_started"
    SESSION_FAILED = "session_failed"


class Event:
    def __init__(self, name: EVENTS, payload=None, meta=None, sender=None):
        self.name = name
        self.payload = payload
        self.meta = meta
        self.sender = sender


class EventBus:
    def __init__(self):
        self.listeners: dict[EVENTS, list[Callable]] = {}
        self._lock = threading.Lock()
        self._populate_events()
        self._middleware: list[Callable[[Event, str, Any], None]] = []

    def publish(self, event: Event):
        with self._lock:
            listeners = list(self.listeners.get(event.name, []))
        for subscriber in listeners:
            try:
                subscriber(event.payload)
                self._notify_middleware(event, "subscriber_notified", None)
            except Exception as e:
                self._notify_middleware(
                    event, "error", {"error": e, "subscriber": subscriber}
                )

                continue
        self._notify_middleware(event, "publish", None)

    def subscribe(
        self, event_name: EVENTS, listener: Callable, weak: bool = False
    ):
        with self._lock:
            if event_name not in self.listeners:
                self.listeners[event_name] = []

            ref = weakref.ref(listener) if weak else listener
            if ref not in self.listeners[event_name]:
                self.listeners[event_name].append(ref)
        self._notify_middleware(
            None, "subscribe", {"event_name": event_name, "listener": listener}
        )

    def unsubscribe(self, event_name: EVENTS, listener: Callable):
        with self._lock:
            if (
                event_name in self.listeners
                and listener in self.listeners[event_name]
            ):
                self.listeners[event_name].remove(listener)
        self._notify_middleware(
            None,
            "unsubscribe",
            {"event_name": event_name, "listener": listener},
        )

    def reset(self):
        """Clear event bus dicts"""
        with self._lock:
            self.listeners.clear()
            self._populate_events()

    def add_middleware(self, function: Callable[[Event, str, Any], None]):
        if not function in self._middleware:
            self._middleware.append(function)

    def _notify_middleware(self, event, event_name, data):
        for function in self._middleware:
            function(event, event_name, data)

    def _populate_events(self):
        for event in EVENTS:
            self.listeners[event] = []
