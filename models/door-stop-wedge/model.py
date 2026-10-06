"""door-stop-wedge: door wedge with grip grooves and a pull hole.

Spec: 120 mm long, 40 mm wide, rising from a 2 mm toe to 25 mm at the heel. Transverse grip
grooves on the sloped top, a 14 mm vertical finger/pull hole near the heel (also hangs on a hook).
Fits under typical interior doors (gap 8-20 mm).
Assumptions: 2 mm toe so the tip prints as a solid wall; prints flat on its base (no supports);
door pushes only on the slope, so layer orientation is irrelevant.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation="auto",
    supports="auto",
    brim="auto",
)

# Parameters
LENGTH = 120.0
WIDTH = 40.0
TOE_H = 2.0
HEEL_H = 25.0
CORNER_R = 4.0
GROOVE_W = 2.0
GROOVE_D = 0.8
GROOVE_PITCH = 6.0
GROOVE_START = 18.0
GROOVE_END = 90.0
PULL_HOLE_D = 14.0
PULL_HOLE_X = 106.0


def build() -> Part:
    profile = Polygon((0, 0), (LENGTH, 0), (LENGTH, HEEL_H), (0, TOE_H), align=None)
    part = extrude(Plane.XZ * profile, WIDTH / 2, both=True)
    part = fillet(part.edges().filter_by(Axis.Z), CORNER_R)
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)

    slope = math.atan2(HEEL_H - TOE_H, LENGTH)
    x = GROOVE_START
    while x <= GROOVE_END:
        z = TOE_H + x * math.tan(slope)
        groove = Box(GROOVE_W, WIDTH + 2, GROOVE_D * 2)
        part -= Pos(x, 0, z) * Rot(0, -math.degrees(slope), 0) * groove
        x += GROOVE_PITCH

    part -= Pos(PULL_HOLE_X, 0, -1) * Cylinder(PULL_HOLE_D / 2, HEEL_H + 2, align=ON_BED)
    return part
