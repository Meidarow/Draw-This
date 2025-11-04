import os
import subprocess
import tempfile

from drawthis.core.constants import DATABASE_FILE

from drawthis.services.resources.file_discovery_service import DatabaseManager

"""
FEH Backend for Draw-This.

This module defines the interface between the GUI and FEH:
It has a single function:

- start_slideshow:
Accepts a series of parameters and builds a bash command calling feh
with a series of flags, according to user preferences. Must use the whole
DB since feh cannot load paths incrementally.

Usage
-----
This file is imported as a package according to the following:
    import render.feh_backend
"""


def start_slideshow_feh(
    geometry: tuple[int, int, int, int] = (960, 1080, 960, 0),
    selected_timer: int = 0,
    **kwargs,
) -> None:
    """Build call to FEH to display a slideshow of all images in DB.
    *Must use total_db_loader, feh cannot load paths incrementally.

            Args:
                :param geometry: String specifying windowed/fullscreen modes
                :param selected_timer: Duration of each slide in seconds
    """
    # Populates a temp file with all paths to pass into the subprocess call
    paths = DatabaseManager(DATABASE_FILE).load_all_rows()
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("\n".join(paths))
        filelist_path = f.name

    cmd = ["feh", "-rZ.", "-B", "black"]

    if selected_timer != 0:
        cmd += ["-D", str(selected_timer)]

    cmd += ["--filelist", filelist_path]

    width, height, hor_offset, vert_offset = geometry
    cmd += ["--geometry", f"{width}x{height}+{hor_offset}+{vert_offset}"]

    print("Executed Command:", " ".join(cmd))

    try:
        subprocess.run(cmd)
    finally:
        # Remove tempfile once slideshow ends
        os.remove(filelist_path)
