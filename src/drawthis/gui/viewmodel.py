import tkinter as tk
from tkinter import filedialog

from drawthis import Model, View, start_slideshow_ogl
from drawthis.app.constants import START_FOLDER, DATABASE_FILE
from drawthis.app.signals import (
    folder_added,
    timer_changed,
    widget_deleted,
    session_started,
    session_ended,
)
from drawthis.utils.logger import logger
from drawthis.utils.subprocess_queue import SignalQueue

BACKEND_FUNCTION = start_slideshow_ogl

"""
Viewmodel for Draw-This.

This model is the core of Draw-This, bridging the GUI and the model, and
initializing the slideshow.

- Viewmodel:
Interface between the View (GUI) and the Model (State/Persistence).
Provides methods to be called by the View, and listens to signals from
the Model to command the View to update.

Usage
-----
This file is imported by Main as a package according to the following:
     from drawthis import Viewmodel
"""


class Viewmodel:
    def __init__(self):
        self.model = Model()
        self.view = View(self)
        self.signal_queue = SignalQueue()

        self._tk_folders = [
            (folder, tk.BooleanVar(value=enabled))
            for folder, enabled in self.model.folders.items()
        ]
        self._tk_timers = self.model.timers

        self._subscribe_to_signals()

    # Public API

    def run(self) -> None:
        """Initializes the app."""
        try:
            self.view.build_gui()
            self._poll_signals()
            self.view.root.mainloop()
        except Exception as e:
            logger.critical(
                msg=f"Execution failed due to error: {e}", exc_info=True
            )
            raise

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
        """Ask user for a folder and add folder if not already present."""
        folder_path = filedialog.askdirectory(initialdir=START_FOLDER)
        if not folder_path or folder_path in self.model.folders:
            return

        self.model.add_folder(folder_path)

    def delete_widget(self, widget_type: str, value: str | int) -> None:
        """Remove widget of [value] from [widget_type] dict"""
        self.model.delete_item(widget_type=widget_type, value=value)

    def sync_folder(self, key: str, value: bool) -> None:
        """Update folder selected status in model"""
        self.model.set_folder_enabled(folder_path=key, enabled=value)

    def sync_selected_timer(self) -> None:
        """Update timer selected status in model"""
        self.model.selected_timer = self.view.delay_var.get()

    def start_slideshow(self) -> None:
        """Delegate slideshow operation to selected BACKEND"""
        if self.model.session_is_running:
            return
        self._recalculate_image_database()
        self.model.save_session()
        BACKEND_FUNCTION(
            queue=self.signal_queue.queue, **self.slideshow_parameters
        )

    # Accessors

    @property
    def tk_folders(self) -> list[tuple[str, tk.BooleanVar]]:
        """Return the list folders, with Tkinter vars."""
        return self._tk_folders

    @tk_folders.setter
    def tk_folders(self, value: list[tuple[str, tk.BooleanVar]]) -> None:
        """Set the list of folders, with Tkinter Vars."""
        self._tk_folders = value

    @property
    def enabled_folders(self) -> list[str]:
        """Return list of enabled folders"""
        return [
            folder for folder, enabled in self.model.folders.items() if enabled
        ]

    @property
    def tk_timers(self) -> list[int]:
        """Return list of timers, just normal integers"""
        return self._tk_timers

    @tk_timers.setter
    def tk_timers(self, value: list[int]) -> None:
        """Set list of timers, just normal integers"""
        self._tk_timers = value

    @property
    def last_timer(self) -> int:
        """Returns last used timer"""
        return self.model.last_session.get("selected_timer", 0)

    @property
    def slideshow_parameters(self):
        """Return dict of parameters passed into backend function"""
        return {
            "selected_timer": self.model.selected_timer,
        }

    # Private helpers

    def _recalculate_image_database(self):
        # If folders changed from last run, repopulate DB
        if not self.enabled_folders:
            return
        if self.model.should_recalculate():
            crawl_folders_iteratively(self.enabled_folders)

    def _subscribe_to_signals(self):
        folder_added.connect(self._on_folder_added)
        timer_changed.connect(self._on_timer_changed)
        widget_deleted.connect(self._on_widget_deleted)
        session_started.connect(self._on_session_started)
        session_ended.connect(self._on_session_ended)

    def _poll_signals(self):
        self.signal_queue.poll_queue()
        self.view.schedule(100, self._poll_signals)

    def _on_widget_deleted(
        self, _, widget_type: str, value: str | int
    ) -> None:
        self.view.delete_widget(widget_type=widget_type, widget_value=value)
        logger.info("Widget deleted.")

    def _on_timer_changed(self, _) -> None:
        self.tk_timers = self.model.timers
        self.view.refresh_timer_gui(self.model.timers)
        logger.info("Timer changed.")

    def _on_folder_added(self, _, folder_path) -> None:
        self.tk_folders = [
            (item[0], tk.BooleanVar(value=item[1]))
            for item in self.model.folders.items()
        ]
        self.view.add_folder_gui(
            folder=folder_path, enabled=tk.BooleanVar(value=True)
        )
        logger.info("Folder added.")

    def _on_session_started(self, _) -> None:
        self.model.session_is_running = True
        logger.info("Session started.")

    def _on_session_ended(self, _) -> None:
        self.model.session_is_running = False
        logger.info("Session ended.")


def crawl_folders_iteratively(folders):
    from drawthis import Crawler

    crawler = Crawler(DATABASE_FILE)
    crawler.clear_db()
    for folder in folders:
        crawler.crawl(folder)
