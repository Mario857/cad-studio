"""planting-dibber: 200 mm T-handle dibber with raised 1 cm depth rings and numbers.

Spec: octagonal shaft (26 mm across flats) with a 60 mm tapered point, raised depth rings every
10 mm from the tip (1-15 cm) and raised depth numbers (≥ 5 mm tall) on the top face, a grip
section and a 110 mm T-bar handle. Overall 200 mm. For bulbs (8-15 cm) and seedlings (2-5 cm).
Prints lying on one flat face so the layers run the full length of the tool (strong in bending
when levering in heavy soil); the octagon's 45° faces print without supports. To keep that
face flat the point is lofted with its underside straight, so the tip sits ~10 mm off-centre
toward the flat (unnoticeable in use).
Material: AzureFilm ABS PLUS. ABS+ yellows/embrittles after a season or two in full sun; the
user's "AzureFilm ASA @BBL H2C 0.4 nozzle" preset is the long-life swap (same geometry).

Assumptions:
- Depth is read from the tip; ring N marks N cm.
- Rings are raised 0.6 mm on every face except the flat print face.
- No fits/hardware in this part.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[],
    print_orientation=(90, 0, 0),   # lie on the flat -Y face: layers along the length
    supports="off",
    brim="auto",
    copies=1,
)

LENGTH = 200.0
SHAFT_R = 13.0          # octagon inradius (26 mm across flats)
TIP_R = 2.5
POINT_LEN = 60.0
RING_PITCH = 10.0
RING_COUNT = 15
RING_H = 0.8
RING_W = 1.6
LABEL_SIZE = 7.5        # digit height ~5.3 mm
LABEL_RAISE = 0.6
TBAR_LEN = 110.0
TBAR_R = 12.0           # T-bar octagon inradius
TBAR_END_CHAMFER = 3.0

C8 = 1 / math.cos(math.radians(22.5))


def octagon(r: float, cy: float = 0.0) -> Sketch:
    """Octagon with inradius r, flat faces at ±X/±Y, centre (0, cy)."""
    pts = [(r * C8 * math.cos(math.radians(22.5 + 45 * k)), cy + r * C8 * math.sin(math.radians(22.5 + 45 * k)))
           for k in range(8)]
    return Polygon(*pts, align=None)


def r_at(z: float) -> float:
    return TIP_R + (SHAFT_R - TIP_R) * min(z, POINT_LEN) / POINT_LEN


def cy_at(z: float) -> float:
    return r_at(z) - SHAFT_R          # keeps the -Y face at y = -SHAFT_R


def build() -> Part:
    z_bar = LENGTH - 2 * TBAR_R
    point = loft([Plane.XY * octagon(TIP_R, cy_at(0)), Plane.XY.offset(POINT_LEN) * octagon(SHAFT_R)], ruled=True)
    shaft = Pos(0, 0, POINT_LEN) * extrude(octagon(SHAFT_R), z_bar - POINT_LEN + 1)
    bar = extrude(Plane.YZ * octagon(TBAR_R, 0), TBAR_LEN / 2, both=True)
    bar = chamfer(bar.edges().filter_by(Axis.X, reverse=True), TBAR_END_CHAMFER)
    bar = Pos(0, TBAR_R - SHAFT_R, LENGTH - TBAR_R) * bar
    part = point + shaft + bar

    keep = Pos(0, -SHAFT_R, 0) * Box(80, 80, LENGTH, align=(Align.CENTER, Align.MIN, Align.MIN))
    slope = (SHAFT_R - TIP_R) / POINT_LEN * 2           # top-face rise per mm along the point
    for n in range(1, RING_COUNT + 1):
        z = n * RING_PITCH
        ring = loft([Plane.XY.offset(z - RING_W / 2) * octagon(r_at(z - RING_W / 2) + RING_H, cy_at(z - RING_W / 2)),
                     Plane.XY.offset(z + RING_W / 2) * octagon(r_at(z + RING_W / 2) + RING_H, cy_at(z + RING_W / 2))],
                    ruled=True)
        part += ring & keep
        # number on the top face, just above its ring, upright along the shaft
        zt = z + RING_W / 2 + 0.8 + LABEL_SIZE * 0.35
        s = slope if zt < POINT_LEN else 0.0
        y_top = cy_at(zt) + r_at(zt)
        n_vec = Vector(0, 1, -s).normalized()
        pl = Plane(origin=(0, y_top - 0.05, zt), x_dir=(-1, 0, 0), z_dir=n_vec)
        part += pl * label(str(n), size=LABEL_SIZE, depth=LABEL_RAISE + 0.05)
    return part
