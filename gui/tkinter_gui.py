import tkinter as tk
from tkinter import filedialog
from launcher.feh_backend import start_slideshow
import sys
import pathlib as path
import json


def add_delay(delay,var):
    duration_vars.append(delay)
    timer = tk.Radiobutton(timer_frame, text=f"{delay} seconds", variable=var, value=delay)
    timer.pack(side="left")

def add_folder(folder_path):
    var = tk.BooleanVar(value=True)
    folder_vars.append((folder_path, var))
    cb = tk.Checkbutton(folder_frame, text=folder_path, variable=var)
    cb.pack(anchor="w")

def select_folder():
    folder_path = filedialog.askdirectory(initialdir=start_folder)
    if folder_path:
        add_folder(folder_path)

def start_slideshow_gui():
    selected_folders = [path for path, var in folder_vars if var.get()]
    selected_delay = delay_var.get()

    if selected_folders:
        start_slideshow(selected_folders, geometry=None, drawing_time=selected_delay)
        save_last_settings(folder_vars,delay_var)

def add_custom_timer():
    if custom_entry.get() != "":
        add_delay(custom_entry.get(),delay_var)

def save_last_settings(folders,delay):
    serializable_folders = [{"path":path,"enabled":var.get()} for path, var in folders]
    serializable_timers = [{"duration": duration} for duration in duration_vars]
    config = {"folders":serializable_folders, "timers":serializable_timers, "last_selected":delay.get()}
    if serializable_folders or serializable_timers:
        write_config(data=config)

def restore_settings():
    config = read_config()
    folders_reload = [(item["path"], tk.BooleanVar(value=item["enabled"])) for item in config["folders"]]
    durations_reload = [item["duration"] for item in config["timers"]]
    return folders_reload, durations_reload

def write_config(data):
    config_path = path.Path("~/.config/draw-this").expanduser()
    config_path.mkdir(parents=True, exist_ok=True)
    with open(file=f"{config_path}/draw-this.json", mode='w+') as config:
        json.dump(obj=data, fp=config, indent=4)

def read_config():
    config_path = path.Path("~/.config/draw-this").expanduser()
    config_path.mkdir(parents=True, exist_ok=True)
    config_file = config_path /"draw-this.json"
    if config_file.exists() and config_file.stat().st_size != 0:
        with open(file=config_file, mode='r+') as config:
            read_data = json.load(fp=config)
    else:
        return {"folders": [], "timers": [], "last_selected": {}}
    return read_data


class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
    def write(self, s):
        self.text_widget.insert("end", s)
        self.text_widget.see("end")
    def flush(self):
        pass


start_folder = "/mnt/Storage/Art/Resources"

root = tk.Tk()
root.title("Draw-This Slideshow")
root.geometry("1000x600")

delay_var = tk.IntVar(value=0)
folder_vars, duration_vars= restore_settings()

# Frame central que segura tudo
central_frame = tk.Frame(root)
central_frame.place(relx=0.5, rely=0.5, anchor="center")


# Timer section
timer_frame = tk.Frame(central_frame)
timer_frame.pack(fill="x", pady=10)

timer_text = tk.Label(timer_frame, text="Select duration:")
timer_text.pack()

for duration in duration_vars:
    timer = tk.Radiobutton(timer_frame, text=f"{duration} seconds", variable=delay_var, value=duration)
    timer.pack(side="left")

timer_inf = tk.Radiobutton(timer_frame, text="indefinite", variable=delay_var, value=0)
timer_inf.pack(side="right")

custom_timer_frame = tk.Frame(central_frame)
custom_timer_frame.pack(fill="x", pady=10)

custom_entry = tk.Entry(custom_timer_frame,width=5)
custom_timer_label_1 = tk.Label(custom_timer_frame, text="Custom: ")
custom_timer_label_1.pack(side="left")
custom_entry.pack(side="left")

custom_timer_label = tk.Label(custom_timer_frame, text="seconds")
custom_timer_label.pack(side="left",padx=5)
add_button_timer = tk.Button(custom_timer_frame, text="Add", command=add_custom_timer)
add_button_timer.pack(side="left")


# Folder section
folder_frame = tk.Frame(central_frame)
folder_frame.pack(fill="both", expand=True, padx=10, pady=10)

folders_label = tk.Label(folder_frame, text="Select folders:")
folders_label.pack()

for folder, var in folder_vars:
    cb = tk.Checkbutton(folder_frame, text=folder, variable=var)
    cb.pack(anchor="w")


# Console section
console_frame = tk.Frame(central_frame)
console_frame.pack(fill="both", expand=True, pady=10)

console_text = tk.Text(console_frame, height=10)
console_text.pack(fill="both", expand=True)
sys.stdout = StdoutRedirector(console_text)


# Buttons
add_button = tk.Button(central_frame, text="Add folder", command=select_folder)
add_button.pack(pady=5)

start_button = tk.Button(central_frame, text="Start", command=start_slideshow_gui)
start_button.pack(pady=5)


root.mainloop()