import sqlite3 as sql
import os, random, queue
# import databases as db
# import aiosqlite as aio


"""
SQLite file lister for Draw-This.

This module defines the file crawler and file loader that interact with a permanent .db file
in ~/.config/.
It has two main classes:

- Crawler:
    Iteratively crawls through folders logic files in Breadth-first order allowing
    for sorting by (randid: random float, mtime: modification time, Built in SQL sorting).

- Loader:
    Returns file paths listed in the SQL database as either a bulk list or in batches
    of a given size.

Usage
-----
This file is imported as a package according to the following:
    import logic.file_listing
"""

class Crawler:
    """Goes through all directories in a queue, adding directories to the queue and
    files to a SQLite database.

        Attributes:
            :ivar database: Connection to the SQLite database
            :ivar loading_block: List of paths buffered waiting to be dumped into DB
            :ivar dir_queue: Queue of directories to scan in FIFO order
        """

    def __init__ (self, db_path= ":memory:"):
        self.database = sql.connect(db_path)
        self.loading_block = []
        self.dir_queue = queue.Queue()
        self._setup_db()

    def crawl(self, root_dir):
        """Goes through all directories in a queue, adding directories to the queue and
    files to the internal loading_block, to be inserted into the database once block is
    large enough to minimize disk I/O.

                Args:
                """

        self.dir_queue.put(root_dir)
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
                        self._commit()
                        file_count = 0
            except (PermissionError, FileNotFoundError, NotADirectoryError) as e:
                print(f"Skipped {current_dir}: {e}")
        self._commit()

    def clear_db(self):
        cursor = self.database.cursor()
        cursor.execute("""
        DROP TABLE IF EXISTS image_paths    
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS image_paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE NOT NULL,
            folder TEXT,
            randid REAL,
            mtime REAL
            )        
        """)

    def _setup_db(self):
        """Creates the database to be used to hold the scanned image paths.

                Args:
                """
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



    def _commit(self):
        """Inserts all paths in the loading_block into the database, generating
        a randid random float for each entry.

                Args:
                """
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

class Loader:
    """Reads all paths in a SQLite database, filtering and sorting them accordingly.

        Attributes:
            :ivar database: Connection to the SQLite database
        """

    def __init__(self, db_path= ":memory:"):
        self.database = sql.connect(db_path)

    def total_db_loader(self):
        """Reads and returns ALL paths in the database in bulk.
                """
        cur = self.database.cursor()
        cur.execute("""
        SELECT  path, folder, randid, mtime
        FROM image_paths
        ORDER BY randid
        """)
        return [row[0] for row in cur.fetchall()]

    # TODO

    def block_loader(self):
        """Reads and returns paths in the database in blocks of size = N.
                """
        pass

    def filter(self):
        """Filters entries in database when reading, by extension.
                """
        pass
