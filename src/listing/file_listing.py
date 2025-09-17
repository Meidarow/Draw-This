import sqlite3 as sql
import os, random, queue
# import databases as db
# import aiosqlite as aio

class Crawler:
    def __init__ (self, root_dir, db_path= ":memory:"):
        self.database = sql.connect(db_path)
        self.loading_block = []
        self.dir_queue = queue.Queue()
        self.dir_queue.put(root_dir)
        self._setup_db()

    def _setup_db(self):
        cursor = self.database.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS image_paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE NOT NULL,
            folder TEXT,
            randid REAL,
            mtime REAL
            )        
        """)

    def commit(self):
        if not self.loading_block:
            return
        rows = []
        for fpath in self.loading_block:
            folder = os.path.dirname(fpath)
            randid = random.random()
            mtime = os.stat(fpath).st_mtime
            rows.append((fpath,folder, randid,mtime))
        self.database.cursor().executemany("INSERT OR IGNORE INTO image_paths(path, folder, randid, mtime) VALUES (?, ?, ?, ?)",rows)
        self.database.commit()
        self.loading_block.clear()

    def crawl(self):
        file_count = 0
        while not self.dir_queue.empty():
            current_dir = self.dir_queue.get()
            try:
                for dir_entry in os.scandir(current_dir):
                    if dir_entry.is_dir():
                        self.dir_queue.put(dir_entry.path)
                        continue
                    self.loading_block.append(dir_entry.path)
                    file_count += 1
                    if file_count == 1500 :
                        self.commit()
                        file_count = 0
            except (PermissionError, FileNotFoundError, NotADirectoryError) as e:
                print(f"Skipped {dir_entry.path}: {e}")
        self.commit()



    def filter(self):
        pass

class Loader:
    def __init__(self):
        self.database = sql.connect("/home/study/.config/draw-this/image_paths.db")

