import tempfile
import unittest
from pathlib import Path

from spt_go.config import Settings
from spt_go.selftest import validate_exports
from spt_go.service import generate


class ExportTests(unittest.TestCase):
    def test_real_projection_and_exports(self):
        with tempfile.TemporaryDirectory() as temp:
            cfg = Settings(output_dir=temp, potential_points="552878.84, 9423290.72; 548000, 9424000;", potential_rays=1)
            first = generate(cfg)
            validate_exports(cfg, first)
            second = generate(cfg)
            self.assertNotEqual(first["folder"], second["folder"])
            self.assertEqual(len(list(Path(temp).glob("SPT_EJEMPLO_*"))), 2)

    def test_unwritable_explicit_output_has_clear_error(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "not_a_directory"
            file.write_text("x")
            cfg = Settings(output_dir=str(file))
            with self.assertRaisesRegex(OSError, "No se puede crear la carpeta de resultados"):
                generate(cfg)


if __name__ == "__main__":
    unittest.main()
