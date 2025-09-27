import os
import tempfile

import pytest

from drawthis.logic.file_listing import Crawler


@pytest.fixture
def temp_image_dir(tmp_path):
    # Create a fake folder with some "images"
    for i in range(3):
        (tmp_path / f"test_{i}.jpg").write_text("fake image content")
    return tmp_path


def test_crawl_inserts_files_into_db(temp_image_dir):
    # Run crawler
    c = Crawler(str(temp_image_dir))
    c.crawl()

    cur = c.database.cursor()
    cur.execute("SELECT COUNT(*) FROM image_paths")
    row_count = cur.fetchone()[0]

    # database should contain all 3 files
    assert row_count == 3

    # random values should all be in [0,1)
    cur.execute("SELECT randid FROM image_paths")
    values = [row[0] for row in cur.fetchall()]
    assert all(0 <= v < 1 for v in values)

@pytest.mark.integration
def test_crawler_on_real_folder():
    db_fd, db_path = tempfile.mkstemp(suffix=".sqlite")
    folder = "/mnt/Storage/Art/Resources"  # your real folder
    c = Crawler(folder, db_path=db_path)
    c.crawl()

    cur = c.database.cursor()
    cur.execute("SELECT COUNT(*) FROM image_paths")
    assert cur.fetchone()[0] > 0

    cur.execute("SELECT randid FROM image_paths")
    assert all(0 <= row[0] < 1 for row in cur.fetchall())

    cur.execute("SELECT path, folder, randid, mtime FROM image_paths LIMIT 5")
    for row in cur.fetchall():
        print(row)

    cur.execute("SELECT COUNT(*) FROM image_paths")
    total_rows = cur.fetchone()[0]
    print("Total rows in DB:", total_rows)



    # cleanup
    c.database.close()
    os.close(db_fd)
    os.remove(db_path)