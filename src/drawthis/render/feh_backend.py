import subprocess, tempfile
from drawthis.logic.file_listing import Crawler, Loader


"""
FEH Backend for Draw-This.

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

def start_slideshow(folders: list, geometry=None, drawing_time=0, db_path=":memory:", recalculate= True):
    """Assembles a bash command calling FEH to display a slideshow of images from a file containing all paths,
    allows setting of slideshow delay and duration.

            Args:
                :param folders: List of paths to root directories from which to display images
                :param recalculate: Boolean specifying whether to re-crawl folders or just load DB
                :param db_path: Path to DB on current OS/platform
                :param drawing_time: Duration of each slide in seconds
                :param geometry: String specifying windowed/fullscreen modes
            """

    if isinstance(folders, str):
        folders = [folders]

    if not folders:
        print("No folder(s) selected")
        return

    if recalculate:
        for folder in folders:
            crawler = Crawler(folder, db_path)
            crawler.crawl()

    paths = Loader(db_path).total_db_loader()
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("\n".join(paths))
        filelist_path = f.name

    cmd = ["feh", "-rZ.", "-B", "black"]

    if drawing_time != 0:
        cmd += ["-D", str(drawing_time)]

    cmd += ["--filelist", filelist_path]

    if geometry is None:
        cmd += ["--geometry", "960x1080+960+0"]

    print("Executed Command:", " ".join(cmd))
    subprocess.run(cmd)
