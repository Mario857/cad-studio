import trimesh
from build123d import Box, Pos

from cadstudio.__main__ import run_check
from cadstudio.interference import fuse_risks
from cadstudio.mesh_check import integrity


def check_of(name, check):
    report = run_check(name, do_slice=False, do_preview=False)
    return next(c for c in report.checks if c.name == check)


def test_parts_apart_ok():
    result = fuse_risks([Box(10, 10, 10), Pos(12, 0, 0) * Box(10, 10, 10)])
    assert result.status == "OK" and not result.facts


def test_parts_too_close_warn():
    result = fuse_risks([Box(10, 10, 10), Pos(10.05, 0, 0) * Box(10, 10, 10)])
    assert result.status == "WARN" and result.facts["gap_0_1"] == 0.05


def test_parts_touching_warn():
    result = fuse_risks([Box(10, 10, 10), Pos(10, 0, 0) * Box(10, 10, 10)])
    assert result.status == "WARN" and "touch" in result.summary


def test_parts_overlapping_warn_with_volume():
    result = fuse_risks([Box(10, 10, 10), Pos(9, 0, 0) * Box(10, 10, 10)])
    assert result.status == "WARN" and result.facts["overlap_0_1"] == 100.0


def test_single_piece_is_not_checked():
    assert fuse_risks([Box(10, 10, 10)]) is None


def test_declared_set_is_not_a_mesh_warning(models_dir):
    assert check_of("good-set", "mesh").status == "OK"
    assert check_of("good-set", "fit").status == "OK"


def test_fused_set_warns(models_dir):
    fit = check_of("bad-fused-set", "fit")
    assert fit.status == "WARN" and "0.05 mm apart" in fit.summary


def test_stray_solid_warns_with_location(models_dir):
    mesh = check_of("bad-stray-solid", "mesh")
    assert mesh.status == "WARN", mesh.summary
    assert mesh.facts["bodies"] == 2 and mesh.facts["declared"] == 1
    assert mesh.facts["smallest_body_mm3"] == 27.0


def test_sealed_cavity_is_not_a_body():
    hollow = trimesh.creation.box((20, 20, 20))
    void = trimesh.creation.box((10, 10, 10))
    void.invert()
    check = integrity(trimesh.util.concatenate([hollow, void]), True)
    assert check.status == "OK", check.summary
    assert check.facts["bodies"] == 1 and check.facts["cavities"] == 1
