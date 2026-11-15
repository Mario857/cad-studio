"""calibration-coupon: ~10 g, ~15 min plate that measures how THIS printer + material prints small features.

Rows (each feature numbered 1..n with a raised label below it, bottom to top as seen from above):
  Row 1 holes (through, modelled with hole_d()):  1=3  2=4  3=5  4=6  5=8  6=10 mm nominal
  Row 2 pegs  (3 mm tall, modelled with wall_t()): 1=3  2=4  3=5  4=6  5=8  6=10 mm nominal
  Row 3 left  thin walls (4 mm tall, 8 mm long):   1=0.4 2=0.8 3=1.2 4=1.6 5=2.0 mm
  Row 3 right overhang ladder (4 mm tall), angle from vertical: 1=30  2=45  3=60 deg (no supports)
  Row 4 bridge ladder (1.2 mm deck), free span:    1=5  2=10  3=15 mm (no supports)

How to use (once per material):
  1. ./cad calibrate                      (creates this model; edit META material= to the filament you load)
  2. ./cad check calibration-coupon       and print the .3mf with that filament.
  3. Measure with calipers: hole diameters, peg diameters, which walls printed solid, the steepest
     overhang / longest bridge without sag.
  4. Record the average error (nominal - measured; positive = hole too small / peg or wall too thin):
       ./cad calibration <material> --hole-offset 0.15 --wall-offset -0.05 --note "Bambu PLA Basic"
     This writes config/calibration.toml; cadlib.hole_d()/clearance()/wall_t() then compensate for that
     material in every model. Values are residuals on top of the current calibration, so they accumulate;
     re-print the coupon after recording to confirm both offsets are near 0 (use --set to overwrite).
Assumptions: 0.4 mm nozzle, draft (0.24 mm) quality, PLA unless META says otherwise.
Intended WARNs: "needs support but supports=off" (overhangs and bridges are what is tested) and thin walls
(the 1.2 mm plate and the 0.4-1.0 mm test walls).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="PLA",            # change to the filament you are calibrating
    quality="draft",           # 0.24 mm layers keep the print short; XY accuracy is unaffected
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="off",
)

DIAMETERS = [3.0, 4.0, 5.0, 6.0, 8.0, 10.0]
WALLS = [0.4, 0.8, 1.2, 1.6, 2.0]
ANGLES = [30.0, 45.0, 60.0]       # overhang from vertical
SPANS = [5.0, 10.0, 15.0]         # bridge free span
PLATE_T = 1.2
PEG_H = 3.0
FEATURE_H = 4.0
WALL_LEN = 8.0
BRIDGE_POST = 4.0
BRIDGE_DECK = 1.2
BRIDGE_W = 8.0
GAP = 3.0
NUM_SIZE = 7.0                    # font size giving ~5 mm digits
NUM_H = 0.6
PLATE_X = 72.0
ROWS_Y = [22.0, 7.0, -8.0, -23.0]
PLATE_Y0, PLATE_Y1 = -36.5, 28.0
LEFT = -PLATE_X / 2 + 5.0
LABEL_DY = -9.5


def num(text, x, y):
    t = label(text, size=NUM_SIZE, depth=NUM_H)
    bb = t.bounding_box()
    return Pos(x - (bb.min.X + bb.max.X) / 2, y - (bb.min.Y + bb.max.Y) / 2, PLATE_T) * t


def centres(widths, x0):
    """Left-to-right centres for features of the given widths."""
    out, x = [], x0
    for w in widths:
        out.append(x + w / 2)
        x += w + GAP
    return out


def build() -> Part:
    plate = rounded_box(PLATE_X, PLATE_Y1 - PLATE_Y0, PLATE_T, radius=3)
    part = Pos(0, (PLATE_Y0 + PLATE_Y1) / 2, 0) * plate
    cuts = []

    for i, (d, x) in enumerate(zip(DIAMETERS, centres(DIAMETERS, LEFT))):
        cuts.append(Pos(x, ROWS_Y[0], -0.1) * Cylinder(hole_d(d) / 2, PLATE_T + 0.2, align=ON_BED))
        part += num(str(i + 1), x, ROWS_Y[0] + LABEL_DY)
        part += Pos(x, ROWS_Y[1], PLATE_T - 0.01) * Cylinder(wall_t(d) / 2, PEG_H, align=ON_BED)
        part += num(str(i + 1), x, ROWS_Y[1] + LABEL_DY)

    y = ROWS_Y[2]
    for i, (t, x) in enumerate(zip(WALLS, centres([6.0] * len(WALLS), LEFT))):
        part += Pos(x, y, PLATE_T - 0.01) * Box(wall_t(t), WALL_LEN, FEATURE_H, align=ON_BED)
        part += num(str(i + 1), x, y + LABEL_DY)
    for i, (a, x) in enumerate(zip(ANGLES, centres([9.0] * len(ANGLES), LEFT + 33.0))):
        w, ext = 2.4, FEATURE_H * math.tan(math.radians(a))
        prof = Polygon((0, 0), (w, 0), (w + ext, FEATURE_H), (0, FEATURE_H), align=None)
        wedge = extrude(Plane.XZ * prof, WALL_LEN / 2, both=True)
        part += Pos(x - 6.0, y, PLATE_T - 0.01) * wedge
        part += num(str(i + 1), x - 3.0, y + LABEL_DY)

    y = ROWS_Y[3]
    x = LEFT
    for i, s in enumerate(SPANS):
        total = 2 * BRIDGE_POST + s
        for px in (x + BRIDGE_POST / 2, x + BRIDGE_POST + s + BRIDGE_POST / 2):
            part += Pos(px, y, PLATE_T - 0.01) * Box(BRIDGE_POST, BRIDGE_W, FEATURE_H, align=ON_BED)
        part += Pos(x + total / 2, y, PLATE_T + FEATURE_H - BRIDGE_DECK) * Box(total, BRIDGE_W, BRIDGE_DECK, align=ON_BED)
        part += num(str(i + 1), x + total / 2, y + LABEL_DY)
        x += total + 6.0

    for cut in cuts:
        part -= cut
    return part
