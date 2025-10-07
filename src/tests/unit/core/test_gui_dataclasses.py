import unittest

from drawthis.core.models.state import FolderSet, TimerSet, Session


class TestTimerSet(unittest.TestCase):
    def test_factory(self):
        ts = TimerSet.from_list([20, 5, 35, 0])
        self.assertEqual([0, 5, 20, 35], ts.all)

    def test_add_sort_and_no_duplicates(self):
        ts = TimerSet()
        ts.add(30)
        ts.add(10)
        ts.add(30)  # insert duplicate
        # assert duplicate not added
        self.assertEqual([10, 30], ts.all)

    def test_remove(self):
        ts = TimerSet.from_list([5, 10])
        ts.remove(5)
        # assert correct value removed
        self.assertEqual([10], ts.all)
        # assert correct exception raised on invalid value removal
        with self.assertRaises(ValueError):
            ts.remove(99)

    def test_copy(self):
        ts = TimerSet.from_list([1, 2])
        cp = ts.copy()
        # assert if copy is functional
        self.assertEqual(ts, cp)
        cp.add(3)
        # assert independent instances
        self.assertNotIn(3, ts.all)


class TestFolderSet(unittest.TestCase):
    def test_factory(self):
        folder_dict = {"a": True, "b": False}
        fs_dict = FolderSet.from_pairs(list(folder_dict.items()))
        fs_tuple = FolderSet.from_pairs([("a", True), ("b", False)])
        self.assertEqual(fs_tuple, fs_dict)
        self.assertCountEqual(["a"], fs_tuple.enabled)
        self.assertCountEqual(["b"], fs_tuple.disabled)
        self.assertEqual({"a": True, "b": False}, fs_tuple.all)

    def test_toggle_unknown(self):
        fs = FolderSet.from_pairs([("a", True)])
        fs.toggle("b")  # should be a no‑op
        self.assertCountEqual(fs.enabled, ["a"])

    def test_enable_disable(self):
        fs = FolderSet()
        fs.enable("x")
        self.assertIn("x", fs.enabled)
        fs.disable("x")
        self.assertIn("x", fs.disabled)

    def test_all_returns_copy(self):
        fs = FolderSet.from_pairs([("a", True)])
        d = fs.all
        d["b"] = False
        self.assertNotIn("b", fs.all)

    def test_copy(self):
        fs = FolderSet.from_pairs([("a", True)])
        cp = fs.copy()
        cp.disable("a")
        self.assertIn("a", fs.enabled)


class TestSession(unittest.TestCase):
    def test_round_trip(self):
        data = {
            "timers": [5, 15],
            "folders": {"x": True, "y": False},
            "selected_timer": 5,
        }
        sess = Session.from_dict(data)
        self.assertEqual(data, sess.to_dict())
        self.assertEqual(data["timers"], sess.to_dict()["timers"])
        self.assertEqual(data["folders"], sess.to_dict()["folders"])

    def test_copy_is_deep(self):
        sess = Session()
        sess.timers.add(10)
        copy = sess.copy()
        copy.timers.add(20)
        self.assertNotIn(20, sess.timers.all)


if __name__ == "__main__":
    unittest.main()
