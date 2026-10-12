import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from spt_go import config


class ConfigTests(unittest.TestCase):
    def test_default_current_and_potential_share_origin(self):
        cfg = config.Settings()
        geometry = config.preview_geometry(cfg)
        self.assertAlmostEqual(math.hypot(*geometry["current"]), cfg.distance)
        self.assertEqual(geometry["routes"][0]["points"][0][:2], (0, 0))

    def test_on_ignores_potential_list(self):
        cfg = config.Settings(same_direction=True, potential_points="no válido")
        self.assertEqual(cfg.directions(), [(cfg.current_e, cfg.current_n)])

    def test_off_multiple_directions_and_fan(self):
        cfg = config.Settings(potential_points="552878.84, 9423290.72; 548000, 9424000;", potential_rays=2)
        cfg.validate()
        self.assertEqual(len(cfg.directions()), 2)
        self.assertEqual(len(config.preview_geometry(cfg)["routes"]), 10)
        self.assertEqual(cfg.point_count, 1 + 10 * len(cfg.potential_percentages))

    def test_percentages_and_reference_radius(self):
        cfg = config.Settings(percentages="100; 61.8; 0; 80")
        self.assertEqual(cfg.percentages_list, [0, 61.8, 80, 100])
        self.assertEqual(cfg.final_percent, 80)
        self.assertAlmostEqual(math.hypot(*config.preview_geometry(cfg)["routes"][0]["end"]), cfg.distance * .8)

    def test_distance_and_direction(self):
        self.assertEqual(config.unit_direction((0, 0), (3, 4)), (.6, .8))
        with self.assertRaises(ValueError):
            config.unit_direction((1, 1), (1, 1))

    def test_zone_hemisphere_and_invalid_values(self):
        config.Settings(zone=1, hemisphere="north").validate()
        for cfg in (config.Settings(zone=0), config.Settings(zone=61), config.Settings(hemisphere="east")):
            with self.assertRaises(ValueError):
                cfg.validate()

    def test_legacy_project_and_unknown_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "anterior.json"
            path.write_text(json.dumps({"schema": "spat-ssee", "version": 1, "settings": {"project": "LEGADO", "zone": 17, "future_field": 1}}), encoding="utf-8")
            self.assertEqual(config.load_settings(path).project, "LEGADO")
            config.save_settings(path, config.Settings())
            self.assertEqual(config.load_settings(path).project, "SPT_EJEMPLO")

    def test_invalid_json_schema(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            path.write_text('{"schema":"other","version":1,"settings":{}}', encoding="utf-8")
            with self.assertRaises(ValueError):
                config.load_settings(path)

    def test_read_only_portable_fallback(self):
        with tempfile.TemporaryDirectory() as temp:
            exe_dir = Path(temp) / "exe"
            fallback = Path(temp) / "local"
            with patch.object(config, "portable_dir", return_value=exe_dir), patch.dict(config.os.environ, {"LOCALAPPDATA": str(fallback)}), patch.object(config, "writable_dir", side_effect=lambda path: path != exe_dir):
                self.assertEqual(config.user_data_dir(), fallback / "SPT Go Portable")
                self.assertEqual(config.default_output_dir(), fallback / "SPT Go Portable" / "Resultados")

    def test_assets_are_in_package(self):
        assets = Path(config.__file__).resolve().parent / "assets"
        self.assertTrue((assets / "logo.png").is_file())
        self.assertTrue((assets / "app.ico").is_file())


if __name__ == "__main__":
    unittest.main()
