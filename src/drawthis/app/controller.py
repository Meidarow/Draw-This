from drawthis.gui.coordinator import Coordinator
from drawthis.render.feh_backend import start_slideshow_feh
from drawthis.render.opengl_backend import start_slideshow_ogl
import pathlib as path
import sys


BACKEND_FUNCTION = start_slideshow_feh
LOG_FOLDER = path.Path("/tmp/draw_this.log")
DATABASE_FOLDER = path.Path("~/.config/draw-this/image_paths.db").expanduser()

class AppController:
    def __init__(self):
        self.gui = Coordinator(self)
        self.start_gui()

    def start_gui(self):
        log_file = open(LOG_FOLDER, "w")
        sys.stdout = log_file
        sys.stderr = log_file

        try:
            self.gui.run()
        finally:
            log_file.close()


    def run_slideshow(self, slideshow_parameters):
        if not slideshow_parameters.get("folders"):
            return
        BACKEND_FUNCTION(db_path=DATABASE_FOLDER, **slideshow_parameters)
