from drawthis.gui.tkinter_viewmodel import Viewmodel

"""
Bootstapper for Iteradraw app. 

Builds the application.

Usage
-----
Run this file directly to start the app:
    python bootstrap.py
"""


def main() -> None:
    app = Viewmodel()
    app.run()


if __name__ == "__main__":
    main()
