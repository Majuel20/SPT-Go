import sys
import tempfile
import unittest
from pathlib import Path

from spt_go.selftest import run_self_test


@unittest.skipUnless(sys.platform == "win32", "Requiere Windows")
class WindowTests(unittest.TestCase):
    def test_gui_resources_and_controls(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(run_self_test(Path(temp) / "report.json", check_gui=True), 0)


if __name__ == "__main__":
    unittest.main()
