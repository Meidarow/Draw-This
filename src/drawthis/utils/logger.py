import pathlib as path
import sys

"""
Simple logging utility meant to be replaced by the built-in python logger. [SOON TO BE DEPRECATED]

This module defines the logger and it's functionality.
It has one class:

- Logger:
    Takes stdout and stderr and redirects them to a file.

Usage
-----
This file is imported by Viewmodel as a package according to the following:
    from drawthis import Logger
"""

LOG_FOLDER = path.Path("/tmp/draw_this.log")


class Logger:

    def __init__(self):
        self.log_file = None

    def start_log(self) -> None:
        self.log_file = open(LOG_FOLDER, "w")
        sys.stdout = self.log_file
        sys.stderr = self.log_file

    def end_log(self) -> None:
        self.log_file.close()