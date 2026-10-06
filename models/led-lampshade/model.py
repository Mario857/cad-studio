"""led-lampshade: geometric faceted pendant lampshade for an E27 lamp holder.

Spec:
- Pendant shade, 200 mm across the widest facet ring, ~146 mm tall, open at the bottom.
- 12-sided antiprism-style faceting: each ring of vertices is rotated half a step against the
  next, so every band is made of flat triangles (geometric look).
- Top flange (ID 42 mm, param) clamps between the E27 holder collar and its shade ring nut.
- Ventilation: a ring of 12 radial slots through the upper cone around the top flange so
  warm air escapes upward.
- Walls ~1.4 mm (spec 1.2-1.6 mm); flange 3 mm thick.

USE LED BULBS ONLY (<= 10 W). ABS softens near 90 degC: never fit an incandescent or halogen
bulb. Keep the bulb glass >= 25 mm from the shade wall (the 200 mm shade gives far more).

Printing: printed upside down (flange on the bed). Every facet then leans outward at <= ~40 deg
from vertical and the vent slots are vertical prisms, so it prints with zero supports.

Assumptions:
- E27 shade ring thread ~40 mm; a 42 mm hole fits standard E27 holders (change TOP_ID).
- Flange outer diameter ~64 mm covers typical E27 shade-ring nuts (~55-60 mm).
- Hanging by the cord/holder only; the shade weight is carried by the flange.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,             # hangs from the E27 holder
    loads=[],
    print_orientation=(180, 0, 0),  # upside down: flange on bed, all facets <= 45 deg
    supports="off",
    brim="auto",
)

# Parameters
TOP_ID = 42.0          # E27 holder hole
FLANGE_T = 3.0         # top flange thickness
WALL = 1.4             # shade wall thickness (1.2-1.6)
SIDES = 12             # facets around
# (z, circumradius) rings of vertices, in-use orientation (bottom rim at z=0)
RINGS = [
    (0.0, 89.0),
    (40.0, 103.0),
    (70.0, 100.0),
    (108.0, 67.0),
    (146.0, 33.0),
]
# ventilation slots around the top ring
VENT_N = 12
VENT_R = 47.0          # slot center radius
VENT_LEN = 14.0        # radial length
VENT_W = 6.0


def _ring(z, r, k):
    off = (k % 2) * math.pi / SIDES
    return [
        Vector(r * math.cos(2 * math.pi * i / SIDES + off),
               r * math.sin(2 * math.pi * i / SIDES + off), z)
        for i in range(SIDES)
    ]


def _tri(a, b, c):
    return Face(Wire.make_polygon([a, b, c], close=True))


def _faceted_solid(rings):
    pts = [_ring(z, r, k) for k, (z, r) in enumerate(rings)]
    faces = []
    for k in range(len(pts) - 1):
        a, b = pts[k], pts[k + 1]
        for i in range(SIDES):
            j = (i + 1) % SIDES
            if k % 2 == 0:   # upper ring rotated +half step
                faces.append(_tri(a[i], a[j], b[i]))
                faces.append(_tri(b[i], a[j], b[j]))
            else:            # lower ring rotated +half step
                faces.append(_tri(a[i], b[j], b[i]))
                faces.append(_tri(a[i], a[j], b[j]))
    faces.append(Face(Wire.make_polygon(pts[0], close=True)))
    faces.append(Face(Wire.make_polygon(pts[-1], close=True)))
    return Solid(Shell(faces)).clean()


def build() -> Part:
    outer = _faceted_solid(RINGS)
    top = outer.faces().sort_by(Axis.Z)[-1]
    bottom = outer.faces().sort_by(Axis.Z)[0]
    shade = offset(outer, -WALL, openings=[top, bottom])

    h = RINGS[-1][0]
    r_top = RINGS[-1][1] * math.cos(math.pi / SIDES)
    flange = Pos(0, 0, h - FLANGE_T) * Cylinder(r_top, FLANGE_T, align=ON_BED)
    part = shade + flange
    part -= Pos(0, 0, h - FLANGE_T - 1) * Cylinder(TOP_ID / 2, FLANGE_T + 2, align=ON_BED)

    cut_h = 60.0
    vent = Pos(0, 0, h + 1 - cut_h) * extrude(SlotOverall(VENT_LEN, VENT_W), cut_h)
    for i in range(VENT_N):
        ang = 360 * (i + 0.5) / VENT_N
        part -= Rot(0, 0, ang) * Pos(VENT_R, 0, 0) * vent
    return part
