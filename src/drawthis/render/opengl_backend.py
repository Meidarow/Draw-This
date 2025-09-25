import moderngl_window as mglw
from PIL import Image
import numpy as np
from PIL.Image import Transpose
from drawthis.utils.shader_parser import parse_shader
from moderngl_window.context.base import KeyModifiers
from drawthis.logic.file_listing import Crawler, Loader
from pathlib import Path
from collections import deque

"""
OpenGL Backend for Draw-This.

This module defines the function that serves as an interface between the GUI and FEH:
It has a single function:

- start_slideshow:
    Accepts a series of parameters and builds a bash command calling feh with a series
    of flags, according to user preferences.

Usage
-----
This file is imported as a package according to the following:
    import render.feh_backend
"""

class RenderWindow(mglw.WindowConfig):
    gl_version = (3, 3)
    window_size = (1920, 1080)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Do initialization here
        self.prog = self.ctx.program(vertex_shader=parse_shader("basic.vert"),fragment_shader=parse_shader("basic.frag"))
        indices = np.array([0, 1, 2, 2, 1, 3], dtype='i4')
        ibo = self.ctx.buffer(indices.tobytes())
        vertices = np.array([
            # x, y, u, v
            -1.0, -1.0, 0.0, 0.0,
            1.0, -1.0, 1.0, 0.0,
            -1.0, 1.0, 0.0, 1.0,
            1.0, 1.0, 1.0, 1.0,
        ], dtype='f4')
        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.vertex_array(self.prog,[(self.vbo,'2f 2f', "in_vert", "in_uv")],ibo)
        self.texture = self.ctx.texture
        self.images = deque([Path(p) for p in Loader(Path("~/.config/draw-this/image_paths.db").expanduser()).total_db_loader()])
        self.set_texture(self.images[0])

    def on_key_event(self, key, action, modifiers: KeyModifiers):
        """Cycle textures with SPACEBAR."""
        if key == self.wnd.keys.RIGHT and action == self.wnd.keys.ACTION_PRESS:
            self.images.rotate(1)
            self.set_texture(self.images[0])

        if key == self.wnd.keys.LEFT and action == self.wnd.keys.ACTION_PRESS:
            self.images.rotate(-1)
            self.set_texture(self.images[0])

    def on_render(self, time: float, frametime: float):
        # This method is called every frame
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        self.vao.render()

    def on_close(self):
        # This method closes the window
        self.wnd.close()

    def set_texture(self, path):
        image = Image.open(fp=path, mode="r").transpose(
            method=Transpose.FLIP_TOP_BOTTOM).convert("RGBA")
        self._scale_vbo(image.width/image.height, self.wnd.width/self.wnd.height)
        self.texture = self.ctx.texture(image.size, 4, data=image.tobytes())
        self.texture.use(location=0)
        self.prog['tex'].value = 0

    def _scale_vbo(self,image_ar,window_ar):
        if image_ar > window_ar :
            h_scale = 1.0
            v_scale = window_ar / image_ar
        else :
            v_scale = 1.0
            h_scale = image_ar / window_ar
        vertices = np.array([
            # x, y, u, v
            -1.0*h_scale, -1.0*v_scale, 0.0, 0.0,
            1.0*h_scale, -1.0*v_scale, 1.0, 0.0,
            -1.0*h_scale, 1.0*v_scale, 0.0, 1.0,
            1.0*h_scale, 1.0*v_scale, 1.0, 1.0,
        ], dtype='f4')
        self.vbo.write(vertices.tobytes())

def start_slideshow_ogl(recalculate, folders, selected_timer=None, db_path=None):

    if recalculate:
        crawler = Crawler(db_path)
        crawler.clear_db()
        for folder in folders:
            crawler.crawl(folder)

    RenderWindow.run()

