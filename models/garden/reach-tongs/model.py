"""reach-tongs: 400 mm reach spring tongs for stink bugs on ceilings/curtains.

Spec: one-piece spring tongs, 400 mm long, arms 3.6 mm thick x 16 mm tall, joined by a rounded
spring back at x=0. Squeeze the finger pads (mid-length, outer side) to close the V; each tip has
a half-cup with a 15 mm blind pocket (Z 2..18, bridge 15 mm) so closed tips form a 15 mm x 16 mm
capsule that holds the bug without crushing it. Stiffening rib on the outer side of each arm from
x=90 to x=350 (flex happens in the 3.6 mm spring zone near the back).
Joint choice: 400 mm > 320 mm bed, but the bed diagonal (~438 mm) fits it, so it is ONE PIECE
printed flat on the diagonal (model is pre-rotated 47 deg about Z) -- no dovetail/pin joint needed. Tong width
(~28 mm open) is kept small to fit the diagonal.
Assumptions: ABS+ is rigid, so cups are hard "soft-cup" shapes with generous radii (no TPU
inserts); tip gap at rest 8 mm; 15 mm pocket ceiling is a max-length bridge, hence supports=off WARN accepted; 16 mm tall plane = Z, arms bend in XY (layers along the bend).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="auto",
)

LENGTH = 396.4  # + 3.6 back cap radius = 400 overall
T = 3.6            # arm thickness
H = 16.0           # arm height (Z)
OPEN = 10.0         # tip gap at rest (inner faces)
POCKET_D = 15.0
CUP_WALL = 2.4
CUP_R = POCKET_D / 2 + CUP_WALL
CUP_H = 20.0
RIB_T = 2.4
RIB_X0, RIB_X1 = 90.0, 350.0
PAD_X0, PAD_X1, PAD_T = 170.0, 215.0, 8.0

DIAG = 47.0
XC = LENGTH - CUP_R
ANG = math.degrees(math.atan(OPEN / 2 / XC))


def yin(x):
    return OPEN / 2 * x / XC


def prism(pts):
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1]))
    if area < 0:
        pts = pts[::-1]
    return extrude(Plane.XY * Polygon(*pts, align=None), H)


def strip(x0, x1, off0, off1, s):
    """Prism between inner-face-offset lines (offset from inner face, outward) on side s."""
    pts = [(x0, s * (yin(x0) + off0)), (x1, s * (yin(x1) + off0)),
           (x1, s * (yin(x1) + off1)), (x0, s * (yin(x0) + off1))]
    return prism(pts)


def build() -> Part:
    p = Pos(0, 0, 0) * Cylinder(T, H, align=ON_BED)
    for s in (1, -1):
        p += strip(0, XC, 0, T, s)
        # stiffening rib (tapered ends)
        rib = [(RIB_X0, T), (RIB_X0 + 12, T + RIB_T), (RIB_X1 - 12, T + RIB_T), (RIB_X1, T)]
        pts = [(x, s * (yin(x) + o)) for x, o in rib]
        p += prism(pts)
        # finger pad
        p += strip(PAD_X0, PAD_X1, T, T + PAD_T, s)
        # cup half-cylinder on the outer side of the inner-face plane
        cup = Cylinder(CUP_R, CUP_H, align=ON_BED)
        keep = Pos(0, s * CUP_R / 2, 0) * Box(2 * CUP_R, CUP_R, CUP_H, align=ON_BED)
        p += Pos(XC, s * yin(XC), 0) * Rot(0, 0, s * ANG) * (cup & keep)
    for s in (1, -1):
        p -= Pos(XC, s * yin(XC), 2) * Rot(0, 0, s * ANG) * Cylinder(POCKET_D / 2, CUP_H - 4, align=ON_BED)
    return Rot(0, 0, DIAG) * p  # laid on the bed diagonal (audit fit-check ignores rz)
