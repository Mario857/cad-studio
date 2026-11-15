"""Tolerance sweep: rebuild with CLEAR/GAP/TOL parameters perturbed by +-0.1 mm; mesh + wall checks per variant.

Variants are built in memory from a patched copy of model.py (so derived module constants follow); nothing is
written to out/.
"""

from __future__ import annotations

import ast
import importlib.util
import tempfile
from pathlib import Path

from .report import RANK, Check

DELTA_MM = 0.1
KEYWORDS = ("CLEAR", "GAP", "TOL")
MAX_PARAMS = 6


def literal_floats(tree: ast.Module) -> dict[str, float]:
    found = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            try:
                value = ast.literal_eval(node.value)
            except ValueError:
                continue
            if name.isupper() and isinstance(value, float) and any(k in name for k in KEYWORDS):
                found[name] = value
    return found


def build_variant(name: str, path: Path, overrides: dict[str, float]):
    """Exec the model with literal overrides; return (mesh, brep_valid)."""
    from build123d import Compound, Shape, export_stl

    from .build import BuildError, short_traceback
    from .mesh_check import load_mesh

    patched = ast.parse(path.read_text())
    for node in patched.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and getattr(node.targets[0], "id", None) in overrides:
            node.value = ast.Constant(overrides[node.targets[0].id])
    ast.fix_missing_locations(patched)
    spec = importlib.util.spec_from_file_location(f"sweep_{name.split('/')[-1].replace('-', '_')}", path)
    module = importlib.util.module_from_spec(spec)
    try:
        exec(compile(patched, str(path), "exec"), module.__dict__)
        shape = module.build()
    except Exception as error:
        raise BuildError(short_traceback(error, path)) from None
    if isinstance(shape, (list, tuple)):
        shape = Compound(children=list(shape))
    if hasattr(shape, "part") and not isinstance(shape, Shape):
        shape = shape.part
    if not isinstance(shape, Shape) or float(shape.volume) <= 0:
        raise BuildError("build() returned no solid")
    with tempfile.TemporaryDirectory() as tmp:
        stl = Path(tmp) / "variant.stl"
        export_stl(shape, str(stl), tolerance=0.01, angular_tolerance=0.15)
        return load_mesh(stl), bool(shape.is_valid)


def evaluate(name: str, path: Path, overrides: dict[str, float]) -> tuple[int, str]:
    """(worst rank, text) over mesh integrity + walls; build failure = FAIL."""
    from .build import BuildError
    from .mesh_check import integrity, wall_thickness

    try:
        mesh, valid = build_variant(name, path, overrides)
    except BuildError as error:
        return 2, f"build error: {str(error).splitlines()[0]}"
    checks = [integrity(mesh, valid)]
    if checks[0].status != "FAIL":
        checks.append(wall_thickness(mesh))
    worst = max(checks, key=lambda c: RANK[c.status])
    return RANK[worst.status], f"{worst.name} {worst.status}: {worst.summary}"


def sweep_check(name: str) -> Check:
    from .config import model_dir

    path = model_dir(name) / "model.py"
    if not path.exists():
        return Check("sweep", "FAIL", f"no such model: {name}")
    params = dict(list(literal_floats(ast.parse(path.read_text())).items())[:MAX_PARAMS])
    if not params:
        return Check("sweep", "SKIP", "no UPPER_CASE float parameter with CLEAR/GAP/TOL in its name")
    base_rank, base_text = evaluate(name, path, {})
    problems, worst, runs = [], base_rank, 0
    for param, value in params.items():
        for sign in (-1, 1):
            variant = round(value + sign * DELTA_MM, 6)
            if variant < 0:
                continue
            runs += 1
            rank, text = evaluate(name, path, {param: variant})
            if rank > base_rank:
                worst = max(worst, rank)
                problems.append(f"{param}={variant:g}: {text}")
    summary = f"{runs} variants of {', '.join(params)} at +-{DELTA_MM} mm"
    facts = {"params": params, "baseline": base_text}
    if problems:
        return Check("sweep", "FAIL" if worst == 2 else "WARN", f"{summary}; breaks: " + " | ".join(problems[:3]), facts)
    return Check("sweep", "OK", f"{summary}, none worse than nominal ({base_text})", facts)
