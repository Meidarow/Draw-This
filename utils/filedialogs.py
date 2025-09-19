from tkinter import filedialog


def select_file(root) -> str:
    return filedialog.askdirectory(initialdir=root)