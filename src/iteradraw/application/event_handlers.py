class RemoveTimerCommand:
    """Manages app state and bridges GUI with backend and persistence layers.

    Do NOT mutate resources from outside the model.
    Attributes:
        :ivar folders (list[tuple[str, tk.BooleanVar]]):
        :ivar timers (list[int]):
        :ivar selected_timer (int): Currently chosen timer duration.
    """

    def __init__(self):
        self._settings_manager = SettingsManager()
        self.session = Session()
        self.last_session = Session()

    # Public API

    def load_last_session(self):
        """Explicitly load previous resources from settings."""
        self.last_session = self._settings_manager.read_config()
        self.session = self.last_session.copy()  # or maybe a copy

    def add_timer(self, timer: int) -> None:
        """
        Add timer to resources

        The timer with value 0 is internally the indefinite, default timer,
        and must not be added with add_timer

        Raises:
            ValueError: timers must be positive, non-zero integers
        """
        if timer <= 0:
            raise ValueError(f"Invalid timer inserted: {timer}")
        self.session.timers.add(timer)
        timer_changed.send(self)

    def add_folder(self, folder: str) -> None:
        """Add folder to resources"""
        self.session.folders.add(folder)
        folder_added.send(self, folder_path=folder)

    def delete_folder(self, path: str) -> None:
        """Delete folder from resources."""
        self.session.folders.remove(path)
        widget_deleted.send(self, widget_type="folder", value=path)

    def set_selected_timer(self, timer: int) -> None:
        """Set the selected timer"""
        self.session.selected_timer = timer

    def delete_timer(self, timer: int) -> None:
        """Delete timer from resources."""
        self.session.timers.remove(timer)
        widget_deleted.send(self, widget_type="timer", value=timer)

    def save_session(self) -> None:
        """Set resources parameters in settings_manager and persists"""
        self._settings_manager.write_config(self.session.copy())
        self.last_session = self.session.copy()


class AddTimerCommand:
    """Manages app state and bridges GUI with backend and persistence layers.

    Do NOT mutate resources from outside the model.
    Attributes:
        :ivar folders (list[tuple[str, tk.BooleanVar]]):
        :ivar timers (list[int]):
        :ivar selected_timer (int): Currently chosen timer duration.
    """

    def __init__(self):
        self._settings_manager = SettingsManager()
        self.session = Session()
        self.last_session = Session()

    # Public API

    def load_last_session(self):
        """Explicitly load previous resources from settings."""
        self.last_session = self._settings_manager.read_config()
        self.session = self.last_session.copy()  # or maybe a copy

    def add_timer(self, timer: int) -> None:
        """
        Add timer to resources

        The timer with value 0 is internally the indefinite, default timer,
        and must not be added with add_timer

        Raises:
            ValueError: timers must be positive, non-zero integers
        """
        if timer <= 0:
            raise ValueError(f"Invalid timer inserted: {timer}")
        self.session.timers.add(timer)
        timer_changed.send(self)

    def add_folder(self, folder: str) -> None:
        """Add folder to resources"""
        self.session.folders.add(folder)
        folder_added.send(self, folder_path=folder)

    def delete_folder(self, path: str) -> None:
        """Delete folder from resources."""
        self.session.folders.remove(path)
        widget_deleted.send(self, widget_type="folder", value=path)

    def set_selected_timer(self, timer: int) -> None:
        """Set the selected timer"""
        self.session.selected_timer = timer

    def delete_timer(self, timer: int) -> None:
        """Delete timer from resources."""
        self.session.timers.remove(timer)
        widget_deleted.send(self, widget_type="timer", value=timer)

    def save_session(self) -> None:
        """Set resources parameters in settings_manager and persists"""
        self._settings_manager.write_config(self.session.copy())
        self.last_session = self.session.copy()
