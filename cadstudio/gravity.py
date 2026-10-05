"""Gravity audit: in-use tip-over stability and print-orientation search (overhangs, supports, bed contact)."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import trimesh
from shapely.geometry import MultiPoint, Point
from shapely.ops import nearest_points

from .config import audit_cfg, printer_cfg
from .report import Check

CONTACT_TOL_MM = 0.05
FIRST_LAYER_MM = 0.2
SAME_DIRECTION_DOT = 0.996
AS_MODELED_BONUS = 0.5
MAX_STABLE_POSES = 8


@dataclass
class Footing:
    contact_cm2: float
    tip_deg: float
    margin_mm: float
    weak_side: str


@dataclass
class Orientation:
    label: str
    transform: np.ndarray
    support_cm2: float
    overhang_cm2: float
    contact_cm2: float
    height_mm: float
    tip_deg: float
    fits: bool
    score: float = 0.0

    def describe(self) -> str:
        return (f"{self.label}: support {self.support_cm2:.1f} cm2, overhang {self.overhang_cm2:.1f} cm2, "
                f"contact {self.contact_cm2:.1f} cm2, h {self.height_mm:.0f} mm")


@dataclass
class PrintPlan:
    chosen: Orientation
    supports: bool
    brim: bool
    mesh: trimesh.Trimesh
    candidates: list[Orientation] = field(default_factory=list)


def axis_name(vector: np.ndarray) -> str:
    axis = int(np.argmax(np.abs(vector[:2])))
    return ("+" if vector[axis] > 0 else "-") + "XY"[axis]


def footing(mesh: trimesh.Trimesh, com: np.ndarray) -> Footing | None:
    """Support polygon = convex hull of everything touching the lowest plane."""
    zmin = mesh.bounds[0][2]
    touching = mesh.vertices[mesh.vertices[:, 2] < zmin + CONTACT_TOL_MM][:, :2]
    hull = MultiPoint([tuple(p) for p in touching]).convex_hull
    if hull.geom_type != "Polygon" or hull.area < 1.0:
        return None
    point = Point(com[0], com[1])
    distance = hull.exterior.distance(point)
    margin = distance if hull.contains(point) else -distance
    edge_point = nearest_points(hull.exterior, point)[0]
    toward_edge = np.array([edge_point.x - com[0], edge_point.y - com[1]])
    direction = toward_edge if margin >= 0 else -toward_edge
    height = max(com[2] - zmin, 1e-6)
    normals_down = -mesh.face_normals[:, 2]
    on_plane = (normals_down > 0.995) & (mesh.triangles_center[:, 2] < zmin + CONTACT_TOL_MM)
    return Footing(
        contact_cm2=float(mesh.area_faces[on_plane].sum() / 100),
        tip_deg=math.degrees(math.atan2(margin, height)),
        margin_mm=margin,
        weak_side=axis_name(direction) if np.linalg.norm(direction) > 1e-9 else "?",
    )


def use_stability(mesh: trimesh.Trimesh, meta: dict, part_grams: float) -> Check:
    """Model coordinates are the in-use orientation (Z up). Loads are extra masses carried in use."""
    if not meta["standing"]:
        return Check("use", "SKIP", "not free-standing (META standing=False)")
    cfg = audit_cfg()
    weighted = mesh.center_mass * part_grams
    total = part_grams
    for load in meta["loads"]:
        weighted = weighted + np.asarray(load["at"], dtype=float) * float(load["grams"])
        total += float(load["grams"])
    com = weighted / total
    foot = footing(mesh, com)
    load_note = f" incl. {total - part_grams:.0f} g load" if meta["loads"] else ""
    facts = {"part_g": round(part_grams, 1), "com_mm": [round(float(v), 1) for v in com]}
    if foot is None:
        return Check("use", "FAIL", "rests on a point/line, it will fall over — add a flat base", facts)
    facts.update(tip_deg=round(foot.tip_deg, 1), margin_mm=round(foot.margin_mm, 1), weak_side=foot.weak_side)
    summary = f"tips at {foot.tip_deg:.1f} deg toward {foot.weak_side}{load_note} (COM margin {foot.margin_mm:.1f} mm)"
    if foot.tip_deg < cfg["tip_fail_deg"]:
        return Check("use", "FAIL", f"{summary} — falls over; widen base toward {foot.weak_side} or lower COM", facts)
    if foot.tip_deg < cfg["tip_warn_deg"]:
        return Check("use", "WARN", f"{summary} — easy to knock over", facts)
    return Check("use", "OK", summary, facts)


def candidate_directions(mesh: trimesh.Trimesh) -> list[tuple[str, np.ndarray]]:
    """Model-frame directions that would point down (-Z) on the bed."""
    directions = [
        ("as modeled", np.array([0, 0, -1.0])),
        ("top down", np.array([0, 0, 1.0])),
        ("+X down", np.array([1.0, 0, 0])),
        ("-X down", np.array([-1.0, 0, 0])),
        ("+Y down", np.array([0, 1.0, 0])),
        ("-Y down", np.array([0, -1.0, 0])),
    ]
    try:
        transforms, probabilities = trimesh.poses.compute_stable_poses(mesh, n_samples=1)
        for transform, _ in sorted(zip(transforms, probabilities), key=lambda tp: -tp[1])[:MAX_STABLE_POSES]:
            down = transform[:3, :3].T @ np.array([0, 0, -1.0])
            directions.append(("stable face", down / np.linalg.norm(down)))
    except Exception:
        pass
    unique: list[tuple[str, np.ndarray]] = []
    for label, direction in directions:
        if all(np.dot(direction, kept) < SAME_DIRECTION_DOT for _, kept in unique):
            unique.append((label, direction))
    return unique


def evaluate(mesh: trimesh.Trimesh, label: str, down: np.ndarray) -> Orientation:
    cfg, printer = audit_cfg(), printer_cfg()
    rotation = trimesh.geometry.align_vectors(down, [0, 0, -1.0])
    placed = mesh.copy()
    placed.apply_transform(rotation)
    lift = trimesh.transformations.translation_matrix([0, 0, -placed.bounds[0][2]])
    placed.apply_transform(lift)
    transform = lift @ rotation

    facing_down = -placed.face_normals[:, 2]
    heights = placed.triangles_center[:, 2]
    areas = placed.area_faces
    lifted = heights > FIRST_LAYER_MM
    overhang = lifted & (facing_down > math.cos(math.radians(cfg["overhang_deg"])))
    support = lifted & (facing_down > math.cos(math.radians(cfg["support_deg"])))

    foot = footing(placed, placed.center_mass)
    x, y, z = placed.extents
    fits = z <= printer["bed_z_mm"] and (
        (x <= printer["bed_x_mm"] and y <= printer["bed_y_mm"]) or (y <= printer["bed_x_mm"] and x <= printer["bed_y_mm"])
    )
    return Orientation(
        label=label,
        transform=transform,
        support_cm2=float(areas[support].sum() / 100),
        overhang_cm2=float(areas[overhang].sum() / 100),
        contact_cm2=foot.contact_cm2 if foot else 0.0,
        height_mm=float(z),
        tip_deg=foot.tip_deg if foot else 0.0,
        fits=bool(fits),
    )


def score(option: Orientation) -> float:
    value = option.support_cm2 * 8 + option.overhang_cm2 * 1.5 + option.height_mm / 25 - min(option.contact_cm2, 25) * 0.3
    if option.tip_deg < 10:
        value += 5
    if option.contact_cm2 < 0.5:
        value += 50
    if not option.fits:
        value += 1e6
    if option.label == "as modeled":
        value -= AS_MODELED_BONUS
    return value


def fixed_orientation(mesh: trimesh.Trimesh, angles_deg) -> Orientation:
    rx, ry, rz = (math.radians(a) for a in angles_deg)
    rotation = trimesh.transformations.euler_matrix(rx, ry, rz, "sxyz")
    down = rotation[:3, :3].T @ np.array([0, 0, -1.0])
    option = evaluate(mesh, f"fixed rot {tuple(angles_deg)}", down)
    placed = mesh.copy().apply_transform(rotation)
    option.transform = trimesh.transformations.translation_matrix([0, 0, -placed.bounds[0][2]]) @ rotation
    return option


def plan_print(mesh: trimesh.Trimesh, meta: dict) -> tuple[PrintPlan, list[Check]]:
    cfg = audit_cfg()
    if meta["print_orientation"] == "auto":
        candidates = [evaluate(mesh, label, down) for label, down in candidate_directions(mesh)]
        for option in candidates:
            option.score = score(option)
        candidates.sort(key=lambda o: o.score)
        chosen = candidates[0]
    else:
        chosen = fixed_orientation(mesh, meta["print_orientation"])
        candidates = [chosen]

    placed = mesh.copy()
    placed.apply_transform(chosen.transform)
    supports = {"on": True, "off": False}.get(meta["supports"], chosen.support_cm2 > cfg["auto_support_cm2"])
    footprint = min(placed.extents[0], placed.extents[1])
    tall = placed.extents[2] / max(footprint, 1e-6) > 4
    brim = {"on": True, "off": False}.get(meta["brim"], chosen.contact_cm2 < cfg["brim_below_cm2"] or tall)

    checks = []
    status = "OK" if chosen.fits else "FAIL"
    detail = "" if chosen.fits else " — does not fit the H2C build volume"
    alternatives = "; ".join(f"{o.label} {o.score:.1f}" for o in candidates[1:3])
    checks.append(Check(
        "orient", status,
        f"{chosen.describe()}{detail}" + (f" [next: {alternatives}]" if alternatives else ""),
        {"chosen": chosen.label, "score": round(chosen.score, 2)},
    ))

    floating = [b for b in placed.split(only_watertight=False) if b.bounds[0][2] > CONTACT_TOL_MM]
    support_status = "OK"
    support_note = f"supports {'ON (tree)' if supports else 'off'}, brim {'on' if brim else 'off'}"
    if floating and not supports:
        support_status, support_note = "FAIL", f"{len(floating)} body floats above the bed with supports off"
    elif chosen.support_cm2 > cfg["auto_support_cm2"] and not supports:
        support_status = "WARN"
        support_note += f"; {chosen.support_cm2:.1f} cm2 needs support but supports=off"
    elif supports:
        support_status = "WARN"
        support_note += f" for {chosen.support_cm2:.1f} cm2 — redesign (chamfers <=45 deg, teardrops) to avoid"
    if chosen.tip_deg < 10 and chosen.fits:
        support_note += f"; wobbly on bed (tips at {chosen.tip_deg:.0f} deg)"
        support_status = "WARN" if support_status == "OK" else support_status
    checks.append(Check("support", support_status, support_note, {"supports": supports, "brim": brim}))
    return PrintPlan(chosen, supports, brim, placed, candidates), checks
