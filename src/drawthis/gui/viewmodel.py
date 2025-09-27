import pathlib as path
import tkinter as tk
from tkinter import filedialog

from drawthis import Model, View, start_slideshow_ogl, start_slideshow_feh
from drawthis.app.signals import folder_added, timer_changed, widget_deleted, session_started, session_ended
from drawthis.utils.logger import Logger
from drawthis.utils.subprocess_queue import SignalQueue

"""
Viewmodel for Draw-This.

This model is the core of Draw-This, bridging the GUI and the model, and
initializing the slideshow.

- Viewmodel:
    Interface between the View (GUI) and the Model (State/Persistence). Provides methods to be called
    upon by the View, and listens to signals from the Model to command the View to update.

Usage
-----
This file is imported by Main as a package according to the following:
     from drawthis import Viewmodel
"""

START_FOLDER = path.Path("/mnt/Storage/Art/Resources")
BACKEND_FUNCTION = start_slideshow_ogl
DATABASE_FOLDER = path.Path("~/.config/draw-this/image_paths.db").expanduser()

class Viewmodel:
    def __init__(self):
        self.model = Model()
        self.view = View(self)
        self.logger = Logger()
        self.logger.start_log()
        self.signal_queue = SignalQueue()

        self._tk_folders = [(folder, tk.BooleanVar(value=enabled)) for folder, enabled in self.model.folders.items()]
        self._tk_timers = self.model.timers

        # Signals:
        folder_added.connect(self._on_folder_added)
        timer_changed.connect(self._on_timer_changed)
        widget_deleted.connect(self._on_widget_deleted)
        session_started.connect(self._on_session_started)
        session_ended.connect(self._on_session_ended)


    # Public API

    def run(self) -> None:
        """Initializes the app."""
        try:
            self.view.build_gui()
            self._poll_signals()
            self.view.root.mainloop()
        finally:
            self.logger.end_log()

    def add_timer(self, new_timer: tk.Entry) -> None:
        """Add a new timer selected by the user if field not empty.

                Args:
                    :param new_timer: Duration in seconds selected by the user.
                """
        timer = new_timer.get()
        if timer == "" or timer == 0 or timer in self.model.timers:
            return

        self.model.add_timer(int(new_timer.get()))

    def add_folder(self) -> None:
        """Asks user for a folder and adds new folder if not already present.
                """

        folder_path = filedialog.askdirectory(initialdir=START_FOLDER)
        if not folder_path or folder_path in self.model.folders:
            return

        self.model.add_folder(folder_path)

    def delete_widget(self, widget_type: str, value: str | int) -> None:
        self.model.delete_item(widget_type=widget_type, value=value)

    def sync_folder(self, key: str, value: bool) -> None:
        self.model.set_folder_enabled(folder_path=key,enabled=value)

    def sync_selected_timer(self) -> None:
        self.model.selected_timer = self.view.delay_var.get()

    def start_slideshow(self) -> None:
        if self.model.is_session_running:
            return
        try:
            # session_started.send(self)
            slideshow_parameters = {
                "folders": [folder for folder, enabled in self.model.folders.items() if enabled],
                "selected_timer": self.model.selected_timer,
                "recalculate": self.model.should_recalculate()
            }
            self.model.save_session()
            if not slideshow_parameters.get("folders"):
                return
            BACKEND_FUNCTION(db_path=DATABASE_FOLDER,queue= self.signal_queue, **slideshow_parameters)
        finally:
            return


    #Accessors

    @property
    def tk_folders(self) -> list[tuple[str,tk.BooleanVar]]:
        """Returns a list[tuple[str,tk.BooleanVar]] of all folders.
                """

        return self._tk_folders

    @tk_folders.setter
    def tk_folders(self, value: list[tuple[str,tk.BooleanVar]]) -> None:
        """Modifies a list[tuple[str,tk.BooleanVar]] of all folders.
                """

        self._tk_folders = value

    @property
    def tk_timers(self) -> list[int]:

        return self._tk_timers

    @tk_timers.setter
    def tk_timers(self, value: list[int]) -> None:

        self._tk_timers = value

    @property
    def last_timer(self) -> int:

        return self.model.last_session.get("selected_timer", 0)


    # Private helpers

    def _poll_signals(self):
        self.signal_queue.poll_queue()
        self.view.schedule(100, self._poll_signals)

    def _on_widget_deleted(self, _, widget_type: str, value: str | int) -> None:
        self.view.delete_widget(widget_type=widget_type, widget_value=value)

    def _on_timer_changed(self, _) -> None:
        self.tk_timers = self.model.timers
        self.view.refresh_timer_gui(self.model.timers)

    def _on_folder_added(self, _, folder_path) -> None:
        self.tk_folders = [(item[0],tk.BooleanVar(value=item[1])) for item in self.model.folders.items()]
        self.view.add_folder_gui(folder=folder_path, enabled=tk.BooleanVar(value=True))

    def _on_session_started(self, _) -> None:
        self.model.is_session_running = True

    def _on_session_ended(self, _) -> None:
        self.model.is_session_running = False