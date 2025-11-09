"""
Persistence layer backend for Draw-This.

This module defines the settings manager and its interface with a JSON file
used for persistence.

Classes:
    JsonPersistence: provides safe, atomic read and write API for the JSON
    format.

Usage:

"""

import json
from pathlib import Path
from typing import Optional, Callable

from iteradraw.domain.repositories.interfaces import Persistence


class JsonPersistence(Persistence):
    def __init__(
        self,
        namespace: str,
        settings_dir_path: str,
        file_name: str,
        on_write_error: Optional[Callable],
        on_read_error: Optional[Callable],
    ):
        self.namespace = namespace
        self.settings_dir_path = Path(settings_dir_path)
        self.settings_dir_path.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.settings_dir_path / file_name
        self.on_read_error = on_read_error
        self.on_write_error = on_write_error

    def read_file(self):
        """Parse file and restores previous resources's final values."""
        if not self.settings_file.exists():
            self.settings_file.touch()
        data = {}
        try:
            with open(self.settings_file, "r", encoding="utf-8") as config:
                data = json.load(config)
        except (json.JSONDecodeError, FileNotFoundError):
            if self.on_read_error:
                self.on_read_error()
        return data

    def write_file(self, data):
        """Create file and stores the current resources' values."""
        content = self.read_file()
        content[self.namespace] = data
        try:
            self._safe_json_write(self.settings_file, content)
        except FileNotFoundError:
            if self.on_write_error:
                self.on_write_error()

    @staticmethod
    def _safe_json_write(path: Path, data: dict) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")

        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        tmp.replace(path)
