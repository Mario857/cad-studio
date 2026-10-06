"""receipt-roll-holder: counter holder for a thermal receipt roll on a printed axle, serrated tear bar.

Spec: base plate + two cheeks with open-top U slots; the printed axle drops into the slots and
end collars stop it sliding out sideways. Roll (ROLL_W 80 mm, set 57 for narrow rolls; Ø up to
80 mm) spins on the axle. Paper runs forward over a serrated tear bar (3 mm teeth) at the front;
pull down to tear. Axle is printed beside the holder lying flat, with an inverted-teardrop
section so its underside prints without supports (the point rests in the U slot in use).

MEASURE BEFORE PRINTING: roll width (ROLL_W), roll Ø (ROLL_D max 80), core inner Ø (CORE_ID,
assumed 12 mm; axle 10 mm). 
Assumptions: rolls unwind from the top/front; holder on a flat counter (not screwed down).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 0, 50), grams=250)],   # full 80x80 roll
    print_orientation=(0, 0, 0),
    supports="off",
    brim="auto",
)

# Parameters
ROLL_W = 80.0            # 57 or 80
ROLL_D = 80.0
CORE_ID = 12.0
AXLE_D = 10.0            # < CORE_ID
SLOT_CLEAR = 0.6         # U slot width = AXLE_D + clear
SIDE_CLEAR = 2.0         # roll to cheek, per side
CHEEK_T = 4.0
BASE_T = 4.0
FLOOR_GAP = 6.0          # roll to base
CHEEK_FRONT = 52.0       # cheek extent in front of the axle (tear bar)
CHEEK_BACK = 45.0
COLLAR_D = 18.0
COLLAR_T = 3.0
BAR_T = 4.0              # tear bar thickness (Y)
TOOTH_P = 3.0            # tear tooth pitch
TOOTH_H = 2.5


def _teardrop_down(d, length):
    r = d / 2
    k = r / math.sqrt(2)
    prof = Circle(r) + Polygon((0, 0), (k, -k), (0, -r * math.sqrt(2)), (-k, -k), align=None)
    return extrude(Plane.YZ * prof, length / 2, both=True)


def _holder():
    axle_z = BASE_T + FLOOR_GAP + ROLL_D / 2
    inner = ROLL_W + 2 * SIDE_CLEAR
    xc = (inner + CHEEK_T) / 2
    y0, y1 = -CHEEK_FRONT - BAR_T / 2, CHEEK_BACK
    base = Pos(0, (y0 + y1) / 2, 0) * rounded_box(inner + 2 * CHEEK_T, y1 - y0, BASE_T, radius=5)
    cheek_h = axle_z + 12
    part = base
    for sx in (-1, 1):
        ck = Pos(sx * xc, (y0 + y1) / 2, 0) * Box(CHEEK_T, y1 - y0, cheek_h, align=ON_BED)
        ck = fillet(ck.edges().group_by(Axis.Z)[-1].filter_by(Axis.X), 6)
        part += ck
    # U slots (open top, round bottom at the axle centre)
    w = AXLE_D + SLOT_CLEAR
    for sx in (-1, 1):
        slot = Pos(sx * xc, 0, axle_z) * Box(CHEEK_T + 2, w, cheek_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
        slot += Pos(sx * xc, 0, axle_z) * Rot(0, 90, 0) * Cylinder(w / 2, CHEEK_T + 2)
        part -= slot
    # tear bar (front wall) with upward teeth
    bar_z = axle_z - 6
    span = inner + CHEEK_T
    bar = Pos(0, -CHEEK_FRONT, 0) * Box(span, BAR_T, bar_z, align=(Align.CENTER, Align.CENTER, Align.MIN))  # front wall, no bridge
    n = int(inner // TOOTH_P)
    tooth = extrude(Plane.XZ * Polygon((-TOOTH_P / 2, 0), (TOOTH_P / 2, 0), (0, TOOTH_H), align=None), BAR_T / 2, both=True)
    for i in range(n):
        bar += Pos(-(n - 1) * TOOTH_P / 2 + i * TOOTH_P, -CHEEK_FRONT, bar_z - 0.01) * tooth
    part += bar
    return part


def _axle():
    inner = ROLL_W + 2 * SIDE_CLEAR
    span = inner + 2 * CHEEK_T + 1.0           # 0.5 mm end play per side
    rod = _teardrop_down(AXLE_D, span + 2 * COLLAR_T)
    for sx in (-1, 1):
        rod += Pos(sx * (span + COLLAR_T) / 2, 0, 0) * _teardrop_down(COLLAR_D, COLLAR_T)
    zmin = -AXLE_D / 2 * math.sqrt(2) + 1.0     # 1.4 mm flat print strip along the rod tip
    rod &= Pos(0, 0, zmin) * Box(400, 100, 100, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Pos(0, CHEEK_BACK + 25, -zmin) * rod


def build():  # 2 bodies intended: holder + loose axle
    return [_holder(), _axle()]
