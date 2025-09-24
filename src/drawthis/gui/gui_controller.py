import sys
import pathlib as path
import tkinter as tk
from drawthis.render.feh_backend import start_slideshow
from drawthis.app.controller import start_slideshow_ogl
from drawthis.gui.viewmodel import TkinterViewmodel
from drawthis.gui.tkinter_gui import GuiBuilder, delete_widget
from drawthis.utils.filedialogs import select_file

BACKEND_FUNCTION = start_slideshow
START_FOLDER = path.Path("/mnt/Storage/Art/Resources")
LOG_FOLDER = path.Path("/tmp/draw_this.log")
DATABASE_FOLDER = path.Path("~/.config/draw-this/image_paths.db").expanduser()


class GuiController:
    def __init__(self):
        self.viewmodel = TkinterViewmodel()
        self.view = GuiBuilder(self)

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

    def start_gui(self):
        self.view.build_gui()
        log_file = open(LOG_FOLDER, "w")
        sys.stdout = log_file
        sys.stderr = log_file

        try:
            self.view.root.mainloop()
        finally:
            log_file.close()

    def run_slideshow(self):
        current_state = self.viewmodel.current_state
        if not current_state.get("folders"):
            return
        BACKEND_FUNCTION(db_path=DATABASE_FOLDER, **current_state)
        self.viewmodel.save_session()

    def get_folders(self) -> list[tuple[str,bool]]:
        """Returns a list[tuple[str,bool]] of all folders.
                """

        return [item for item in self.viewmodel.folders.items()].copy()

    def sync_folder(self, key, value):
        self.viewmodel.folders[key] = value

    def get_timers(self):

        return self.viewmodel.timers

    def get_last_timer(self):

        return self.viewmodel.selected_timer