"""Load a model's `build()` and export STEP + STL in its in-use orientation."""

from __future__ import annotations

import importlib.util
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path

from .config import REPO, model_dir, out_dir, settings

META_DEFAULTS = {
    "material": None,
    "quality": None,
    "standing": False,
    "loads": [],
    "print_orientation": "auto",
    "supports": "auto",
    "brim": "auto",
    "copies": 1,
}


class BuildError(Exception):
    pass


@dataclass
class BuildResult:
    name: str
    meta: dict
    stl: Path
    step: Path
    brep_valid: bool
    brep_volume_mm3: float
    notes: list[str] = field(default_factory=list)


def load_module(name: str):
    path = model_dir(name) / "model.py"
    if not path.exists():
        raise BuildError(f"no such model: {name} (looked for models/*/{name}/model.py; run ./cad new {name} --category <dir>)")
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location(f"models.{name.split('/')[-1].replace('-', '_')}", path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as error:
        raise BuildError(short_traceback(error, path)) from None
    return module, path


def short_traceback(error: Exception, model_path: Path) -> str:
    """Only frames from the model and cadlib — keeps error output small."""
    frames = [
        frame for frame in traceback.extract_tb(error.__traceback__)
        if frame.filename == str(model_path) or "/cadlib/" in frame.filename
    ]
    lines = [f"  {Path(f.filename).relative_to(REPO)}:{f.lineno} {f.line}" for f in frames[-4:]]
    return "\n".join([f"{type(error).__name__}: {error}", *lines])


def resolve_meta(module) -> dict:
    from .profiles import PresetError, resolve_material, resolve_quality

    meta = {**META_DEFAULTS, **getattr(module, "META", {})}
    defaults = settings()["defaults"]
    try:
        meta["material"], _ = resolve_material(meta["material"] or defaults["material"])
        meta["quality"], _, _ = resolve_quality(meta["quality"] or defaults["quality"])
    except PresetError as error:
        raise BuildError(str(error)) from None
    return meta


def build(name: str) -> BuildResult:
    from build123d import Compound, Shape, export_step, export_stl

    module, path = load_module(name)
    meta = resolve_meta(module)
    if not hasattr(module, "build"):
        raise BuildError(f"models/{name}/model.py must define build()")
    try:
        shape = module.build()
    except Exception as error:
        raise BuildError(short_traceback(error, path)) from None

    if isinstance(shape, (list, tuple)):
        shape = Compound(children=list(shape))
    if hasattr(shape, "part") and not isinstance(shape, Shape):
        shape = shape.part  # BuildPart context
    if not isinstance(shape, Shape):
        raise BuildError(f"build() returned {type(shape).__name__}, expected a build123d Part/Solid/Compound")

    notes = []
    volume = float(shape.volume)
    if volume <= 0:
        raise BuildError("build() returned an empty shape (volume 0) — check boolean operations")
    valid = bool(shape.is_valid)
    if not valid:
        notes.append("B-rep reports invalid geometry (usually a failed boolean or fillet)")

    target = out_dir(name)
    step = target / f"{name}.step"
    stl = target / f"{name}.stl"
    export_step(shape, str(step))
    export_stl(shape, str(stl), tolerance=0.01, angular_tolerance=0.15)
    return BuildResult(name, meta, stl, step, valid, volume, notes)
