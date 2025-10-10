import random
import sys
import unittest
from typing import NamedTuple
from unittest import mock

from drawthis.core.models.resources.dataclasses import FileEntry, ImageRow
from drawthis.core.protocols.protocols import *

_stat_result: "StatLike"
_is_dir: bool
_is_symlink: bool


class MockDirEntry:
    path: str
    _stat_result: "StatLike"
    _is_dir: bool
    _is_symlink: bool

    def __init__(self, stat_result, is_dir, is_symlink, path):
        self.path = path
        self._is_dir = is_dir
        self._is_symlink = is_symlink
        self._stat_result = stat_result

    def stat(self) -> "StatLike":
        return self._stat_result

    def is_dir(self) -> bool:
        return self._is_dir

    def is_symlink(self) -> bool:
        return self._is_symlink


def make_fake_stat(**overrides):
    """Create a minimal ``os.stat_result``‑like named‑tuple."""
    stat = NamedTuple(
        "StatResult",
        [
            ("st_mode", int),
            ("st_ino", int),
            ("st_dev", int),
            ("st_nlink", int),
            ("st_uid", int),
            ("st_gid", int),
            ("st_size", int),
            ("st_atime", float),
            ("st_mtime", float),
            ("st_ctime", float),
        ],
    )
    defaults = dict(
        st_mode=0o100644,
        st_ino=1,
        st_dev=1,
        st_nlink=1,
        st_uid=1000,
        st_gid=1000,
        st_size=0,
        st_atime=1_600_000_000.0,
        st_mtime=1_600_000_001.0,
        st_ctime=1_600_000_002.0,
    )
    defaults.update(overrides)
    return stat(**defaults)


def deterministic_random(seed: int = 0) -> Callable[[], float]:
    rng = random.Random(seed)
    return rng.random


class TestFileListingDataclasses(unittest.TestCase):
    def test_file_entry_from_dir_entry_like(self):
        stat_result = make_fake_stat()
        path = "generic/fake/path/string/to/file.fake"
        dir_entry_like = MockDirEntry(
            stat_result,
            False,
            False,
            path,
        )
        file_entry = FileEntry.from_dir_entry(dir_entry_like)

        self.assertEqual(False, file_entry.is_dir)
        self.assertEqual(False, file_entry.is_symlink)
        self.assertEqual(path, file_entry.path)
        self.assertEqual(stat_result.st_mtime, file_entry.stat.st_mtime)
        self.assertEqual(stat_result.st_ino, file_entry.stat.st_ino)
        self.assertEqual(stat_result.st_dev, file_entry.stat.st_dev)

    def test_image_row_from_file_entry(self):
        self.skipTest("Deprecated test - refactor needed")
        stat_result = make_fake_stat()
        path = "generic/fake/path/string/to/file.fake"
        dir_entry_like = MockDirEntry(
            stat_result,
            False,
            False,
            path,
        )
        file_entry = FileEntry.from_dir_entry(dir_entry_like)
        with mock.patch(
            "drawthis.logic.protocols.random.random",
            deterministic_random(42),
        ):
            image_row = ImageRow.from_file_entry(file_entry)
            exp_randid = deterministic_random(42)()
        self.assertEqual(file_entry.path, image_row.file_path)
        self.assertEqual(file_entry.stat.st_mtime, image_row.mtime)
        self.assertEqual(exp_randid, image_row.randid)

    def test_return_type_and_fields(self):
        self.skipTest("Deprecated test - refactor needed")
        fake_stat = make_fake_stat(st_mtime=1234567890.0)

        def fake_stat_fn(*args):
            return fake_stat

        with mock.patch(
            "drawthis.logic.file_listing.random.random",
            deterministic_random(42),
        ):
            row = build_row_from(
                file_path="some/file.jpg", stat_fn=fake_stat_fn
            )

        self.assertEqual(set(ImageRow._fields), set(row._fields))
        self.assertIsInstance(row, ImageRow)

        expected_randid = deterministic_random(42)()
        self.assertAlmostEqual(row.randid, expected_randid)

    # ------------------------------------------------------------------
    # 2️⃣  Path handling – a matrix of interesting path shapes
    # ------------------------------------------------------------------
    @staticmethod
    def path_cases():
        """Yield (input_path, expected_folder)."""
        cases = [
            ("foo.jpg", ""),
            ("dir/subdir/image.png", "dir/subdir"),
            ("/abs/path/to/file.tiff", "/abs/path/to"),
            ("unicode/файл.jpeg", "unicode"),
            ("trailing/slash/", "trailing/slash"),
        ]
        # Windows‑style path – only relevant when the test runs on Windows.
        # On POSIX platforms the back‑slashes are just characters, so the
        # expected folder is '' (empty string).
        if sys.platform.startswith("win"):
            cases.append(("C:\\Windows\\Path\\file.bmp", "C:\\Windows\\Path"))
        else:
            cases.append(("C:\\Windows\\Path\\file.bmp", ""))
        return cases

    def test_path_derivation(self):
        self.skipTest("Deprecated test - refactor needed")
        fake_stat = make_fake_stat()

        def fake_stat_fn(*args):
            return fake_stat

        for inp, exp_folder in self.path_cases():
            with self.subTest(path=inp):
                row = build_row_from(file_path=inp, stat_fn=fake_stat_fn)

                self.assertEqual(row.file_path, inp)
                self.assertEqual(row.folder, os.path.dirname(inp))
                self.assertEqual(row.folder, exp_folder)

    # ------------------------------------------------------------------
    # 3️⃣  Stat handling – verify that ``mtime`` comes from the stat result
    # ------------------------------------------------------------------
    def test_mtime_propagated(self):
        self.skipTest("Deprecated test - refactor needed")
        fake_stat = make_fake_stat(st_mtime=1_234_567_890.0)

        def fake_stat_fn(*args):
            return fake_stat

        row = build_row_from(file_path="any.jpg", stat_fn=fake_stat_fn)

        self.assertEqual(row.mtime, fake_stat.st_mtime)

    # ------------------------------------------------------------------
    # 4️⃣  Default behaviour – when ``stat_fn`` is omitted
    # ------------------------------------------------------------------
    def test_default_uses_os_stat(self):
        self.skipTest("Deprecated test - refactor needed")
        """If no ``stat_fn`` is supplied the function must call ``os.stat``."""
        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            tmp.write(b"hello world")
            tmp.flush()

            # Patch the *os.stat* that build_row imported at definition time.
            # The default argument is already bound, so we verify the returned
            # value comes from the mock rather than asserting a call count.
            with mock.patch(
                "drawthis.logic.file_listing.os.stat"
            ) as mock_stat:
                mock_stat.return_value = make_fake_stat(st_mtime=42.0)

                row = build_row_from(file_path=tmp.name)  # no stat_fn argument

                self.assertEqual(row.mtime, 42.0)

    # ------------------------------------------------------------------
    # 5️⃣  Random‑id edge cases – type and range
    # ------------------------------------------------------------------
    def test_randid_is_float_between_0_and_1(self):
        self.skipTest("Deprecated test - refactor needed")
        fake_stat = make_fake_stat()

        def fake_stat_fn(*args):
            return fake_stat

        for _ in range(20):
            row = build_row_from(file_path="x.jpg", stat_fn=fake_stat_fn)
            self.assertIsInstance(row.randid, float)
            self.assertGreaterEqual(row.randid, 0.0)
            self.assertLess(row.randid, 1.0)

    # ------------------------------------------------------------------
    # 6️⃣  Error handling – invalid ``stat_fn`` or missing ``st_mtime``
    # ------------------------------------------------------------------
    def test_invalid_stat_fn_raises(self):
        self.skipTest("Deprecated test - refactor needed")
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            build_row_from(file_path="a.jpg", stat_fn="not a function")

    def test_missing_mtime_attribute(self):
        self.skipTest("Deprecated test - refactor needed")

        class IncompleteStat:
            pass

        with self.assertRaises(AttributeError):
            build_row_from(
                file_path="b.jpg", stat_fn=lambda _: IncompleteStat()
            )

    # ------------------------------------------------------------------
    # 7️⃣  No side‑effects – ensure the function does not touch the filesystem
    # ------------------------------------------------------------------
    def test_no_file_io_when_custom_stat_fn_used(self):
        self.skipTest("Deprecated test - refactor needed")
        fake_stat = make_fake_stat(st_mtime=99.0)
        fake_stat_fn = mock.Mock(return_value=fake_stat)

        with mock.patch("drawthis.logic.file_listing.os.stat") as mock_os_stat:
            row = build_row_from(file_path="dummy.jpg", stat_fn=fake_stat_fn)

            mock_os_stat.assert_not_called()
            fake_stat_fn.assert_called_once_with("dummy.jpg")
            self.assertEqual(row.mtime, 99.0)

    # ------------------------------------------------------------------
    # 8️⃣  Type‑checking sanity – ensure mypy sees the correct signatures
    # ------------------------------------------------------------------
    def test_type_hints_exist(self):
        self.skipTest("Deprecated test - refactor needed")
        from inspect import signature

        sig = signature(build_row_from)
        self.assertEqual(sig.parameters["file_path"].annotation, str)
        self.assertTrue(
            sig.parameters["stat_fn"].annotation == Callable
            or sig.parameters["stat_fn"].annotation == Callable[[str], Any]
        )
        self.assertEqual(sig.return_annotation, ImageRow)


if __name__ == "__main__":
    unittest.main()
