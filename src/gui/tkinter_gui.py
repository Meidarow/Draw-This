import tkinter as tk
from tkinter import filedialog
import sys
from launcher.feh_backend import start_slideshow
import settings_manager as sett


class TkinterInterface:
    def __init__(self):
        self.settings_manager = sett.SettingsManager(folders=[], timers= [], last_timer= 0)
        self.folders = [(folder,tk.BooleanVar(value=enabled)) for folder, enabled in self.settings_manager.get_folders()]
        self.timers = self.settings_manager.get_timers()
        self.selected_timer = self.settings_manager.get_last_timer()
        self.start_folder = "/mnt/Storage/Art/Resources"
        self.database_folder = "/home/study/.config/draw-this/image_paths.db"

    def delete_item(self, value):
        if isinstance(value, str):
            self.folders = [t for t in self.folders if t[0] != value]
            return

        if isinstance(value, int):
            self.timers.remove(value)
            return

    def add_folder(self):
        folder_path = filedialog.askdirectory(initialdir=self.start_folder)
        if not folder_path or folder_path in [f for f, _ in self.folders]:
            return "", False

        var =  tk.BooleanVar(value=True)
        self.folders.append((folder_path, var))
        return folder_path, var

    def set_selected_timer(self, timer: int):
        self.selected_timer = timer

    def add_custom_timer(self, custom_timer):
        if custom_timer.get() == "":
            return

        self.add_timer(int(custom_timer.get()))

    def add_timer(self, timer: int):
        if timer in self.timers or timer == 0:
            return

        self.timers.append(timer)
        self.timers = sorted(self.timers)

    def get_folders(self):
        return [(folder, tk_enabled.get()) for (folder, tk_enabled) in self.folders]

    def get_tk_folders(self) -> list[tuple[str,tk.BooleanVar]]:
        return self.folders

    def get_last_timer(self):
        return self.selected_timer

    def get_timers(self) -> list[int]:
        return self.timers

    def start_slideshow(self, timer):
        self.set_selected_timer(timer.get())
        selected_folders = [folder for folder, enabled in self.get_folders() if enabled]
        if not selected_folders:
            return

        start_slideshow(selected_folders, geometry=None, drawing_time=self.selected_timer)
        self.settings_manager.set_last_timer(self.selected_timer)
        self.settings_manager.set_timers(self.timers)
        self.settings_manager.set_folders(self.get_folders())
        self.settings_manager.write_config()


class GuiBuilder:
    def __init__(self):
        self.folder_widgets = {}
        self.timer_widgets = {}

        self.root = tk.Tk()
        self.interface = TkinterInterface()
        self.root.title("Draw-This")
        self.root.geometry("1000x600")
        self.central_frame = tk.Frame(self.root)
        self.central_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.delay_var = tk.IntVar(value=self.interface.get_last_timer())
        self.folder_frame = tk.Frame(self.central_frame)
        self.folder_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.timer_frame = tk.Frame(self.central_frame)
        self.timer_frame.pack(fill="x", pady=10)
        self.console_frame = tk.Frame(self.central_frame)
        self.console_frame.pack(fill="both", expand=True, pady=10)

    def delete_widget(self, widget_dict: dict, widget_value):
        widget = widget_dict.pop(widget_value)
        self.interface.delete_item(widget_value)
        widget["button"].destroy()
        widget["delete_button"].destroy()
        if isinstance(widget_value,int):
            return

        widget["row"].destroy()


    def build_folder_section(self):
        # Folder section
        folders_label = tk.Label(self.folder_frame, text="Select folders:")
        folders_label.pack()

        for (folder, tk_enabled) in self.interface.get_tk_folders():
            folder_row = tk.Frame(self.folder_frame)
            folder_row.pack(fill="x", anchor="w", pady=1)
            cb = tk.Checkbutton(folder_row, text=folder, variable=tk_enabled)
            cb.pack(side="left", anchor="w")
            del_cb = tk.Button(folder_row, text="X", command=lambda f=folder: self.delete_widget(self.folder_widgets, f))
            del_cb.pack(side="right")
            self.folder_widgets[folder]= {"button":cb,"delete_button": del_cb, "row": folder_row}

    def build_timer_section(self):
        # Timer section
        timer_text = tk.Label(self.timer_frame, text="Select duration:")
        timer_text.pack()

        for timer in self.interface.get_timers():
            rb = tk.Radiobutton(self.timer_frame, text=f"{timer} seconds", variable=self.delay_var, value=timer)
            rb.pack(side="left")
            del_cb = tk.Button(self.timer_frame,text="X", command=lambda t=timer : self.delete_widget(self.timer_widgets,t))
            del_cb.pack(side="left")
            self.timer_widgets[timer]= {"button":rb,"delete_button": del_cb}

        timer_inf = tk.Radiobutton(self.timer_frame, text="indefinite", variable=self.delay_var, value=0)
        timer_inf.pack(side="right")

        custom_timer_frame = tk.Frame(self.central_frame)
        custom_timer_frame.pack(fill="x", pady=10)

        custom_entry = tk.Entry(custom_timer_frame, width=5)
        custom_timer_label_1 = tk.Label(custom_timer_frame, text="Custom: ")
        custom_timer_label_1.pack(side="left")
        custom_entry.pack(side="left")

        custom_timer_label = tk.Label(custom_timer_frame, text="seconds")
        custom_timer_label.pack(side="left", padx=5)
        add_button_timer = tk.Button(custom_timer_frame, text="Add", command=lambda: self.add_timer_and_refresh(custom_entry))
        add_button_timer.pack(side="left")

    def build_console_section(self):
        # Console section
        console_text = tk.Text(self.console_frame, height=10)
        console_text.pack(fill="both", expand=True)
        sys.stdout = StdoutRedirector(console_text)

    def add_folder_and_refresh(self):
        folder, var = self.interface.add_folder()
        if folder == "":
            return
        folder_row = tk.Frame(self.folder_frame)
        folder_row.pack(fill="x", anchor="w", pady=1)
        cb = tk.Checkbutton(folder_row, text=folder, variable=var)
        cb.pack(side="left", anchor="w")
        del_cb = tk.Button(folder_row,text="X", command=lambda f=folder: self.delete_widget(self.folder_widgets,f))
        del_cb.pack(side="right")
        self.folder_widgets[folder]= {"button":cb,"delete_button": del_cb, "row": folder_row}

    def add_timer_and_refresh(self, entry):
        self.interface.add_custom_timer(entry)
        for timer in self.timer_widgets.values():
            timer["button"].destroy()
            timer["delete_button"].destroy()
        self.timer_widgets.clear()

        for timer in self.interface.get_timers():
            rb = tk.Radiobutton(self.timer_frame, text=f"{timer} seconds", variable=self.delay_var, value=timer)
            rb.pack(side="left")
            del_cb = tk.Button(self.timer_frame,text="X", command=lambda t=timer: self.delete_widget(self.timer_widgets,t))
            del_cb.pack(side="left")
            self.timer_widgets[timer]= {"button":rb,"delete_button": del_cb}

    def build_buttons_section(self):
        add_button = tk.Button(self.central_frame, text="Add folder", command=lambda:self.add_folder_and_refresh())
        add_button.pack(pady=5)

        start_button = tk.Button(self.central_frame, text="Start", command=lambda: self.interface.start_slideshow(self.delay_var))
        start_button.pack(pady=5)

class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
    def write(self, s):
        self.text_widget.insert("end", s)
        self.text_widget.see("end")
    def flush(self):
        pass

window = GuiBuilder()
window.build_folder_section()
window.build_timer_section()
window.build_console_section()
window.build_buttons_section()
window.root.mainloop()