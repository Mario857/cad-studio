"""Strength estimate (APPROXIMATE): peak bending + axial stress on the weakest cross-section along the load path.

For each declared force (META force=[dict(at, newtons, dir)] and META loads, treated as gravity forces) the mesh is
sliced by planes perpendicular to the lever arm (load point -> part centre of mass). At each slice the moment of the
force about the section centroid and the section's second moment of area give sigma = M*c/I + F_axial/A. The worst
slice is compared with the material's printed strength: strength_z if the beam axis is within 45 deg of the print Z
axis (tension across layers), else strength_xy. Solid-section assumption; infill, stress concentrations, creep and
layer-line quality are NOT modelled, hence the safety factor.
"""

from __future__ import annotations

import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient

from .config import audit_cfg, settings
from .report import Check

GRAVITY = 9.81
SECTIONS = 48
END_MARGIN = 0.02  # skip the very ends of the lever arm (zero moment at the tip, mesh edge at the far end)
Z_AXIS_DOT = 0.707


def forces_of(meta: dict) -> list[tuple[np.ndarray, float, np.ndarray, str]]:
    """(point, newtons, unit direction, label) for every declared force and load."""
    found = []
    for item in meta.get("force") or []:
        direction = np.asarray(item.get("dir", (0, 0, -1)), dtype=float)
        found.append((np.asarray(item["at"], dtype=float), float(item["newtons"]),
                      direction / np.linalg.norm(direction), "force"))
    for item in meta.get("loads") or []:
        found.append((np.asarray(item["at"], dtype=float), float(item["grams"]) * GRAVITY / 1000,
                      np.array([0.0, 0.0, -1.0]), "load"))
    return [f for f in found if f[1] > 0]


def section_stress(polygons: list[Polygon], moment_dir: np.ndarray | None, moment: float, axial: float):
    """Peak stress (MPa) in a planar section; moment_dir = unit neutral-axis direction in plane coordinates."""
    area = sum(p.area for p in polygons)
    if area < 1e-6:
        return None
    stress = axial / area
    if moment_dir is None or moment <= 0:
        return stress
    m = moment_dir
    n = np.array([-m[1], m[0]])
    inertia_origin = 0.0
    cn_area = 0.0
    far = []
    for poly in polygons:
        poly = orient(poly, 1.0)
        for ring in [poly.exterior, *poly.interiors]:
            xy = np.asarray(ring.coords)
            pm, pn = xy @ m, xy @ n
            cross = pm[:-1] * pn[1:] - pm[1:] * pn[:-1]
            inertia_origin += float(np.sum((pn[:-1] ** 2 + pn[:-1] * pn[1:] + pn[1:] ** 2) * cross) / 12)
            cn_area += float(np.sum((pn[:-1] + pn[1:]) * cross) / 6)
        far.append(np.asarray(poly.exterior.coords) @ n)
    centroid_n = cn_area / area
    inertia = inertia_origin - area * centroid_n ** 2
    reach = max(float(np.max(np.abs(f - centroid_n))) for f in far)
    if inertia <= 1e-6:
        return None
    return stress + moment * reach / inertia


def worst_section(mesh: trimesh.Trimesh, point: np.ndarray, newtons: float, direction: np.ndarray):
    """Return (peak MPa, axis unit vector, location xyz) over sections along the lever arm, or None."""
    lever = mesh.center_mass - point
    if np.linalg.norm(lever) < 1e-6:
        return None
    axis = lever / np.linalg.norm(lever)
    force = newtons * direction
    along = (mesh.vertices - point) @ axis
    t_end = float(along.max())
    if t_end <= 0:
        return None
    worst = None
    for t in np.linspace(t_end * END_MARGIN, t_end * (1 - END_MARGIN), SECTIONS):
        origin = point + axis * t
        path = mesh.section(plane_origin=origin, plane_normal=axis)
        if path is None:
            continue
        planar, to_3d = path.to_planar()
        polygons = [p for p in planar.polygons_full if p.is_valid]
        if not polygons:
            continue
        area = sum(p.area for p in polygons)
        centroid = sum((np.asarray(p.centroid.coords[0]) * p.area for p in polygons)) / area
        centroid_3d = (to_3d @ np.array([centroid[0], centroid[1], 0, 1.0]))[:3]
        moment_vec = np.cross(centroid_3d - point, force)  # N*mm
        in_plane = to_3d[:3, :3].T @ moment_vec
        planar_m = in_plane[:2]
        norm = np.linalg.norm(planar_m)
        moment_dir = planar_m / norm if norm > 1e-9 else None
        stress = section_stress(polygons, moment_dir, float(norm), abs(float(force @ axis)))
        if stress is not None and (worst is None or stress > worst[0]):
            worst = (stress, axis, centroid_3d)
    return worst


def material_strength(material: str) -> tuple[float, float, str]:
    table = settings()["materials"]
    key = material if material in table else "PLA"
    note = "" if key == material else f"; no strength data for {material!r}, PLA values used"
    entry = table[key]
    return float(entry.get("strength_xy_mpa", 40)), float(entry.get("strength_z_mpa", 20)), note


def strength_check(mesh: trimesh.Trimesh, meta: dict, plan) -> Check:
    forces = forces_of(meta)
    if not forces:
        return Check("strength", "SKIP", "no META force/loads declared")
    cfg = audit_cfg()
    warn_sf, fail_sf = float(cfg.get("safety_factor", 3)), float(cfg.get("safety_factor_fail", 1.5))
    xy, z, note = material_strength(meta["material"])
    rotation = plan.chosen.transform[:3, :3]

    best = None  # (safety factor, stress, allowed, location, orientation)
    for point, newtons, direction, _label in forces:
        result = worst_section(mesh, point, newtons, direction)
        if result is None:
            continue
        stress, axis, where = result
        printed_z = abs(float((rotation @ axis)[2])) > Z_AXIS_DOT
        allowed = z if printed_z else xy
        factor = allowed / max(stress, 1e-9)
        if best is None or factor < best[0]:
            best = (factor, stress, allowed, where, "Z (across layers)" if printed_z else "XY (along layers)")
    if best is None:
        return Check("strength", "WARN", "could not slice a load path (load point at centre of mass?)")
    factor, stress, allowed, where, orient_note = best
    facts = {"stress_mpa": round(stress, 2), "allowed_mpa": allowed, "safety_factor": round(factor, 2),
             "at_xyz": [round(float(v), 1) for v in where]}
    summary = (f"~{stress:.1f} MPa peak vs {allowed:g} MPa {orient_note}, safety factor ~{factor:.1f} "
               f"near {facts['at_xyz']} [rough beam estimate, solid section{note}]")
    if factor < fail_sf:
        return Check("strength", "FAIL", f"{summary} — will likely break; thicken the weakest section or reorient", facts)
    if factor < warn_sf:
        return Check("strength", "WARN", f"{summary} — below target {warn_sf:g}", facts)
    return Check("strength", "OK", summary, facts)
