import itertools
from pathlib import Path

from PIL import Image
from moderngl_window.context.base import KeyModifiers

from drawthis.render.opengl_backend import RenderWindow


def make_dummy_image(color, size=(64, 64)):
    """Return a Pillow image filled with a solid RGBA color."""
    img = Image.new("RGBA", size, color)
    return img


def test_texture_loading(monkeypatch):
    """Integration test: load multiple textures onto the quad."""

    class TestWindow1(RenderWindow):
        window_size = (256, 256)  # small test window

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            # Replace texture with dummy ones for testing
            self.textures = [
                self.ctx.texture(img.size, 4, img.tobytes())
                for img in [
                    make_dummy_image((255, 0, 0, 255)),  # red
                    make_dummy_image((0, 255, 0, 255)),  # green
                    make_dummy_image((0, 0, 255, 255)),  # blue
                ]
            ]
            self.current = 0

        def on_render(self, time, frametime):
            # Cycle through textures
            tex = self.textures[self.current % len(self.textures)]
            tex.use(location=0)
            self.vao.render()
            self.current += 1

    # This will open a window & run the loop — not great for CI
    # but good for local smoke testing


class TestWindow2(RenderWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Preload some test images
        self.images = itertools.cycle(
            [
                Path("/home/study/Desktop/img1.png"),
                Path("/home/study/Desktop/img2.webp"),
                Path("/home/study/Desktop/img3.webp"),
            ]
        )
        self.set_texture(next(self.images))

    def on_key_event(self, key, action, modifiers: KeyModifiers):
        """Cycle textures with SPACEBAR."""
        if key == self.wnd.keys.SPACE and action == self.wnd.keys.ACTION_PRESS:
            self.set_texture(next(self.images))


if __name__ == "__main__":  # run() exits the app loop
    TestWindow2.run()
