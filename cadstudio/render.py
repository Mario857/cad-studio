"""`./cad render`: ray-traced review sheet (8 views incl. a section cut) for humans, rendered by Blender.

The matplotlib `preview.png` stays the fast default; this is the optional, better-looking sheet: real
shadows, one colour per body, a capped section through the part and the as-printed pose.
Blender is driven headless through `blender_scene.py`, either by an installed Blender
(`CAD_BLENDER_BIN=/Applications/Blender.app/Contents/MacOS/Blender`) or, by default, by the pinned
`bpy` wheel that uv fetches into its cache on first use (~250 MB macOS, ~430 MB Linux; nothing is added
to this project's environment).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import trimesh

SCENE_SCRIPT = Path(__file__).with_name("blender_scene.py")
BPY_SPEC = os.environ.get("CAD_BPY_SPEC", "bpy==5.3.0")
BPY_PYTHON = os.environ.get("CAD_BPY_PYTHON", "3.13")
TIMEOUT_S = 900

CLAY = (0.38, 0.55, 0.78)
PALETTE = [  # one colour per body when the model has several
    (0.26, 0.52, 0.86), (0.93, 0.60, 0.18), (0.30, 0.68, 0.42), (0.80, 0.33, 0.36),
    (0.58, 0.46, 0.80), (0.20, 0.70, 0.74), (0.86, 0.76, 0.26), (0.55, 0.58, 0.62),
]
CAP = (0.95, 0.36, 0.22)
AXES = {"x": 0, "y": 1, "z": 2}


class RenderError(Exception):
    pass


@dataclass(frozen=True)
class Cut:
    axis: int
    at: float
    keep: int  # +1 keeps the side with larger coordinates, -1 the smaller

    def label(self) -> str:
        return f"section {'XYZ'[self.axis]} = {self.at:g} mm"

    def view(self) -> tuple[float, float, float]:
        """Look at the cut face from the removed side, slightly from above and off-axis so depth reads."""
        direction = [0.35, -0.35, 0.4] if self.axis == 2 else [0.35, 0.35, 0.4]
        direction[self.axis] = -float(self.keep)
        return tuple(direction)

    def job(self) -> dict:
        return {"axis": self.axis, "at": self.at, "keep": self.keep}


def runner() -> tuple[list[str], str] | None:
    """Command prefix that runs blender_scene.py, plus a label; None when Blender cannot be driven here."""
    binary = os.environ.get("CAD_BLENDER_BIN")
    if binary:
        if not Path(binary).exists():
            raise RenderError(f"CAD_BLENDER_BIN does not exist: {binary}")
        return [binary, "-b", "--factory-startup", "--python-exit-code", "1", "-P", str(SCENE_SCRIPT), "--"], "blender"
    uv = shutil.which("uv")
    if uv:
        return [uv, "run", "--quiet", "--no-project", "--python", BPY_PYTHON, "--with", BPY_SPEC,
                "python", str(SCENE_SCRIPT)], BPY_SPEC
    return None


def body_labels(mesh: trimesh.Trimesh) -> np.ndarray:
    """Connected-component index per face, numbered by first appearance (stable between runs)."""
    raw = trimesh.graph.connected_component_labels(mesh.face_adjacency, node_count=len(mesh.faces))
    _, first, inverse = np.unique(raw, return_index=True, return_inverse=True)
    return np.argsort(np.argsort(first))[inverse].astype(np.int32)


def default_cut(mesh: trimesh.Trimesh, labels: np.ndarray) -> Cut:
    """Vertical plane through the middle of the biggest body, containing its longer horizontal axis."""
    biggest = np.bincount(labels, weights=mesh.area_faces).argmax()
    points = mesh.vertices[np.unique(mesh.faces[labels == biggest])]
    low, high = points.min(axis=0), points.max(axis=0)
    axis = 1 if high[0] - low[0] >= high[1] - low[1] else 0
    return Cut(axis, round(float((low[axis] + high[axis]) / 2), 2), +1)


def parse_cut(text: str, mesh: trimesh.Trimesh) -> Cut:
    """`x`, `y`, `z` (through the middle) or `z=12.5` (absolute mm in model coordinates)."""
    name, _, value = text.lower().partition("=")
    if name not in AXES:
        raise RenderError(f"--cut expects x, y or z (optionally =<mm>), got {text!r}")
    axis = AXES[name]
    try:
        at = float(value) if value else float(mesh.bounds.mean(axis=0)[axis])
    except ValueError:
        raise RenderError(f"--cut {text!r}: {value!r} is not a number") from None
    low, high = mesh.bounds[:, axis]
    if not low < at < high:
        raise RenderError(f"--cut {text}: plane is outside the part ({'XYZ'[axis]} spans {low:.1f}..{high:.1f} mm)")
    return Cut(axis, round(at, 2), -1 if axis == 2 else +1)  # horizontal cut keeps the lower half


def sheet_tiles(cut: Cut, tile_px: int, has_print: bool) -> list[dict]:
    tiles = [
        dict(title="in use — iso", mesh="use", dir=(1, -1, 0.8)),
        dict(title="in use — back", mesh="use", dir=(-1, 1, 0.8)),
        dict(title="front", mesh="use", dir=(0, -1, 0)),
        dict(title="side", mesh="use", dir=(1, 0, 0)),
        dict(title="top", mesh="use", dir=(0, 0, 1), ground=False),
        dict(title="bottom", mesh="use", dir=(0, 0, -1), ground=False),
        dict(title=cut.label(), mesh="use", dir=cut.view(), cut=cut.job()),
    ]
    if has_print:
        tiles.append(dict(title="as printed", mesh="print", dir=(1, -1, 0.8)))
    for tile in tiles:
        tile["res"] = (tile_px, tile_px)
    return tiles


def write_npz(mesh: trimesh.Trimesh, labels: np.ndarray, path: Path) -> None:
    np.savez(path, vertices=np.asarray(mesh.vertices, dtype=np.float32),
             faces=np.asarray(mesh.faces, dtype=np.int32), body=labels)


def run_blender(job: dict, work: Path) -> str:
    found = runner()
    if found is None:
        raise RenderError("needs uv (fetches the bpy wheel) or CAD_BLENDER_BIN=<path to blender>")
    command, label = found
    job_file = work / "job.json"
    job_file.write_text(json.dumps(job))
    # ./cad runs inside the project's uv environment; the bpy interpreter must not inherit it.
    env = {k: v for k, v in os.environ.items() if k not in ("VIRTUAL_ENV", "PYTHONPATH", "PYTHONHOME")}
    try:
        result = subprocess.run(command + [str(job_file)], capture_output=True, text=True, timeout=TIMEOUT_S, env=env)
    except subprocess.TimeoutExpired:
        raise RenderError(f"blender timed out after {TIMEOUT_S}s") from None
    missing = [tile["out"] for tile in job["tiles"] if not Path(tile["out"]).exists()]
    if result.returncode != 0 or "@@DONE@@" not in result.stdout or missing:
        log = work / "blender.log"
        log.write_text(result.stdout + "\n" + result.stderr)
        lines = [l for l in (result.stderr + result.stdout).splitlines() if "Error" in l or "error" in l]
        raise RenderError(f"{label} exit {result.returncode}: {(lines[-1] if lines else 'no output')[-200:]} (log: {log})")
    return result.stdout.split("@@DONE@@", 1)[1].strip().splitlines()[0]


def font(size: int):
    import matplotlib
    from PIL import ImageFont

    return ImageFont.truetype(str(Path(matplotlib.get_data_path()) / "fonts/ttf/DejaVuSans.ttf"), size)


def flatten(path: Path, background=(255, 255, 255)):
    from PIL import Image

    tile = Image.open(path).convert("RGBA")
    canvas = Image.new("RGBA", tile.size, (*background, 255))
    canvas.alpha_composite(tile)
    return canvas.convert("RGB")


def compose_sheet(tiles: list[dict], caption: str, target: Path, columns: int = 4) -> Path:
    from PIL import Image, ImageDraw

    size = tiles[0]["res"][0]
    header, label_h, gap = round(size * 0.13), round(size * 0.075), round(size * 0.02)
    rows = -(-len(tiles) // columns)
    sheet = Image.new("RGB", (columns * size + (columns + 1) * gap, header + rows * (size + label_h + gap)), "white")
    draw = ImageDraw.Draw(sheet)
    draw.text((gap * 2, header * 0.25), caption, fill=(20, 20, 20), font=font(round(header * 0.42)))
    for index, tile in enumerate(tiles):
        x = gap + (index % columns) * (size + gap)
        y = header + (index // columns) * (size + label_h + gap)
        draw.rectangle((x, y, x + size - 1, y + size + label_h - 1), fill=(246, 247, 249))
        sheet.paste(flatten(Path(tile["out"]), (246, 247, 249)), (x, y + label_h))
        draw.text((x + gap, y + label_h * 0.18), tile["title"], fill=(60, 60, 60), font=font(round(label_h * 0.55)))
    sheet.save(target, optimize=True)
    return target


def render(name: str, use_mesh: trimesh.Trimesh, print_mesh: trimesh.Trimesh | None, out: Path, work: Path,
           cut: str | None = None, hero: bool = False, tile_px: int = 512, samples: int = 24) -> list[Path]:
    """Render out/render.png (and out/hero.png with hero=True). Returns the files written."""
    work.mkdir(parents=True, exist_ok=True)
    labels = body_labels(use_mesh)
    bodies = int(labels.max()) + 1
    section = parse_cut(cut, use_mesh) if cut else default_cut(use_mesh, labels)

    meshes = {"use": str(work / "use.npz")}
    write_npz(use_mesh, labels, work / "use.npz")
    if print_mesh is not None and len(print_mesh.faces) == len(use_mesh.faces):
        write_npz(print_mesh, labels, work / "print.npz")  # same faces, re-oriented: bodies keep their colours
        meshes["print"] = str(work / "print.npz")

    tiles = sheet_tiles(section, tile_px, "print" in meshes)
    for index, tile in enumerate(tiles):
        tile["out"] = str(work / f"tile{index}.png")
    job_tiles = list(tiles)
    hero_tile = None
    if hero:
        hero_tile = dict(mesh="use", dir=(1, -1.25, 0.7), res=(1600, 1200), persp=True, out=str(work / "hero.png"))
        job_tiles.append(hero_tile)
    for tile in job_tiles:
        Path(tile["out"]).unlink(missing_ok=True)

    job = {
        "meshes": meshes,
        "colors": [CLAY] if bodies == 1 else PALETTE,
        "cap_color": CAP,
        "samples": samples,
        "tiles": [{k: v for k, v in tile.items() if k != "title"} for tile in job_tiles],
    }
    run_blender(job, work)

    size = " x ".join(f"{v:.0f}" for v in use_mesh.extents)
    caption = f"{name}   {size} mm" + (f"   {bodies} bodies (one colour each)" if bodies > 1 else "")
    written = [compose_sheet(tiles, caption, out / "render.png")]
    if hero_tile:
        flatten(Path(hero_tile["out"]), (238, 240, 243)).save(out / "hero.png", optimize=True)
        written.append(out / "hero.png")
    return written
