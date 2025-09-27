import pathlib as path
import sys

LOG_FOLDER = path.Path("/tmp/draw_this.log")


class Logger:

    def __init__(self):
        self.log_file = None

    def start_log(self):
        self.log_file = open(LOG_FOLDER, "w")
        sys.stdout = self.log_file
        sys.stderr = self.log_file

    def end_log(self):
        self.log_file.close()