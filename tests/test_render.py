"""./cad render: everything except Blender itself runs here; the real render is opt-in (CAD_TEST_BLENDER=1)."""
import json
import os
import stat
import sys

import numpy as np
import pytest
import trimesh
from PIL import Image

from cadstudio import render as R


def two_boxes():
    big = trimesh.creation.box((40, 20, 10))
    small = trimesh.creation.box((5, 5, 5))
    small.apply_translation((60, 0, 0))
    return trimesh.util.concatenate([big, small])


FAKE_BLENDER = """#!{python}
import json, sys
from PIL import Image
assert sys.argv[1:7] == ["-b", "--factory-startup", "--python-exit-code", "1", "-P", {script!r}], sys.argv
assert sys.argv[7] == "--"
job = json.load(open(sys.argv[8]))
for tile in job["tiles"]:
    Image.new("RGBA", tuple(tile["res"]), (200, 60, 60, 128)).save(tile["out"])
print("@@DONE@@ blender fake")
"""


@pytest.fixture
def fake_blender(tmp_path, monkeypatch):
    binary = tmp_path / "blender"
    binary.write_text(FAKE_BLENDER.format(python=sys.executable, script=str(R.SCENE_SCRIPT)))
    binary.chmod(binary.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("CAD_BLENDER_BIN", str(binary))
    return binary


def test_body_labels_are_per_body_and_stable():
    mesh = two_boxes()
    labels = R.body_labels(mesh)
    assert labels[0] == 0 and set(labels) == {0, 1}
    assert (labels[:12] == 0).all() and (labels[12:] == 1).all()


def test_default_cut_goes_through_the_biggest_body_along_its_long_axis():
    mesh = two_boxes()
    cut = R.default_cut(mesh, R.body_labels(mesh))
    assert (cut.axis, cut.at, cut.keep) == (1, 0.0, 1)  # plane Y=0 contains the 40 mm X axis of the big box


def test_parse_cut():
    mesh = two_boxes()
    assert R.parse_cut("z", mesh).job() == {"axis": 2, "at": 0.0, "keep": -1}
    assert R.parse_cut("x=10", mesh).job() == {"axis": 0, "at": 10.0, "keep": 1}
    with pytest.raises(R.RenderError, match="outside the part"):
        R.parse_cut("z=50", mesh)
    with pytest.raises(R.RenderError, match="expects x, y or z"):
        R.parse_cut("w", mesh)


def test_cut_view_looks_at_the_cut_face():
    assert R.Cut(1, 0.0, +1).view()[1] == -1.0  # keeps +Y, so the camera sits on the -Y side
    assert R.Cut(2, 0.0, -1).view()[2] == 1.0   # keeps the lower half, camera above


def test_runner_rejects_a_missing_binary(monkeypatch):
    monkeypatch.setenv("CAD_BLENDER_BIN", "/nonexistent/blender")
    with pytest.raises(R.RenderError):
        R.runner()


def test_runner_defaults_to_the_pinned_bpy_wheel(monkeypatch):
    monkeypatch.delenv("CAD_BLENDER_BIN", raising=False)
    monkeypatch.setattr(R.shutil, "which", lambda name: "/usr/bin/uv")
    command, label = R.runner()
    assert label == R.BPY_SPEC and "--no-project" in command and command[-1] == str(R.SCENE_SCRIPT)
    monkeypatch.setattr(R.shutil, "which", lambda name: None)
    assert R.runner() is None


def test_render_writes_sheet_and_hero(tmp_path, fake_blender):
    mesh = two_boxes()
    flipped = mesh.copy()
    flipped.apply_transform(trimesh.transformations.rotation_matrix(np.pi, (1, 0, 0)))
    files = R.render("demo", mesh, flipped, tmp_path, tmp_path / "work", cut="z=1", hero=True, tile_px=64)
    assert [f.name for f in files] == ["render.png", "hero.png"]
    sheet = Image.open(tmp_path / "render.png")
    assert sheet.mode == "RGB" and sheet.width > 4 * 64 and sheet.height > 2 * 64
    assert Image.open(tmp_path / "hero.png").size == (1600, 1200)

    job = json.loads((tmp_path / "work" / "job.json").read_text())
    assert len(job["tiles"]) == 9 and set(job["meshes"]) == {"use", "print"}
    assert job["tiles"][6]["cut"] == {"axis": 2, "at": 1.0, "keep": -1}
    assert job["colors"] == [list(c) for c in R.PALETTE]  # two bodies -> palette, not clay
    data = np.load(job["meshes"]["use"])
    assert data["faces"].shape == (24, 3) and data["body"].max() == 1


def test_render_reports_a_blender_failure(tmp_path, fake_blender):
    fake_blender.write_text(f"#!{sys.executable}\nimport sys\nprint('Error: boom')\nsys.exit(1)\n")
    with pytest.raises(R.RenderError, match="boom"):
        R.render("demo", two_boxes(), None, tmp_path, tmp_path / "work", tile_px=64)
    assert (tmp_path / "work" / "blender.log").exists()


@pytest.mark.skipif(not os.environ.get("CAD_TEST_BLENDER"), reason="set CAD_TEST_BLENDER=1 (downloads the bpy wheel)")
def test_real_blender_render(tmp_path, monkeypatch):
    monkeypatch.delenv("CAD_BLENDER_BIN", raising=False)
    mesh = two_boxes()
    files = R.render("demo", mesh, mesh, tmp_path, tmp_path / "work", tile_px=96, samples=4)
    pixels = np.asarray(Image.open(files[0]).convert("L"), dtype=float)
    assert pixels.std() > 5  # not a blank sheet
    section = np.asarray(Image.open(tmp_path / "work" / "tile6.png").convert("RGB"), dtype=int)
    reddish = (section[..., 0] > 180) & (section[..., 2] < 150) & (section[..., 0] - section[..., 2] > 70)
    assert reddish.mean() > 0.01  # the capped cut face is visible
