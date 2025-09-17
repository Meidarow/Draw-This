import tkinter as tk
from tkinter import filedialog
import sys
from launcher.feh_backend import start_slideshow
import settings.settings_manager as sett
import pathlib as path


"""
Tkinter GUI for Draw-This.

This module defines the GUI and its interface to the backend slideshow engine.
It has two main classes:

- TkinterInterface:
    Manages app state (folders, timers, selected timer) and bridges
    between GUI, backend, and persistence (settings).

- GuiBuilder:
    Constructs Tkinter widgets, binds them to interface state, and 
    handles user interaction (folder selection, timer selection, console output).

Usage
-----
Run this file directly to start the GUI:
    python tkinter_gui.py
"""

class TkinterInterface:
    """Manages app state and bridges GUI with backend and persistence layers.

        Attributes:
            :ivar folders (list[tuple[str, tk.BooleanVar]]): Folder paths with enabled flags.
            :ivar timers (list[int]): Available timers.
            :ivar selected_timer (int): Currently chosen timer duration.
        """

    def __init__(self):
        self.settings_manager = sett.SettingsManager(folders=[], timers= [], last_timer= 0)
        self.folders = [(folder,tk.BooleanVar(value=enabled)) for folder, enabled in self.settings_manager.get_folders()]
        self.timers = self.settings_manager.get_timers()
        self.selected_timer = self.settings_manager.get_last_timer()
        self.start_folder = "/mnt/Storage/Art/Resources"
        self.database_folder = path.Path("~/.config/draw-this/image_paths.db").expanduser()


    #Public API:

    def delete_item(self, value: str | int) -> None:
        """Removes a folder or timer from the attributes that store them.

                Args:
                    :param value: Folder or Timer to be deleted from internal list.
                """
        if isinstance(value, str):
            self.folders = [t for t in self.folders if t[0] != value]
            return

        if isinstance(value, int):
            self.timers.remove(value)
            return

    def add_folder(self) -> tuple[str, tk.BooleanVar]:
        """Asks user for a folder and adds new folder if not already present.
                """

        folder_path = filedialog.askdirectory(initialdir=self.start_folder)
        if not folder_path or folder_path in [f for f, _ in self.folders]:
            return "", tk.BooleanVar(value=False)

        var =  tk.BooleanVar(value=True)
        self.folders.append((folder_path, var))
        return folder_path, var

    def set_selected_timer(self, timer: int) -> None:
        """Sets internal attribute to a passes timer value.

                Args:
                    :param timer: Duration in seconds.
                """

        self.selected_timer = timer

    def add_custom_timer(self, custom_timer: tk.Entry) -> None:
        """Add a new timer selected by the user if field not empty.

                Args:
                    :param custom_timer: Duration in seconds selected by the user.
                """

        if custom_timer.get() == "":
            return

        self.add_timer(int(custom_timer.get()))

    def add_timer(self, timer: int) -> None:
        """Add a new timer if not already present.

                Args:
                    :param timer: Duration in seconds.
                """

        if timer in self.timers or timer == 0:
            return

        self.timers.append(timer)
        self.timers = sorted(self.timers)

    def start_slideshow(self, timer: tk.IntVar) -> None:
        """Passes GUI state to feh backend to start slideshow.

                Args:
                    :param timer: Slideshow duration in seconds.
                """

        self.set_selected_timer(timer.get())
        selected_folders = [folder for folder, enabled in self.get_folders() if enabled]
        if not selected_folders:
            return
        recalculate = self._should_recalculate()
        start_slideshow(selected_folders, geometry=None, drawing_time=self.selected_timer,
                        db_path=self.database_folder, recalculate=recalculate)
        self._save_session()


    #Acessors:

    def get_folders(self) -> list[tuple[str, bool]]:
        """Returns a list[tuple[str,bool]] of all folders.
                """

        return [(folder, tk_enabled.get()) for (folder, tk_enabled) in self.folders]

    def get_tk_folders(self) -> list[tuple[str,tk.BooleanVar]]:
        """Returns a list[tuple[str,tk.BooleanVar]] of all folders.
                """

        return self.folders

    def get_last_timer(self) -> int:
        """Returns the last used timer.
                """

        return self.selected_timer

    def get_timers(self) -> list[int]:
        """Returns a list[int] of all internal timers.
                """

        return self.timers


    #Private helpers:

    def _should_recalculate(self) -> bool:
        """Returns a bool indicating whether selected folders has changed
        since the last slideshow.
                """

        selected_folders = [folder for folder, enabled in self.get_folders() if enabled]
        previous_folders = [folder for folder, enabled in self.settings_manager.get_folders() if enabled]
        if selected_folders != previous_folders:
            return True
        return False

    def _save_session(self) -> None:
        """Sets all current parameters in the settings_manager and saves to config.json.
                """

        self.settings_manager.set_last_timer(self.selected_timer)
        self.settings_manager.set_timers(self.timers)
        self.settings_manager.set_folders(self.get_folders())
        self.settings_manager.write_config()


class GuiBuilder:
    """Build and maintains the GUI and sends state to interface module.

        Attributes:
            :ivar folder_widgets (dict(dict)): Current folder widgets displayed.
            :ivar timer_widgets (dict(dict)): Current timer widgets displayed.
            :ivar interface (TkinterInterface): Interface object for GUI-Backend communication.
            :ivar root (tk.Tk): Root tkinter window.
        """

    def __init__(self):
        self.folder_widgets = {}
        self.timer_widgets = {}

        self.root = tk.Tk()
        self.interface = TkinterInterface()
        self._build_window()

    def build_gui(self):
        self.build_folder_section()
        self.build_buttons_section()
        self.build_timer_section()

    def build_folder_section(self) -> None:
        """Assembles all components of the main window's vertical folder list section.
                """

        header_row = tk.Frame(self.folder_frame)
        header_row.pack(anchor="center", fill="x")
        folders_label = tk.Label(header_row, text="Select folders:")
        folders_label.pack(side="left")
        add_button = tk.Button(header_row, text="Add folder", command=lambda:self.add_folder_gui())
        add_button.pack(side="right")
        for (folder, tk_enabled) in self.interface.get_tk_folders():
            self._build_folder(folder,tk_enabled)

    def build_timer_section(self) -> None:
        """Assembles all components of the main window's horizontal timer list section.
                """

        timer_text = tk.Label(self.timer_frame, text="Select duration:")
        timer_text.pack()

        custom_timer_frame = tk.Frame(self.timer_frame)
        custom_timer_frame.pack(fill="x", pady=10)

        custom_entry = tk.Entry(custom_timer_frame, width=5)
        custom_timer_label_1 = tk.Label(custom_timer_frame, text="Custom: ")
        custom_timer_label_1.pack(side="left")
        custom_entry.pack(side="left")

        custom_timer_label = tk.Label(custom_timer_frame, text="seconds")
        custom_timer_label.pack(side="left", padx=5)
        add_button_timer = tk.Button(custom_timer_frame, text="Add", command=lambda: self.add_timer_gui(custom_entry))
        add_button_timer.pack(side="left")

        for timer in self.interface.get_timers():
            self._build_timer(timer)

        timer_inf = tk.Radiobutton(self.timer_frame, text="indefinite", variable=self.delay_var, value=0)
        timer_inf.pack(side="right")


    def add_folder_gui(self) -> None:
        """Adds a single folder, with its path received via user file dialog to the
        internal attribute and to the GUI.
                """

        folder, var = self.interface.add_folder()
        if folder == "":
            return
        self._build_folder(folder, var)

    def add_timer_gui(self, entry: tk.Entry) -> None:
        """Adds a single timer, with duration received via user interaction to the
        internal attribute and to the GUI.

                Args:
                    :param entry: Tkinter IntVar from the user entry field.
                """

        self.interface.add_custom_timer(entry)
        self._clear_gui_timers()

        for timer in self.interface.get_timers():
            self._build_timer(timer= timer)
            

    def build_buttons_section(self) -> None:
        """Assembles all components of the main window's "start" and "add folder" buttons.
                """

        start_button = tk.Button(self.main_frame, text="Start", command=lambda: self.interface.start_slideshow(self.delay_var))
        start_button.grid(row=1, column=1, sticky="nswe", padx=5)

    #Private helpers:

    def _build_window(self) -> None:
        """Assembles all base components of the main widget for the GUI.
                """

        self.root.title("Draw-This")
        self.root.geometry("1000x600")

        self.delay_var = tk.IntVar(value=self.interface.get_last_timer())

        # Main container with two columns
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Left: Folder list
        self.folder_canvas = tk.Canvas(self.main_frame, width=900)
        self.folder_scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.folder_canvas.yview)
        self.folder_frame = tk.Frame(self.folder_canvas, width= 890)

        self.folder_frame.bind(
            "<Configure>",
            lambda e: self.folder_canvas.configure(
                scrollregion=self.folder_canvas.bbox("all"),
            )
        )

        self.folder_canvas.configure(yscrollcommand=self.folder_scrollbar.set)
        self.folder_frame.grid()
        self.folder_canvas.grid(row=0, column=0, sticky="nswe")
        self.folder_scrollbar.grid(row=0, column=0, sticky="nse")
        self.main_frame.columnconfigure(0, weight=10)
        self.main_frame.rowconfigure(0, weight=1)

        # Right: Timers
        self.timer_frame = tk.Frame(self.main_frame, bd=1, relief="sunken", width=110)
        self.timer_frame.grid(row=0, column=1, sticky="ns", padx=5, pady=5)
        self.main_frame.columnconfigure(1, weight=0)  # make right column expand


    def _delete_widget(self, widget_dict: dict, widget_value: str | int) -> None:
        """Removes all components of a single widget from the GUI AND updates
        internal attributes to reflect that.

                Args:
                    :param widget_dict: Widget dict from which to remove widget
                    :param widget_value: [UNIQUE] Value of widget to be removed
                """

        widget = widget_dict.pop(widget_value)
        self.interface.delete_item(widget_value)
        for component in widget.values():
            component.destroy()
    
    def _clear_gui_timers(self):
        """Removes all components of a single timer from the GUI ONLY.
                """

        for timer in self.timer_widgets.values():
            for w in timer.values():
                w.destroy()
        self.timer_widgets.clear()
    
    def _build_timer(self, timer: int | str) -> None:
        """Assembles all components of a timer widget.

                Args:
                    :param timer: Duration in seconds of new timer
                """

        timer_row = tk.Frame(self.timer_frame)
        timer_row.pack(fill="x", anchor="w", pady=1)

        rb = tk.Radiobutton(timer_row, text=f"{timer} seconds", variable=self.delay_var, value=timer)
        rb.pack(side="left")
        del_cb = tk.Button(timer_row, text="X",
                           command=lambda t=timer: self._delete_widget(self.timer_widgets, t))
        del_cb.pack(side="left")
        self.timer_widgets[timer] = {"button": rb, "delete_button": del_cb, "row": timer_row}
        
    def _build_folder(self, folder: str, var: tk.BooleanVar) -> None:
        """Assembles all components of a folder widget.

                Args:
                    :param folder: Path to folder to be added
                    :param var: Whether to have the folder selected
                """

        folder_row = tk.Frame(self.folder_frame)
        folder_row.pack(fill="x", anchor="w", pady=1)
        cb = tk.Checkbutton(folder_row, text=folder, variable=var)
        cb.pack(side="left", anchor="w")
        del_cb = tk.Button(folder_row, text="X", command=lambda f=folder: self._delete_widget(self.folder_widgets, f))
        del_cb.pack(side="right")
        self.folder_widgets[folder] = {"button": cb, "delete_button": del_cb, "row": folder_row}


def main():
    window = GuiBuilder()
    window.build_gui()
    log_file = open("/tmp/draw_this.log", "w")
    sys.stdout = log_file
    sys.stderr = log_file

    try:
        window.root.mainloop()
    finally:
        log_file.close()

if __name__ == "__main__":
    main()
