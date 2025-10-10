from drawthis.core.models.resources.dataclasses import Session
from drawthis.core.types import JsonSettingsPersistence

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
