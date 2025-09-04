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
    timer = tk.Radiobutton(timer_frame, text=f"{delay} seconds", variable=var, value=delay)
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
default_delay = [5, 32, 62, 302]

root = tk.Tk()
root.title("Draw-This Slideshow")
root.geometry("1000x600")

folder_vars =[]
delay_var = tk.IntVar(value=0)

# Frame central que segura tudo
central_frame = tk.Frame(root)
central_frame.place(relx=0.5, rely=0.5, anchor="center")

# Timer section
timer_frame = tk.Frame(central_frame)
timer_frame.pack(fill="x", pady=10)

timer_text = tk.Label(timer_frame, text="Select duration:")
timer_text.pack()

# Folder section
folder_frame = tk.Frame(central_frame)
folder_frame.pack(fill="both", expand=True, padx=10, pady=10)

folders_label = tk.Label(folder_frame, text="Select folders:")
folders_label.pack()

# Console section
console_frame = tk.Frame(central_frame)
console_frame.pack(fill="both", expand=True, pady=10)


# Botões
add_button = tk.Button(central_frame, text="Add folder", command=select_folder)
add_button.pack(pady=5)

start_button = tk.Button(central_frame, text="Start", command=start_slideshow_gui)
start_button.pack(pady=5)

for duration in default_delay:
    add_delay(str(duration),delay_var)

timer_inf = tk.Radiobutton(timer_frame, text="indefinite", variable=delay_var, value=0)
timer_inf.pack(side="right")

for folder in default_folders:
    add_folder(folder)

console_text = tk.Text(console_frame, height=10)
console_text.pack(fill="both", expand=True)
sys.stdout = StdoutRedirector(console_text)

root.mainloop()