"""Shaded PNG previews (in-use iso/front/side + print orientation) for humans; Claude should not read them."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

LIGHT = np.array([0.4, -0.6, 0.7]) / np.linalg.norm([0.4, -0.6, 0.7])
BASE_COLOR = np.array([0.30, 0.55, 0.85])
MAX_FACES = 60000
VIEWS = [("in use — iso", 25, -55), ("in use — front", 0, -90), ("in use — side", 0, 0)]


def draw(axis, mesh: trimesh.Trimesh, title: str, elev: float, azim: float) -> None:
    faces = mesh.faces
    if len(faces) > MAX_FACES:
        faces = faces[np.random.default_rng(0).choice(len(faces), MAX_FACES, replace=False)]
    normals = trimesh.triangles.normals(mesh.vertices[faces])[0]
    shade = 0.35 + 0.65 * np.clip(normals @ LIGHT, 0, 1)
    colors = np.clip(BASE_COLOR[None, :] * shade[:, None] + 0.1, 0, 1)
    axis.add_collection3d(Poly3DCollection(mesh.vertices[faces], facecolors=colors, edgecolor="none"))
    low, high = mesh.bounds
    center, half = (low + high) / 2, (high - low).max() / 2
    for setter, c in zip((axis.set_xlim, axis.set_ylim, axis.set_zlim), center):
        setter(c - half, c + half)
    axis.set_box_aspect((1, 1, 1))
    axis.view_init(elev=elev, azim=azim)
    axis.set_title(title, fontsize=9)
    axis.set_axis_off()


def render(use_mesh: trimesh.Trimesh, print_mesh: trimesh.Trimesh | None, target: Path) -> Path:
    panels = VIEWS + ([("print orientation", 25, -55)] if print_mesh is not None else [])
    figure = plt.figure(figsize=(8, 8), dpi=110)
    for index, (title, elev, azim) in enumerate(panels):
        axis = figure.add_subplot(2, 2, index + 1, projection="3d")
        draw(axis, print_mesh if title == "print orientation" else use_mesh, title, elev, azim)
    size = "x".join(f"{v:.0f}" for v in use_mesh.extents)
    figure.suptitle(f"{target.parent.parent.name}  ({size} mm)", fontsize=11)
    figure.tight_layout()
    figure.savefig(target)
    plt.close(figure)
    return target
