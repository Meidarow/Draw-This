import sys
import pathlib as path
import tkinter as tk
from drawthis.render.feh_backend import start_slideshow
from drawthis.app.controller import start_slideshow_ogl
from drawthis.gui.model import TkinterInterface
from drawthis.gui.tkinter_gui import GuiBuilder, delete_widget
from drawthis.utils.filedialogs import select_file

#[(folder,tk.BooleanVar(value=enabled)) for folder, enabled in
class GuiController:
    def __init__(self):
        self.start_folder = "/mnt/Storage/Art/Resources"
        self.log_folder = path.Path("/tmp/draw_this.log")
        self.database_folder = path.Path("~/.config/draw-this/image_paths.db").expanduser()
        #self.controller = AppController()
        self.viewmodel = TkinterInterface()
        self.view = GuiBuilder(self)

    def add_timer(self, new_timer: tk.Entry) -> None:
        """Add a new timer selected by the user if field not empty.

                Args:
                    :param new_timer: Duration in seconds selected by the user.
                """
        timer = new_timer.get()
        if timer == "" or timer == 0 or timer in self.viewmodel.get_timers():
            return

        self.viewmodel.add_timer(int(new_timer.get()))
        self.view.refresh_timer_gui(self.viewmodel.get_timers())

    def add_folder(self) -> None:
        """Asks user for a folder and adds new folder if not already present.
                """

        folder_path = select_file(root=self.start_folder)
        if not folder_path or folder_path == "" or folder_path in self.viewmodel.get_folders():
            return

        self.viewmodel.add_folder(folder_path)
        self.view.add_folder_gui(folder_path)

    def delete_widget(self, widget_dict, item):
        self.viewmodel.delete_item(item)
        delete_widget(widget_dict, item)

    def start_gui(self):
        self.view.build_gui()
        log_file = open(self.log_folder, "w")
        sys.stdout = log_file
        sys.stderr = log_file

        try:
            self.view.root.mainloop()
        finally:
            log_file.close()

    def start_slideshow(self) -> None:
        """Passes GUI state to feh backend to start slideshow.

                Args:
                """

        current_state = self.viewmodel.get_current_state()
        selected_folders = current_state["folders"]
        selected_timer = current_state["timer"]
        recalculate = current_state["recalculate"]
        if not selected_folders:
            return
        start_slideshow(
            folders=selected_folders,
            geometry=None,
            drawing_time=selected_timer,
            db_path=self.database_folder,
            recalculate=recalculate
        )
        self.viewmodel.save_session()

    def start_slideshow_gl(self) -> None:
        """Passes GUI state to OpenGL backend to start slideshow.

                Args:
                """

        current_state = self.viewmodel.get_current_state()
        selected_folders = current_state["folders"]
        selected_timer = current_state["timer"]
        recalculate = current_state["recalculate"]

        if not selected_folders:
            return
        start_slideshow_ogl(
            recalculate=recalculate,
            folders=selected_folders
        )
        self.viewmodel.save_session()

    def sync_folder(self, key, value):
        self.viewmodel.get_folders()[key] = value

    def get_tk_folders(self) -> list[tuple[str,tk.BooleanVar]]:
        """Returns a list[tuple[str,tk.BooleanVar]] of all folders.
                """

        return [(item[0], tk.BooleanVar(value=item[1])) for item in self.viewmodel.get_folders().items()]

    def get_timers(self):

        return self.viewmodel.get_timers()

    def get_last_timer(self):

        return self.viewmodel.get_selected_timer()