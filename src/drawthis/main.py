import sys
from gui.tkinter_gui import GuiBuilder

"""
Main function for Draw-This app. Initializes the GUI.

Usage
-----
Run this file directly to start the GUI:
    python main.py
"""

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