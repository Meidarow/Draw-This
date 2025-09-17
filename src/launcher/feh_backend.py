import subprocess

def start_slideshow(folders, geometry=None, drawing_time=0):
    if isinstance(folders, str):
        folders = [folders]

    if not folders:
        print("No folder(s) selected")
        return

    cmd = ["feh", "-rzZ.","-B","black"]

    if drawing_time!=0:
        cmd +=["-D", str(drawing_time)]

    cmd +=  folders

    if geometry is None:
        cmd += ["--geometry", "960x1080+960+0"]

    print("Executed Command:", " ".join(cmd))
    subprocess.run(cmd)