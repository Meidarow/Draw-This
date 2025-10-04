import pathlib as path

"""This module houses all global constants"""

# Frontend constants
START_FOLDER: path.Path = path.Path("/mnt/Storage/Art/Resources")

# File-listing constants
DATABASE_FILE: path.Path = (
    path.Path.home() / ".config" / "draw-this" / "image_paths.db"
)

# Logger constants
LOG_FOLDER = path.Path("/tmp/draw_this.log")
