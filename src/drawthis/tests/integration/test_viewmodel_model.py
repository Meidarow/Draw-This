import tkinter as tk
import unittest
from unittest import mock

from drawthis.gui.state import Session
from drawthis.gui.viewmodel import Viewmodel


class MockView:
    def __init__(self, selected_timer: int = None):
        self.folder_widgets: dict[str, dict[str, tk.Widget]] = {}
        self.timer_widgets: dict[str, dict[int, tk.Widget]] = {}
        self.selected_timer_var = None or selected_timer


class ViewmodelModelIntegrationn(unittest.TestCase):
    """
    Verify that invoking ViewModel methods from the view correctly updates
    the underlying Model.

    Steps:
    - Create a mock GUI and instantiate the ViewModel with it.
    - Patch ``drawthis.gui.viewmodel.filedialog.askdirectory`` to return a
      deterministic path and call ``add_folder()``.
    - Add a timer using a mocked Tkinter widget.

    Expected outcomes:
    * The Model’s folder collection contains the path returned by the patched
      dialog and the folder’s enabled status matches the ViewModel’s state.
    * The Model’s timer collection includes the timer value supplied via the
      mocked widget.
    """

    def test_folder_flow(self):
        self.skipTest("Deprecated test - refactor needed")
        mock_gui = MockView()
        vm = Viewmodel(gui=mock_gui)
        file_paths = [f"fake/path/string/{i}" for i in range(3)]

        with mock.patch(
            "drawthis.gui.viewmodel.filedialog.askdirectory",
            side_effect=file_paths,
        ):
            vm.add_folder()
            self.assertEqual(
                {"fake/path/string/0": True},
                vm.model.session.folders.all,
            )
            vm.add_folder()
            self.assertEqual(
                {"fake/path/string/0": True, "fake/path/string/1": True},
                vm.model.session.folders.all,
            )
            vm.sync_folder("fake/path/string/0")
            self.assertEqual(
                {"fake/path/string/0": False, "fake/path/string/1": True},
                vm.model.session.folders.all,
            )

    def test_timer_flow(self):
        self.skipTest("Deprecated test - refactor needed")
        mock_gui = MockView()
        vm = Viewmodel(gui=mock_gui)

        # tests insertion and update
        timer = mock.Mock()
        timer.get.return_value = str(123)
        vm.add_timer(timer)
        self.assertEqual([123], vm.model.session.timers.all)

        # test secondary insertion and sorting
        timer = mock.Mock()
        timer.get.return_value = str(1)
        vm.add_timer(timer)
        self.assertEqual([1, 123], vm.model.session.timers.all)

        from drawthis.utils.logger import logger

        # test invalid addition and exception raise
        invalid_timer = mock.Mock()
        invalid_timer.get.return_value = str(0)
        with self.assertLogs(logger, level="WARNING") as cm:
            vm.add_timer(invalid_timer)
        self.assertIn("0 is an Invalid timer value", cm.output[0])

        # test removal and update
        vm.delete_widget(widget_type="timer", value=123)
        self.assertEqual([1], vm.model.session.timers.all)

    def test_startshow_parameters(self):
        self.skipTest("Deprecated test - refactor needed")
        mock_gui = MockView(selected_timer=123)
        vm = Viewmodel(gui=mock_gui)

        timer = mock.Mock()
        timer.get.return_value = str(123)
        vm.add_timer(timer)

        file_paths = [f"fake/path/string/{i}" for i in range(3)]
        with mock.patch(
            "drawthis.gui.viewmodel.filedialog.askdirectory",
            side_effect=file_paths,
        ):
            vm.add_folder()
            vm.add_folder()
            vm.add_folder()

        session_dict = {
            "folders": {
                "fake/path/string/0": True,
                "fake/path/string/1": True,
                "fake/path/string/2": True,
            },
            "timers": [123],
        }
        session_bench = Session.from_dict(session_dict)
        with mock.patch.object(vm.slideshow, "start") as mock_start_slideshow:
            vm.start_slideshow()

        mock_start_slideshow.assert_called_once_with(session_bench)
