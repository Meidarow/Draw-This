import tkinter as tk

"""
Tkinter GUI for Draw-This.

This module defines the GUI and its builder's methods.
It has one class:

- GuiBuilder:
    Constructs Tkinter widgets, binds them to interface state, and 
    handles user interaction (folder selection, timer selection, console output).

Usage
-----
Run this file directly to start the GUI:
    python tkinter_gui.py
"""


class View:
    """Build and maintains the GUI and sends state to interface module.

        Attributes:
            :ivar _folder_widgets (dict(dict)): Current folder widgets displayed.
            :ivar _timer_widgets (dict(dict)): Current timer widgets displayed.
            :ivar interface (TkinterInterface): Interface object for GUI-Backend communication.
            :ivar root (tk.Tk): root tkinter window.
        """

    def __init__(self, controller):
        self._controller = controller

        self._folder_widgets = {}
        self._timer_widgets = {}

        self.root = tk.Tk()
        self.delay_var = tk.IntVar(value=self._controller.last_timer)
        self.delay_var.trace_add(
            mode="write",
            callback=self.on_timer_change
        )
        self._build_window()

    def build_gui(self):
        self._build_folder_section()
        self._build_buttons_section()
        self._build_timer_section()

    def add_folder_gui(self, folder: str, enabled: tk.BooleanVar) -> None:
        """Adds a single folder, with its path received via user file dialog to the
        internal attribute and to the GUI.
                """

        var = enabled
        def on_folder_change(*args):
            self._controller.sync_folder(folder, var.get())

        var.trace_add(
            mode="write",
            callback= on_folder_change
        )
        self._build_widget(
            key=folder,
            parent_frame=self.folder_frame,
            main_widget_class=tk.Checkbutton,
            main_widget_args={"text": folder, "variable": var},
            widget_type="folder"
        )


    def refresh_timer_gui(self, timers: list[int]) -> None:
        """Adds a single timer, with duration received via user interaction to the
        internal attribute and to the GUI.

                Args:
                    :param timers: List of integer values of timers in viewmodel.
                """
        clear_gui_widgets(self._timer_widgets)

        for timer in timers:
            self._build_widget(
                key=timer,
                parent_frame=self.timer_frame,
                main_widget_class=tk.Radiobutton,
                main_widget_args={"text": f"{timer} seconds", "variable": self.delay_var, "value": timer},
                widget_type="timer"
            )
    def on_timer_change(self,*args):
        self._controller.sync_selected_timer()


    # Private helpers:

    def _build_window(self) -> None:
        """Assembles all base components of the main widget for the GUI.
                """

        self.root.title("Draw-This")
        self.root.geometry("1000x600")




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

    def _build_folder_section(self) -> None:
        """Assembles all components of the main window's vertical folder list section.
                """

        header_row = tk.Frame(self.folder_frame)
        header_row.pack(anchor="center", fill="x")
        folders_label = tk.Label(header_row, text="Select folders:")
        folders_label.pack(side="left")
        add_button = tk.Button(header_row, text="Add folder", command=self._controller.add_folder)
        add_button.pack(side="right")

        for (folder, enabled) in self._controller.tk_folders:
            self.add_folder_gui(folder, enabled)

    def _build_timer_section(self) -> None:
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
        add_button_timer = tk.Button(custom_timer_frame, text="Add", command=lambda: self._controller.add_timer(custom_entry))
        add_button_timer.pack(side="left")

        for timer in self._controller.tk_timers:
            self._build_widget(
                key=timer,
                parent_frame=self.timer_frame,
                main_widget_class=tk.Radiobutton,
                main_widget_args={"text": f"{timer} seconds", "variable": self.delay_var, "value": timer},
                widget_type="timer"
            )

        timer_inf = tk.Radiobutton(self.timer_frame, text="indefinite", variable=self.delay_var, value=0)
        timer_inf.pack(side="right")

    def _build_buttons_section(self) -> None:
        """Assembles all components of the main window's "start" and "add folder" buttons.
                """

        start_button = tk.Button(self.main_frame, text="Start", command=self._controller.start_slideshow)
        start_button.grid(row=1, column=1, sticky="nswe", padx=5)

    def _build_widget(self, key, parent_frame, main_widget_class, main_widget_args=None, widget_type=None):
        """Generic GUI builder for a single row widget with delete button.
                """
        if main_widget_args is None:
            main_widget_args = {}

        if widget_type is None:
            widget_dict = {}
        else:
            widget_dict = {
                "folder": self._folder_widgets,
                "timer": self._timer_widgets
            }[widget_type]

        row = tk.Frame(parent_frame)
        row.pack(fill="x", anchor="w", pady=1)

        main_widget = main_widget_class(row, **main_widget_args)
        main_widget.pack(side="left")

        del_btn = tk.Button(row, text="X", command=lambda k=key: self._controller.delete_widget(widget_type, k))
        del_btn.pack(side="left" if main_widget_class == tk.Radiobutton else "right")

        widget_dict[key] = {"main": main_widget, "delete_button": del_btn, "row": row}

    def delete_widget(self, widget_type: str, widget_value: str | int) -> None:
        """Removes all components of a single widget from the GUI AND updates
        internal attributes to reflect that.

                Args:
                    :param widget_type: Widget dict from which to remove widget
                    :param widget_value: [UNIQUE] Value of widget to be removed
                """
        widget_dicts = {
            "folder": self._folder_widgets,
            "timer": self._timer_widgets
        }
        widget = widget_dicts[widget_type].pop(widget_value)
        for component in widget.values():
            component.destroy()
    
def clear_gui_widgets(widget_dict):
    """Removes all components of a single widget from the GUI ONLY.
            """

    for widget in widget_dict.values():
        for w in widget.values():
            if hasattr(w, "destroy"):
                w.destroy()
    widget_dict.clear()


