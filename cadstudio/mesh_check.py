"""Mesh integrity and wall-thickness checks (orientation independent)."""

from __future__ import annotations

import numpy as np
import trimesh

from .config import audit_cfg
from .report import Check

MAX_THICKNESS_RAYS = 2500
RAY_EPSILON_MM = 1e-3


def load_mesh(path) -> trimesh.Trimesh:
    mesh = trimesh.load_mesh(path, process=True)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.to_mesh()
    return mesh


def integrity(mesh: trimesh.Trimesh, brep_valid: bool, declared: int = 1) -> Check:
    """`declared` = how many separate pieces build() says it returns (1, or the length of its list)."""
    shells = mesh.split(only_watertight=False)
    # A sealed internal void is its own inward-facing shell (negative volume): not a body.
    cavities = [s for s in shells if s.is_watertight and s.volume < 0]
    bodies = [s for s in shells if not (s.is_watertight and s.volume < 0)]
    facts = {
        "watertight": bool(mesh.is_watertight),
        "winding_ok": bool(mesh.is_winding_consistent),
        "bodies": len(bodies),
        "declared": declared,
        "cavities": len(cavities),
        "volume_cm3": round(float(mesh.volume) / 1000, 2),
        "triangles": len(mesh.faces),
        "bbox_mm": [round(float(v), 1) for v in mesh.extents],
    }
    problems = []
    if not facts["watertight"]:
        problems.append("mesh not watertight (open edges)")
    if not facts["winding_ok"]:
        problems.append("inconsistent face winding")
    if not brep_valid:
        problems.append("invalid B-rep")
    size = "x".join(f"{v:g}" for v in facts["bbox_mm"])
    summary = f"{facts['volume_cm3']} cm3, bbox {size} mm, {facts['bodies']} body, {facts['triangles']} tris"
    if cavities:
        summary += f", {len(cavities)} sealed cavity"
    if problems:
        return Check("mesh", "FAIL", "; ".join(problems), facts)
    if len(bodies) > declared:
        loose = min(bodies, key=lambda body: abs(body.volume))
        where = ", ".join(f"{v:.1f}" for v in loose.bounds.mean(axis=0))
        facts["smallest_body_mm3"] = round(abs(float(loose.volume)), 2)
        hint = "return a list if they are separate parts" if declared == 1 else "a part is in several pieces"
        return Check("mesh", "WARN", f"{summary} — {len(bodies)} bodies but build() declares {declared} part"
                     f"{'s' if declared > 1 else ''}: smallest is {facts['smallest_body_mm3']} mm3 at ({where}); "
                     f"stray solid / missing union, or {hint}", facts)
    return Check("mesh", "OK", summary, facts)


def wall_thickness(mesh: trimesh.Trimesh) -> Check:
    """Cast rays inward from area-weighted surface samples; hit distance = local thickness."""
    cfg = audit_cfg()
    rng = np.random.default_rng(0)
    areas = mesh.area_faces
    count = min(MAX_THICKNESS_RAYS, len(mesh.faces))
    faces = rng.choice(len(mesh.faces), size=count, replace=count > len(mesh.faces), p=areas / areas.sum())
    normals = mesh.face_normals[faces]
    origins = mesh.triangles_center[faces] - normals * RAY_EPSILON_MM
    locations, ray_index, _ = mesh.ray.intersects_location(origins, -normals, multiple_hits=False)
    if len(ray_index) == 0:
        return Check("walls", "WARN", "could not measure (no ray hits)")

    thickness = np.full(count, np.nan)
    thickness[ray_index] = np.linalg.norm(locations - origins[ray_index], axis=1)
    measured = ~np.isnan(thickness)
    values = thickness[measured]
    weights = areas[faces][measured]
    weights = weights / weights.sum()

    thin_fail = float(weights[values < cfg["fail_wall_mm"]].sum() * 100)
    thin_warn = float(weights[values < cfg["warn_wall_mm"]].sum() * 100)
    p2 = float(np.percentile(values, 2))
    facts = {
        "p2_mm": round(p2, 2),
        "median_mm": round(float(np.median(values)), 2),
        "area_pct_below_fail": round(thin_fail, 1),
        "area_pct_below_warn": round(thin_warn, 1),
    }
    thin_spots = origins[measured][values < cfg["warn_wall_mm"]]
    if len(thin_spots):
        facts["thin_example_xyz"] = [round(float(v), 1) for v in thin_spots[0]]

    summary = f"thinnest ~{p2:.2f} mm (p2), median {facts['median_mm']} mm"
    if thin_fail > 1.0:
        where = f" near {facts['thin_example_xyz']}" if "thin_example_xyz" in facts else ""
        return Check("walls", "FAIL", f"{thin_fail:.1f}% of surface < {cfg['fail_wall_mm']} mm{where}", facts)
    if thin_warn > 3.0:
        where = f" near {facts['thin_example_xyz']}" if "thin_example_xyz" in facts else ""
        return Check("walls", "WARN", f"{summary}; {thin_warn:.1f}% of surface < {cfg['warn_wall_mm']} mm{where}", facts)
    return Check("walls", "OK", summary, facts)
