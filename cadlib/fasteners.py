"""Metric fastener cutters. Every cutter points down (-Z) from z=0: position it on the surface and subtract."""

from build123d import Align, Cone, Cylinder, Part, Pos, RegularPolygon, extrude

from .fit import HOLE_COMPENSATION

DOWN = (Align.CENTER, Align.CENTER, Align.MAX)

# clearance hole, socket-head diameter/height, countersink diameter, hex nut across-flats/height,
# heat-set insert hole diameter/depth (CNC Kitchen style inserts).
METRIC = {
    "M2":   dict(clear=2.4, head_d=3.8, head_h=2.0, csk_d=4.4, nut_af=4.0, nut_h=1.6, insert_d=3.2, insert_h=3.0),
    "M2.5": dict(clear=2.9, head_d=4.5, head_h=2.5, csk_d=5.5, nut_af=5.0, nut_h=2.0, insert_d=3.6, insert_h=4.0),
    "M3":   dict(clear=3.4, head_d=5.5, head_h=3.0, csk_d=6.3, nut_af=5.5, nut_h=2.4, insert_d=4.0, insert_h=4.0),
    "M4":   dict(clear=4.5, head_d=7.0, head_h=4.0, csk_d=8.4, nut_af=7.0, nut_h=3.2, insert_d=5.6, insert_h=5.0),
    "M5":   dict(clear=5.5, head_d=8.5, head_h=5.0, csk_d=10.4, nut_af=8.0, nut_h=4.0, insert_d=6.4, insert_h=6.0),
    "M6":   dict(clear=6.6, head_d=10.0, head_h=6.0, csk_d=12.6, nut_af=10.0, nut_h=5.0, insert_d=8.0, insert_h=7.0),
    "M8":   dict(clear=8.6, head_d=13.0, head_h=8.0, csk_d=16.6, nut_af=13.0, nut_h=6.5, insert_d=9.7, insert_h=8.0),
}
NUT_CLEARANCE = 0.3


def spec(size: str) -> dict:
    if size not in METRIC:
        raise ValueError(f"unknown fastener {size!r}; options: {', '.join(METRIC)}")
    return METRIC[size]


def bolt_hole(size: str, depth: float, head: str | None = "socket", head_depth: float | None = None) -> Part:
    """Through/blind clearance hole of `depth`; head = 'socket' (counterbore), 'csk' (countersink) or None."""
    s = spec(size)
    cutter = Cylinder(s["clear"] / 2, depth, align=DOWN)
    if head == "socket":
        cutter += Cylinder(s["head_d"] / 2 + 0.3, head_depth or s["head_h"] + 0.2, align=DOWN)
    elif head == "csk":
        sink = (s["csk_d"] - s["clear"]) / 2
        cutter += Cone(s["clear"] / 2, s["csk_d"] / 2, sink, align=DOWN)
    return cutter


def nut_trap(size: str, depth: float | None = None, rotation: float = 0) -> Part:
    """Hex pocket (flats along X by default); add `bolt_hole` for the shank."""
    s = spec(size)
    hexagon = RegularPolygon((s["nut_af"] + NUT_CLEARANCE) / 2, 6, major_radius=False, rotation=rotation)
    return Pos(0, 0, -(depth or s["nut_h"] + 0.3)) * extrude(hexagon, depth or s["nut_h"] + 0.3)


def insert_hole(size: str, depth: float | None = None) -> Part:
    """Blind hole for a heat-set insert, with a small lead-in chamfer and melt overflow room."""
    s = spec(size)
    hole_depth = depth or s["insert_h"] + 1.0
    return (
        Cylinder(s["insert_d"] / 2, hole_depth, align=DOWN)
        + Cone(s["insert_d"] / 2 + 0.4, s["insert_d"] / 2, 0.4, align=DOWN)
    )


def pin_hole(diameter: float, depth: float) -> Part:
    """Vertical hole that prints at `diameter`."""
    return Cylinder((diameter + HOLE_COMPENSATION) / 2, depth, align=DOWN)
