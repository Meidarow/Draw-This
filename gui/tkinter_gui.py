import tkinter as tk
from tkinter import filedialog
from launcher.feh_backend import start_slideshow
import sys

last_folder = "/mnt/Storage/Art/Resources"

def add_folder(path):
    var = tk.BooleanVar(value=True)
    folder_vars.append((path, var))
    cb = tk.Checkbutton(folder_frame, text=path, variable=var)
    cb.pack(anchor="w")

def select_folder():
    path = filedialog.askdirectory(initialdir=last_folder)
    if path:
        add_folder(path)

def start_slideshow_gui():
    selected_folders = [path for path, var in folder_vars if var.get()]
    selected_delay = delay_var.get()

    if selected_folders:
        start_slideshow(selected_folders, geometry=None, drawing_time=selected_delay)

def add_delay(delay,var):
    timer = tk.Radiobutton(timer_frame, text=delay, variable=var, value=delay)
    timer.pack(side="left")


class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
    def write(self, s):
        self.text_widget.insert("end", s)
        self.text_widget.see("end")
    def flush(self):
        pass

default_folders = ["/mnt/Storage/Art/Resources/Animals","/mnt/Storage/Art/Resources/Humans/Figures/Non-Nude"]
default_delay = [35, 65, 5, 0]

root = tk.Tk()
root.title("Draw-This Slideshow")
root.geometry("1000x400")

folder_vars =[]
delay_var = tk.IntVar(value=0)

timer_frame = tk.Frame(root)
timer_frame.pack(fill="both")

folder_frame = tk.Frame(root)
folder_frame.pack(fill="both", expand=True, padx=10,pady=10)

console_frame = tk.Frame(root)
console_frame.pack(fill="both", expand=True)

console_text = tk.Text(console_frame, height=10)
console_text.pack(fill="both", expand=True)

timer_text = tk.Label(timer_frame,text="Select duration (0 is infinite): ")
timer_text.pack(side="left")

for duration in default_delay:
    add_delay(str(duration),delay_var)
timer_text_2 = tk.Label(timer_frame,text=" seconds")
timer_text_2.pack(side="left")

for folder in default_folders:
    add_folder(folder)

add_button = tk.Button(root, text="Add folder", command=select_folder)
add_button.pack(pady=5)

start_button = tk.Button(root, text="Start", command=start_slideshow_gui)
start_button.pack(pady=5)

sys.stdout = StdoutRedirector(console_text)

root.mainloop()