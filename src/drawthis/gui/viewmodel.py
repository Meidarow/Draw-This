import pathlib as path
import tkinter as tk

from drawthis import Model, View, select_file
from drawthis.app.signals import folder_added, timer_changed, widget_deleted

START_FOLDER = path.Path("/mnt/Storage/Art/Resources")

class Viewmodel:
    def __init__(self, app):
        self.model = Model()
        self.view = View(self)
        self.app = app

        self._tk_folders = [(folder, tk.BooleanVar(value=enabled)) for folder, enabled in self.model.folders.items()]
        self._tk_timers = self.model.timers

        # Signals:
        folder_added.connect(self.on_folder_added)
        timer_changed.connect(self.on_timer_changed)
        widget_deleted.connect(self.on_widget_deleted)

    def run(self):
        self.view.build_gui()
        self.view.root.mainloop()


    def add_timer(self, new_timer: tk.Entry) -> None:
        """Add a new timer selected by the user if field not empty.

                Args:
                    :param new_timer: Duration in seconds selected by the user.
                """
        timer = new_timer.get()
        if timer == "" or timer == 0 or timer in self.model.timers:
            return

        self.model.add_timer(int(new_timer.get()))

    def on_timer_changed(self, _):
        self.tk_timers = self.model.timers
        self.view.refresh_timer_gui(self.model.timers)


    def add_folder(self) -> None:
        """Asks user for a folder and adds new folder if not already present.
                """

        folder_path = select_file(root=START_FOLDER)
        if not folder_path or folder_path in self.model.folders:
            return

        self.model.add_folder(folder_path)

    def on_folder_added(self, _, folder_path):
        self.tk_folders = [(item[0],tk.BooleanVar(value=item[1])) for item in self.model.folders.items()]
        self.view.add_folder_gui(folder=folder_path, enabled=tk.BooleanVar(value=True))


    def delete_widget(self, widget_type, item):
        self.model.delete_item(widget_type, item)

    def on_widget_deleted(self, _, widget_type, value):
        self.view.delete_widget(widget_type, value)


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

    def sync_folder(self, key, value):
        self.model.set_folder_enabled(key,value)

    def sync_selected_timer(self):
        self.model.selected_timer = self.view.delay_var.get()
    # Private helpers:

    def start_slideshow(self):
        if not self.model.is_session_running:
            try:
                self.model.is_session_running = True
                slideshow_parameters = {
                    "folders": [folder for folder, enabled in self.model.folders.items() if enabled],
                    "selected_timer": self.model.selected_timer,
                    "recalculate": self.model.should_recalculate()
                }
                self.model.save_session()

                self.app.run_slideshow(slideshow_parameters)
            finally:
                self.model.is_session_running = False
