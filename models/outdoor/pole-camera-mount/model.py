"""pole-camera-mount: trekking-pole clamp with a 1/4"-20 camera stud -> turns the pole into a monopod.

Spec: clamps a trekking-pole shaft of Ø14-18 mm. The pole sits in a bore that runs into a 90° V-block;
an M5 thumb screw (through a captive M5 nut in the opposite wall) pushes the pole into the V, so
every diameter in the range is held on two lines + the screw tip (no ring flex needed).
On the arm next to the pole, a 1/4"-20 hex bolt is pushed up from below into an anti-rotation
hex pocket and sticks out of the top as a camera stud for a ball head / phone clamp.
In-use: pole axis = Z through the origin, stud points up (+Z) at x = STUD_X.

Load: 0.5 kg camera/phone at 150 mm lever. Printed upright (as modelled, layers ⟂ pole) so the clamp
hoop and the screw-thrust wall are loaded along the layers; the camera moment acts on a 30 mm deep
solid block (bending stress across layers ~0.1 MPa), and the bolt head bears on the pocket roof in
compression - the strongest orientation for this part.

Hardware: M5 x 25 thumb screw (or socket screw + printed knob), M5 hex nut,
1/4"-20 x 1" hex bolt (7/16" AF head) as camera stud.
Assumptions: pole shaft round (not tapered at the clamp spot); 1/4"-20 hex head 11.1 mm AF x 4.4 mm;
stud protrudes ~8 mm (typical ball-head thread depth 6-8 mm); stick a thin rubber strip in the V if
the pole finish must not be marked.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[dict(at=(28.0, 0.0, 30.0 + 150.0), grams=500)],
    print_orientation=(0, 0, 0),  # upright: clamp hoop + screw thrust along layers
    supports="auto",
    brim="auto",
)

# Pole + clamp
POLE_D_MAX = 18.0          # largest shaft
POLE_D_MIN = 14.0          # smallest shaft
POLE_CLEAR = 0.6           # diametral slide clearance for the largest shaft
HEIGHT = 30.0              # clamp length along the pole
WALL = 4.0                 # ring wall around the bore (structural >= 2)
# M5 thumb screw + captive nut
SCREW = "M5"
SCREW_CLEAR_D = clearance(5.0, "loose")      # 5.4 mm
NUT_AF = 8.0 + 2 * FIT["slide"]              # 8.5 mm slot width
NUT_H = 4.0 + 2 * FIT["slide"]               # 4.5 mm slot thickness
SCREW_BOSS_X = 21.0                          # outer face of the screw boss (-X)
SCREW_BOSS_W = 16.0
# 1/4"-20 camera stud
STUD_X = 28.0
STUD_CLEAR_D = 6.35 + 2 * FIT["slide"]       # 6.85
STUD_HEAD_AF = 11.11 + 2 * FIT["snug"]       # 11.4 hex pocket across flats
STUD_POCKET_H = 17.0                         # pocket roof height -> ~8 mm stud with a 1" bolt
ARM_W = 26.0
ARM_END = STUD_X + 12.0
EDGE_R = 3.0


def _cavity() -> Part:
    r = (POLE_D_MAX + POLE_CLEAR) / 2
    t = r / math.sqrt(2)                       # tangent points of the 45° V flanks
    apex = r * math.sqrt(2)
    v = Polygon((apex, 0), (t, t), (t, -t), align=None)
    sk = Circle(r) + v
    return extrude(Plane.XY.offset(-1) * sk, HEIGHT + 2)


def build() -> Part:
    r_out = (POLE_D_MAX + POLE_CLEAR) / 2 + WALL
    outline = (
        Circle(r_out + 2)
        + Pos(ARM_END / 2, 0) * Rectangle(ARM_END, ARM_W)
        + Pos(-SCREW_BOSS_X / 2, 0) * Rectangle(SCREW_BOSS_X, SCREW_BOSS_W)
    )
    body = extrude(outline, HEIGHT)
    body = fillet(body.edges().filter_by(Axis.Z), EDGE_R)
    body = chamfer(body.edges().group_by(Axis.Z)[0], 0.4)

    body -= _cavity()

    # M5 thumb-screw hole along X at mid-height, horizontal -> teardrop
    zc = HEIGHT / 2
    body -= Pos(-SCREW_BOSS_X / 2 - 2, 0, zc) * teardrop_hole(SCREW_CLEAR_D, SCREW_BOSS_X + 4, along="X")
    # captive nut slot, dropped in from the top
    nut_x = -(SCREW_BOSS_X + (POLE_D_MAX + POLE_CLEAR) / 2) / 2
    slot_bot = zc - NUT_AF / 2 - 0.3
    body -= Pos(nut_x, 0, slot_bot) * Box(NUT_H, NUT_AF, HEIGHT, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # 1/4"-20 stud: hex head pocket from below + clearance shank up through the top
    body -= Pos(STUD_X, 0, -1) * extrude(RegularPolygon(STUD_HEAD_AF / math.sqrt(3), 6, major_radius=True), STUD_POCKET_H + 1)
    body -= Pos(STUD_X, 0, -1) * Cylinder(STUD_CLEAR_D / 2, HEIGHT + 2, align=ON_BED)
    # 45° conical roof instead of a flat bridge; the head corners seat on the cone
    r_hex = STUD_HEAD_AF / math.sqrt(3) + 0.1
    body -= Pos(STUD_X, 0, STUD_POCKET_H) * Cone(r_hex, STUD_CLEAR_D / 2 - 0.5, r_hex - STUD_CLEAR_D / 2 + 0.5,
                                               align=(Align.CENTER, Align.CENTER, Align.MIN))
    return body
