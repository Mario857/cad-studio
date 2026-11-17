"""travel-laptop-stand-joint-coupon: cut-down test of the stand's two unproven joints (print before the stand).

Why: the stand is a HIGH first-print risk (3 h, 123 g) and two of its fits are not print-proven.
Three pieces, same material and settings as the stand, each printed the way the stand prints it:
  1. Socket strip: three square sockets for the 10 mm spreader tenon, numbered
       1 = 10.2 (press)   2 = 10.3 (snug, what the stand uses)   3 = 10.5 (slide)
     Sockets are vertical, as in the stand's feet (12 mm deep here, 20 mm in the stand).
  2. Tenon stub: a 10 x 10 double-ended tenon with the stand's tip and bed-edge chamfers, printed lying
     down like the spreaders.
  3. Pivot plate, 10 mm like the bars: one 5.3 bore with the countersink on the bed face (bar B), one
     5.3 bore with the M5 nut pocket on the top face (bar A).
How to use: push the stub into each socket by hand. Wanted: goes in with a firm push, does not rock, and
  pulls out again. Report the number. Then try the hardware: the countersunk screw head should sit flush,
  the nyloc nut should drop fully into its pocket without turning, the screw should spin in the bore with no rattle.

Dimensions
  tenon 10.0, sockets 10.2 / 10.3 / 10.5     MEASURED (modelled sizes: this coupon is what proves them)
  M5 bore 5.3, countersink 10.4, nut 8.0 AF  MEASURED (standard hardware; keep in sync with travel-laptop-stand)
Assumptions: PETG shrinks the same in the coupon and the stand; the user has M5 x 20 countersunk screws
  and M5 nyloc nuts.
Risks: a short 12 mm socket feels looser than the stand's 20 mm one; judge rocking, not pull-out force.
Accept: one socket number gives a firm, rock-free, removable fit; screw head flush; nut held.
"""

from build123d import *

from cadlib import *

META = dict(
    material="PETG",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="off",
)

TENON = 10.0
FITS = ["press", "snug", "slide"]     # socket 1, 2, 3
PITCH = 18.0
STRIP_W = 24.0
STRIP_H = 12.0
HOLE_Y = 4.0             # socket centre, leaves room for the number
NUM_SIZE = 5.0
NUM_H = 0.6

STUB_L = 20.0            # each tenon end
COLLAR_T = 4.0
COLLAR_W = 16.0
COLLAR_UP = 3.0

PLATE_T = 10.0           # = bar thickness
PIVOT_D = 5.3
CSK_D = 10.4
NUT_DEPTH = 5.5
GAP = 4.0


def socket_strip() -> Part:
    length = PITCH * len(FITS) + 4.0
    part = Box(length, STRIP_W, STRIP_H, align=ON_BED)
    part = fillet(part.edges().filter_by(Axis.Z), 2.0)
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    for i, fit in enumerate(FITS):
        x = (i - (len(FITS) - 1) / 2) * PITCH
        size = clearance(TENON, fit)
        part -= Pos(x, HOLE_Y, STRIP_H / 2) * Box(size, size, STRIP_H + 2)
        text = label(str(i + 1), size=NUM_SIZE, depth=NUM_H)
        box = text.bounding_box()
        part += Pos(x - (box.min.X + box.max.X) / 2, -7.5 - (box.min.Y + box.max.Y) / 2, STRIP_H) * text
    return part


def tenon_stub() -> Part:
    length = 2 * STUB_L + COLLAR_T
    bar = Box(length, TENON, TENON, align=ON_BED)
    bar = chamfer(bar.edges().filter_by(Axis.Y) + bar.edges().filter_by(Axis.Z), 0.6)
    bar = chamfer(bar.edges().filter_by(Axis.X).group_by(Axis.Z)[0], 0.4)
    return bar + Box(COLLAR_T, COLLAR_W, TENON + COLLAR_UP, align=ON_BED)


def pivot_plate() -> Part:
    part = Box(34.0, 16.0, PLATE_T, align=ON_BED)
    part = fillet(part.edges().filter_by(Axis.Z), 2.0)
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    for x in (-8.0, 8.0):
        part -= Pos(x, 0, PLATE_T / 2) * Cylinder(PIVOT_D / 2, PLATE_T + 2)
    part -= Pos(-8.0, 0, PLATE_T) * nut_trap("M5", NUT_DEPTH)            # nut pocket, open to the top
    depth = (CSK_D - PIVOT_D) / 2
    part -= Pos(8.0, 0, depth / 2) * Cone(CSK_D / 2 + 0.01, PIVOT_D / 2, depth + 0.01)   # countersink on the bed face
    return part


def build():
    placed, y = [], 0.0
    for piece in (socket_strip(), tenon_stub(), pivot_plate()):
        box = piece.bounding_box()
        placed.append(Pos(-(box.min.X + box.max.X) / 2, y - box.min.Y, 0) * piece)
        y += box.max.Y - box.min.Y + GAP
    return placed
