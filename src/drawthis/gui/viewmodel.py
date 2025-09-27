import pathlib as path
import tkinter as tk

from drawthis import Model, View, select_file, start_slideshow_ogl
from drawthis.app.signals import folder_added, timer_changed, widget_deleted, session_running, session_ended
from drawthis.utils.logger import Logger

START_FOLDER = path.Path("/mnt/Storage/Art/Resources")
BACKEND_FUNCTION = start_slideshow_ogl
DATABASE_FOLDER = path.Path("~/.config/draw-this/image_paths.db").expanduser()

class Viewmodel:
    def __init__(self):
        self.model = Model()
        self.view = View(self)
        self.logger = Logger()
        self.logger.start_log()

        self._tk_folders = [(folder, tk.BooleanVar(value=enabled)) for folder, enabled in self.model.folders.items()]
        self._tk_timers = self.model.timers

        # Signals:
        folder_added.connect(self._on_folder_added)
        timer_changed.connect(self._on_timer_changed)
        widget_deleted.connect(self._on_widget_deleted)
        session_running.connect(self._on_session_running)
        session_ended.connect(self._on_session_ended)


    # Public API

    def run(self):
        try:
            self.view.build_gui()
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

        folder_path = select_file(root=START_FOLDER)
        if not folder_path or folder_path in self.model.folders:
            return

        self.model.add_folder(folder_path)
    def delete_widget(self, widget_type, item):
        self.model.delete_item(widget_type, item)

    def sync_folder(self, key, value):
        self.model.set_folder_enabled(key,value)

    def sync_selected_timer(self):
        self.model.selected_timer = self.view.delay_var.get()

    def start_slideshow(self):
        if self.model.is_session_running:
            return
        try:
            slideshow_parameters = {
                "folders": [folder for folder, enabled in self.model.folders.items() if enabled],
                "selected_timer": self.model.selected_timer,
                "recalculate": self.model.should_recalculate()
            }
            self.model.save_session()
            if not slideshow_parameters.get("folders"):
                return
            BACKEND_FUNCTION(db_path=DATABASE_FOLDER, **slideshow_parameters)
        finally:
            return


    #Accessors

    @property
    def tk_folders(self) -> list[tuple[str,tk.BooleanVar]]:
        """Returns a list[tuple[str,bool]] of all folders.
                """

        return self._tk_folders

    @tk_folders.setter
    def tk_folders(self, value) -> None:
        """Returns a list[tuple[str,bool]] of all folders.
                """

        self._tk_folders = value

    @property
    def tk_timers(self):

        return self._tk_timers

    @tk_timers.setter
    def tk_timers(self, value):

        self._tk_timers = value

    @property
    def last_timer(self):

        return self.model.last_session.get("selected_timer", 0)


    # Private helpers

    def _on_widget_deleted(self, _, widget_type, value):
        self.view.delete_widget(widget_type, value)

    def _on_timer_changed(self, _):
        self.tk_timers = self.model.timers
        self.view.refresh_timer_gui(self.model.timers)

    def _on_folder_added(self, _, folder_path):
        self.tk_folders = [(item[0],tk.BooleanVar(value=item[1])) for item in self.model.folders.items()]
        self.view.add_folder_gui(folder=folder_path, enabled=tk.BooleanVar(value=True))

    def _on_session_running(self, text):
        self.model.is_session_running = True
        print(text)

    def _on_session_ended(self):
        self.model.is_session_running = False