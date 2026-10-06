"""jar-opener: under-cabinet V-grip jar opener for 40-90 mm lids.

Spec: 160 x 130 x 5 mm plate screwed up under a wall cabinet/shelf (4 x countersunk
4 mm wood screws). Below it hang two 8 mm toothed jaws forming a V, 104 mm wide at the
front and 30 mm at the back: push the lid into the V until it wedges, then turn the jar
counter-clockwise (either way works - teeth are symmetric). Lid grip depth 22 mm.
Printed upside down (plate on the bed): jaws grow straight up, no supports.
Assumptions: cabinet bottom >= 15 mm thick (screw length 16 mm); lids 40-90 mm diameter
and >= 6 mm tall; jar torque ~5 N.m is resisted by the 4 screws.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[],
    print_orientation=(180, 0, 0),
    supports="auto",
    brim="auto",
)

# Parameters
PLATE_L = 160.0        # X
PLATE_W = 130.0        # Y
PLATE_T = 5.0
JAW_H = 22.0           # grip depth below the plate
JAW_T = 8.0
V_FRONT_W = 104.0      # inner width at the front (fits 90 mm lid)
V_BACK_W = 30.0        # inner width at the back (stops 40 mm lid)
V_Y0 = -60.0           # front of jaws
V_Y1 = 45.0            # back of jaws
BACK_T = 8.0
TOOTH_H = 1.5
TOOTH_P = 5.0
CORNER_R = 8.0
SCREW = "M4"
SCREW_XY = ((-70, -52), (70, -52), (-70, 55), (70, 55))


def _jaw(sign: float) -> Face:
    """Toothed jaw polygon for one side (sign -1 left, +1 right)."""
    p0 = (sign * V_FRONT_W / 2, V_Y0)
    p1 = (sign * V_BACK_W / 2, V_Y1)
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    ln = math.hypot(dx, dy)
    ux, uy = dx / ln, dy / ln
    nx, ny = (uy, -ux) if sign < 0 else (-uy, ux)  # inward normal (toward x=0)
    pts = [(p0[0] - nx * JAW_T, p0[1] - ny * JAW_T), (p1[0] - nx * JAW_T, p1[1] - ny * JAW_T)]
    n = int(ln // TOOTH_P)
    for i in range(n, -1, -1):
        t = i * TOOTH_P
        pts.append((p0[0] + ux * t, p0[1] + uy * t))
        if i > 0:
            tm = t - TOOTH_P / 2
            pts.append((p0[0] + ux * tm + nx * TOOTH_H, p0[1] + uy * tm + ny * TOOTH_H))
    return Polygon(*pts, align=None)


def build() -> Part:
    plate = Pos(0, 0, JAW_H) * Box(PLATE_L, PLATE_W, PLATE_T, align=ON_BED)
    plate = fillet(plate.edges().filter_by(Axis.Z), CORNER_R)
    jaws = [extrude(_jaw(s), JAW_H + 0.5, dir=(0, 0, 1)) for s in (-1, 1)]
    back = Pos(0, V_Y1 + BACK_T / 2 - 1, 0) * Box(V_BACK_W + 2 * JAW_T + 6, BACK_T, JAW_H + 0.5,
                                                   align=ON_BED)
    part = plate + jaws[0] + jaws[1] + back
    # countersunk screws: head on the visible (lower) face of the plate, shank going up
    for x, y in SCREW_XY:
        part -= Pos(x, y, JAW_H) * Rot(180, 0, 0) * bolt_hole(SCREW, PLATE_T + 1, head="csk")
    # 0.4 mm chamfer on the plate's top face (bed side when printed flipped)
    part = chamfer(part.edges().group_by(Axis.Z)[-1], 0.4)
    return part
