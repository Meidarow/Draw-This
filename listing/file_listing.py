import sqlite3 as sql
import os, random, queue
# import databases as db
# import aiosqlite as aio

class Crawler:
    def __init__ (self, root_dir):
        self.database = sql.connect("/home/study/.config/draw-this/image_paths.db")
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
        rows = []
        for fpath in self.loading_block:
            folder = fpath
            randid = random.Random()
            rows.append((folder, randid))
        self.database.cursor().executemany("INSERT OR IGNORE INTO image_paths(path, folder, randid, mtime) VALUES (?, ?, ?, ?)",rows)

    def crawl(self):
        file_count = 0
        try:
            for dir_entry in os.scandir(self.dir_queue.get()):
                if dir_entry.is_dir():
                    self.dir_queue.put(dir_entry.path)
                    continue
                self.loading_block.append(dir_entry.path)
                file_count += 1
                if file_count == 500 :
                    self.commit()
                    file_count = 0
            self.commit()
        except (PermissionError, FileNotFoundError, NotADirectoryError):
            pass



    def filter(self):
        pass

class Loader:
    def __init__(self):
        database = sql.connect("/home/study/.config/draw-this/image_paths.db")

