import threading
from typing import Type, Callable

from iteradraw.application.commands.interfaces import Command


class CommandBus:
    def __init__(self):
        self.handler_map = {}
        self.lock = threading.Lock()

    def register(self, command_type: Type[Command], handler: Callable):
        if command_type in self.handler_map:
            raise ValueError("Command already registered to a handler")
        with self.lock:
            self.handler_map[command_type] = handler

    def dispatch(self, command: Command):
        handler = self.handler_map.get(type(command))
        if not handler:
            raise ValueError("Command not registered to a handler.")
        handler(command)
