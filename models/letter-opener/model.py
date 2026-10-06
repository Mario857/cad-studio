"""letter-opener: 200 mm plastic letter opener with a slanted slitting edge and ergonomic handle.

Spec: flat blade (flat underside, bevelled top) whose front end has a slanted edge rising to a
blunt rounded tip; all blade edges are bevelled down to EDGE_T (0.8 mm, slits paper, not knife-sharp).
Ergonomic lofted handle: palm swell, finger waist and a small front guard, flat underside, lanyard
hole. Printed flat along its length (fixed orientation) so the layers run along the blade.

Assumptions: used for paper envelopes only; overall length TOTAL_L = 200 mm.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),   # flat on the bed, length along X: layers run along the blade
    supports="off",
    brim="auto",
)

TOTAL_L = 200.0
HANDLE_L = 95.0
BLADE_W = 18.0
BLADE_T = 3.0
EDGE_T = 0.8            # bevelled edge thickness (blunt, safe)
BEVEL_W = 6.0           # bevel width on the top face
SLANT_START = 70.0      # blade x where the slanted slitting edge starts
TIP_Y = 3.0             # tip offset above the blade centre line
LANYARD_D = 5.0

# handle sections: (x, width, height) — x measured from blade root (handle extends to -X)
SECTIONS = [(-HANDLE_L, 12, 7), (-HANDLE_L + 4, 22, 12), (-78, 27, 15), (-55, 28, 16),
            (-32, 21, 13), (-10, 25, 12), (6, 15, 5)]


def make_blade() -> Part:
    blade_l = TOTAL_L - HANDLE_L
    hw = BLADE_W / 2
    pts = [(-8, -hw), (SLANT_START, -hw), (blade_l, TIP_Y - 1.5), (blade_l - 1.5, TIP_Y + 1.5),
           (blade_l - 18, hw), (-8, hw)]                     # counter-clockwise
    blade = extrude(Polygon(*pts, align=None), BLADE_T)
    # bevel: cut a half-space through every outer edge at z = EDGE_T, rising inward to BLADE_T
    tilt = math.degrees(math.atan2(BLADE_T - EDGE_T, BEVEL_W))
    for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
        dx, dy = x2 - x1, y2 - y1
        a = math.degrees(math.atan2(-dy, -dx))            # local +Y -> outward normal
        cut = Rot(-tilt, 0, 0) * Box(400, 400, 50, align=(Align.CENTER, Align.CENTER, Align.MIN))
        blade -= Pos((x1 + x2) / 2, (y1 + y2) / 2, EDGE_T) * Rot(0, 0, a) * cut
    return blade


def make_handle() -> Part:
    secs = []
    for x, w, h in SECTIONS:
        ry = h * 0.6
        secs.append(Plane.YZ.offset(x) * Pos(0, h - ry) * Ellipse(w / 2, ry))
    handle = loft(secs)
    handle &= Box(400, 100, 100, align=ON_BED)
    handle -= Pos(-HANDLE_L + 12, 0, -1) * Cylinder(LANYARD_D / 2, 30, align=ON_BED)
    return handle


def build() -> Part:
    return make_blade() + make_handle()
