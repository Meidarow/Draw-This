import pathlib as path
import tkinter as tk
from drawthis.utils.config import SettingsManager
from drawthis.gui.viewmodel import TkinterViewmodel
from drawthis.gui.tkinter_gui import View, delete_widget
from drawthis.utils.filedialogs import select_file

START_FOLDER = path.Path("/mnt/Storage/Art/Resources")

class Coordinator:
    def __init__(self, app):
        self._settings_manager = SettingsManager()
        self.last_session = self._settings_manager.read_config()
        self._is_session_running = False
        self.viewmodel = TkinterViewmodel(self.last_session)
        self.view = View(self)
        self.app = app

    def run(self):
        self.view.build_gui()
        self.view.root.mainloop()

    def add_timer(self, new_timer: tk.Entry) -> None:
        """Add a new timer selected by the user if field not empty.

                Args:
                    :param new_timer: Duration in seconds selected by the user.
                """
        timer = new_timer.get()
        if timer == "" or timer == 0 or timer in self.viewmodel.timers:
            return

        self.viewmodel.add_timer(int(new_timer.get()))
        self.view.refresh_timer_gui(self.viewmodel.timers)

    def add_folder(self) -> None:
        """Asks user for a folder and adds new folder if not already present.
                """

        folder_path = select_file(root=START_FOLDER)
        if not folder_path or folder_path == "" or folder_path in self.viewmodel.folders:
            return

        self.viewmodel.add_folder(folder_path)
        self.view.add_folder_gui(folder_path, True)

    def delete_widget(self, widget_dict, item):
        self.viewmodel.delete_item(item)
        delete_widget(widget_dict, item)

    def run_slideshow(self):
        if not self._is_session_running:
            try:
                self._is_session_running = True
                self.app.run_slideshow(self.slideshow_data())
                self._save_session()
            finally:
                self._is_session_running = False

    def slideshow_data(self) -> dict:
        self.viewmodel.selected_timer = self.view.delay_var.get()
        slideshow_parameters = {
            "folders": [folder for folder, enabled in self.viewmodel.folders.items() if enabled],
            "selected_timer": self.viewmodel.selected_timer,
            "recalculate": self._should_recalculate()
        }
        return slideshow_parameters


    #Accessors

    def get_folders(self) -> list[tuple[str,bool]]:
        """Returns a list[tuple[str,bool]] of all folders.
                """

        return [item for item in self.viewmodel.folders.items()]

    def sync_folder(self, key, value):
        self.viewmodel.set_folder_enabled(key,value)

    def get_timers(self):

        return self.viewmodel.timers

    def get_last_timer(self):

        return self.last_session.get("selected_timer", 0)

    # Private helpers:

    def _save_session(self) -> None:
        """Sets all current parameters in the settings_manager and saves to config.json.
                """
        data = self.viewmodel.dump_state
        self._settings_manager.write_config(data)
        self.last_session = data

    def _should_recalculate(self) -> bool:
        """Returns a bool indicating whether selected folders has changed
        since the last slideshow.
                """

        selected_folders = {path for path, enabled in self.viewmodel.folders.items() if enabled}
        previous_folders = {item.get("path") for item in self.last_session.get("folders") if item.get("enabled") }
        if selected_folders != previous_folders:
            return True
        return False
