import moderngl
import moderngl_window as mglw
import numpy as np
from PIL.Image import Transpose
from pyglet import image

import drawthis.utils.shader_parser
from drawthis.utils.shader_parser import parse_shader
from PIL import Image

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
        vertices = np.array([
            # x, y, u, v
            -1.0, -1.0, 0.0, 0.0,
            1.0, -1.0, 1.0, 0.0,
            -1.0, 1.0, 0.0, 1.0,
            1.0, 1.0, 1.0, 1.0,
        ], dtype='f4')
        vbo = self.ctx.buffer(vertices.tobytes())
        indices = np.array([0, 1, 2, 2, 1, 3], dtype='i4')
        ibo = self.ctx.buffer(indices.tobytes())
        self.vao = self.ctx.vertex_array(self.prog,[( vbo,'2f 2f', "in_vert", "in_uv")],ibo)
        image = Image.open(fp="/home/study/Desktop/img1.png",mode="r").transpose(method=Transpose.FLIP_TOP_BOTTOM).convert("RGBA")
        self.texture = self.ctx.texture(image.size, 4, data= image.tobytes())
        self.texture.use(location=0)
        self.prog['tex'].value = 0

    def on_render(self, time: float, frametime: float):
        # This method is called every frame
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        self.vao.render()


