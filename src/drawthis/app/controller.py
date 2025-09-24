from moderngl_window.context.base import KeyModifiers
from drawthis.logic.file_listing import Loader
from drawthis.logic.file_listing import Crawler
from pathlib import Path
import itertools
from drawthis.render.opengl_backend import RenderWindow


class TestWindow2(RenderWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Preload some test images
        self.images = itertools.cycle([Path(p) for p in Loader(Path("~/.config/draw-this/image_paths.db").expanduser()).total_db_loader()])
        self.set_texture(next(self.images))

    def on_key_event(self, key, action, modifiers: KeyModifiers):
        """Cycle textures with SPACEBAR."""
        if key == self.wnd.keys.SPACE and action == self.wnd.keys.ACTION_PRESS:
            self.set_texture(next(self.images))

def start_slideshow_ogl(recalculate, folders, timer=None, db_path=None):

    if recalculate:
        for folder in folders:
            crawler = Crawler(folder, Path("~/.config/draw-this/image_paths.db").expanduser())
            crawler.crawl()
    TestWindow2.run()
