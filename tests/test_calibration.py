"""Calibration offsets, the calibration.toml writer and the coupon scaffolds. Run: python -m unittest discover tests"""

import argparse
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from cadlib import fit
from cadstudio import calibrate


class CalibrationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        patcher = mock.patch.dict(os.environ, {"CAD_CALIBRATION_FILE": str(self.tmp / "calibration.toml")})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(fit.set_material, None)
        fit.set_material(None)

    def test_defaults_unchanged_without_calibration(self):
        self.assertAlmostEqual(fit.hole_d(5.0), 5.2)
        self.assertAlmostEqual(fit.clearance(5.0, "slide"), 5.5)
        fit.set_material("PLA")  # no file -> zero offset
        self.assertAlmostEqual(fit.hole_d(5.0), 5.2)
        self.assertAlmostEqual(fit.wall_t(1.2), 1.2)

    def test_offsets_applied_per_material(self):
        path = self.tmp / "calibration.toml"
        calibrate.write_calibration(calibrate.record({}, "PLA", hole=0.15, wall=-0.05, note='say "hi"'), path)
        self.assertEqual(calibrate.load_calibration(path)["PLA"]["note"], 'say "hi"')
        fit.set_material("PLA")
        self.assertAlmostEqual(fit.hole_d(5.0), 5.35)
        self.assertAlmostEqual(fit.clearance(5.0, "snug"), 5.45)
        self.assertAlmostEqual(fit.wall_t(1.2), 1.15)
        fit.set_material("PETG")
        self.assertAlmostEqual(fit.hole_d(5.0), 5.2)

    def test_record_accumulates_and_overwrites(self):
        data = calibrate.record({}, "PLA", hole=0.1)
        data = calibrate.record(data, "PLA", hole=0.05, wall=0.1)
        self.assertEqual(data["PLA"], {"hole_offset": 0.15, "wall_offset": 0.1})
        self.assertEqual(calibrate.record(data, "PLA", hole=0.0, absolute=True)["PLA"]["hole_offset"], 0.0)

    def test_coupon_scaffold(self):
        with mock.patch.object(calibrate, "MODELS_DIR", self.tmp), mock.patch.object(calibrate, "_rel", str):
            args = argparse.Namespace(name="thing", feature="M3 nut trap", category="misc")
            self.assertEqual(calibrate.cmd_coupon(args), 0)
            text = (self.tmp / "misc" / "thing-fit-gauge" / "model.py").read_text()
            self.assertIn("M3 nut trap", text)
            self.assertNotIn("{{", text)
            self.assertEqual(calibrate.cmd_coupon(args), 1)  # already exists


if __name__ == "__main__":
    unittest.main()
