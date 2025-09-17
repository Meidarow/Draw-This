import subprocess, tempfile
from listing.file_listing import Crawler, Loader


def start_slideshow(folders: list, geometry=None, drawing_time=0, db_path=":memory:"):

    if isinstance(folders, str):
        folders = [folders]

    if not folders:
        print("No folder(s) selected")
        return

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
