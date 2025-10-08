from drawthis.core.models.settings.dataclasses import APPSETTINGS, AppSettings
from drawthis.core.protocols.protocols import JsonSettingsPersistence

"""
Persistence manager for Draw-This.

This module defines the settings manager and its interface with a JSON file
used for persistence.
It has a single class:

- SettingsManager:
Manages persistence of app state (folders, timers, selected timer) across
multiple runs
and can store previous session parameters in a JSON file in ~/.config/.

Usage
-----
This file is imported as a package according to the following:
    import settings.settings_manager
"""


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
