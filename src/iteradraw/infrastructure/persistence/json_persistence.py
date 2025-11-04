"""
Persistence manager for Draw-This.

This module defines the settings manager and its interface with a JSON file
used for persistence.
It has a single class:

- SettingsManager:
Manages persistence of app state (folders, timers, selected timer) across
multiple runs
and can store previous resources parameters in a JSON file in ~/.config/.

Usage
-----
This file is imported as a package according to the following:
    import settings.settings_manager
"""

import json
from abc import ABC
from pathlib import Path
from typing import Optional, Callable

from iteradraw.domain.models.session import Session
from iteradraw.domain.repositories.interfaces import ModelType, Persistence


class JsonSettingsPersistence(Persistence, ABC):
    def __init__(
        self,
        model_cls: ModelType,
        on_write_error: Optional[Callable],
        on_read_error: Optional[Callable],
    ):
        self.model_cls = model_cls
        self.settings_dir_path = Path(self.model_cls.settings_dir_path)
        self.settings_dir_path.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.settings_dir_path / self.model_cls.file_name
        self.on_read_error = on_read_error
        self.on_write_error = on_write_error

    def read_file(self):
        """Parse file and restores previous resources's final values."""
        if not self.settings_file.exists():
            self.settings_file.touch()
        data = None
        try:
            with open(self.settings_file, "r", encoding="utf-8") as config:
                data = json.load(config)
        except (json.JSONDecodeError, FileNotFoundError):
            if self.on_read_error:
                self.on_read_error()
        defaults = self._make_default_dict()
        merged = defaults.copy()
        if data:
            merged.update({k: v for k, v in data.items() if k in defaults})
        return self._make_object(merged)

    def write_file(self, model_object):
        """Create file and stores the current resources' values."""
        model_object_dict = self._make_dict(model_object)
        try:
            self._safe_json_write(self.settings_file, model_object_dict)
        except FileNotFoundError:
            if self.on_write_error:
                self.on_write_error()

    @staticmethod
    def _safe_json_write(path: Path, data: dict) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")

        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        tmp.replace(path)

    @staticmethod
    def _make_dict(model_object) -> dict:
        return model_object.to_dict()

    def _make_object(self, model_object_dict):
        return self.model_cls.from_dict(model_object_dict)

    def _make_default_dict(self) -> dict:
        return self.model_cls().to_dict()


# TODO implement the settings dir and filenames for the differente models,
#  all else is already clean and generic


class AppSettingsPersistence(JsonSettingsPersistence):
    """Defines the API of app user preferences persistence."""

    def __init__(self):
        super().__init__(
            settings_dir_path=APPSETTINGS.DEFAULTS.SETTINGS_DIR,
            file_name=APPSETTINGS.DEFAULTS.FILE_NAME,
            model_cls=AppSettings,
            on_read_error=None,
            on_write_error=None,
        )


class SlideshowSettingsPersistence(JsonSettingsPersistence):
    """Defines the API of slideshow preferences persistence."""

    def __init__(self):
        super().__init__(
            settings_dir_path=SlideshowDefaults.SETTINGS_DIR,
            file_name=SlideshowDefaults.FILE_NAME,
            model_cls=Session,
            on_read_error=None,
            on_write_error=None,
        )
