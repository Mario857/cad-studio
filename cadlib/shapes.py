"""Print-friendly primitives. Solids sit on z=0 (bed / table) unless noted."""

from __future__ import annotations

import math

from build123d import (
    Align, Axis, Box, Circle, Part, Plane, Polygon, Pos, Rot, Text, chamfer, extrude, fillet,
)

from .fit import HOLE_COMPENSATION

ON_BED = (Align.CENTER, Align.CENTER, Align.MIN)
ELEPHANT_FOOT_CHAMFER = 0.4


def rounded_box(length: float, width: float, height: float, radius: float = 2.0,
                top_radius: float = 0.0, bottom_chamfer: float = ELEPHANT_FOOT_CHAMFER) -> Part:
    """Box on the bed with rounded vertical edges, optional rounded top, and a 45° bottom chamfer."""
    part = Box(length, width, height, align=ON_BED)
    if radius > 0:
        part = fillet(part.edges().filter_by(Axis.Z), radius)
    if top_radius > 0:
        part = fillet(part.edges().group_by(Axis.Z)[-1], top_radius)
    if bottom_chamfer > 0:
        part = chamfer(part.edges().group_by(Axis.Z)[0], bottom_chamfer)
    return part


TEARDROP_TIP_ROTATION = {
    ("Y", "+Z"): (0, 0, 0), ("Y", "-Z"): (0, 180, 0), ("Y", "+X"): (0, 90, 0), ("Y", "-X"): (0, -90, 0),
    ("X", "+Z"): (0, 0, 0), ("X", "-Z"): (180, 0, 0), ("X", "-Y"): (90, 0, 0), ("X", "+Y"): (-90, 0, 0),
}


def teardrop_hole(diameter: float, length: float, along: str = "Y", tip: str = "+Z") -> Part:
    """Hole that prints without supports when horizontal. Centered at origin, axis `along`.

    `tip` = the model direction that is UP on the print bed (only differs from +Z with a fixed
    print_orientation, e.g. a part printed on its side).
    """
    r = (diameter + HOLE_COMPENSATION) / 2
    k = r / math.sqrt(2)
    profile = Circle(r) + Polygon((0, 0), (k, k), (0, r * math.sqrt(2)), (-k, k), align=None)
    base_axis = "X" if along == "X" else "Y"
    plane = {"Y": Plane.XZ, "X": Plane.YZ}[base_axis]
    hole = extrude(plane * profile, length / 2, both=True)
    if along == "Z":
        if tip not in ("+X", "-X", "+Y", "-Y"):
            raise ValueError(f"tip {tip!r} must be perpendicular to axis 'Z'")
        hole = Rot(90, 0, 0) * hole  # axis Y -> Z, tip +Z -> -Y
        return Rot(0, 0, {"-Y": 0, "+Y": 180, "+X": 90, "-X": -90}[tip]) * hole
    if (along, tip) not in TEARDROP_TIP_ROTATION:
        raise ValueError(f"tip {tip!r} must be perpendicular to axis {along!r}")
    return Rot(*TEARDROP_TIP_ROTATION[(along, tip)]) * hole


def rib(length: float, height: float, thickness: float) -> Part:
    """Right-triangle gusset in the XZ plane: corner at origin, leg `length` along +X, `height` up +Z."""
    triangle = Polygon((0, 0), (length, 0), (0, height), align=None)
    return extrude(Plane.XZ * triangle, thickness / 2, both=True)


def label(text: str, size: float = 6.0, depth: float = 0.6, font: str = "Arial", bold: bool = True) -> Part:
    """Text solid from z=0 up to `depth`; add to a top face to emboss, subtract (moved down) to engrave."""
    from build123d import FontStyle

    style = FontStyle.BOLD if bold else FontStyle.REGULAR
    return extrude(Text(text, font_size=size, font=font, font_style=style), depth)


def slot(length: float, width: float, depth: float) -> Part:
    """Stadium-shaped slot cutter pointing down from z=0, long axis X (for adjustable mounting)."""
    from build123d import SlotOverall

    return Pos(0, 0, -depth) * extrude(SlotOverall(length, width + HOLE_COMPENSATION), depth)


def at(x: float = 0, y: float = 0, z: float = 0, rx: float = 0, ry: float = 0, rz: float = 0):
    """Location shorthand: `at(10, 0, 5, rz=90) * part`."""
    return Pos(x, y, z) * Rot(rx, ry, rz)
