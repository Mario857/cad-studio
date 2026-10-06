"""coworking-desk-sign: foldable A-frame desk sign "In a call" / "Free to talk".

Spec: two 90 mm wide x 60 mm tall panels (landscape), 3 mm thick, joined along their 90 mm
edge by a print-in-place PETG living hinge (0.8 mm strip, 12 mm long, on the inner side of the
tent). 'In a call' on one panel's outer face, 'Free to talk' on the other: 6 mm text raised
0.6 mm. Both texts read upright (top toward the hinge) once folded. A separate flat spreader
base frame (printed on the same plate) has two slots the panel feet drop into, fixing the tent
at 55 deg between panels and stopping it from splaying open.

Model is returned in PRINT layout (flat, text up): sign at x<0, spreader base at x>0. The
in-use tent (approx 57 mm tall, feet 65-72 mm apart, standing in an 84 x 99 mm base frame)
is computed in params below; its tip angle is ~55 deg sideways (>> 12 deg).

Assumptions:
- PETG (living hinge would crack in PLA); 0.2 mm layers so the 0.8 mm hinge strip = 4 layers.
  The 0.8 mm hinge strip is intentionally thinner than the 1.2 mm wall rule (it must flex).
- "Folds flat" = the sign opens flat (180 deg) for storage/printing; in use it is folded to
  the 55 deg tent and set into the base frame.
- Hinge bend is assumed circular when computing slot positions; slots have 0.4 mm clearance.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="PETG",
    quality="standard",
    standing=True,             # print layout lies flat; in-use tent stability computed in docstring
    loads=[],
    print_orientation=(0, 0, 0),  # already flat, raised text up
    supports="off",
    brim="auto",
)

# Parameters
PANEL_W = 90.0        # panel width (along hinge, X)
PANEL_H = 60.0        # panel height (Y in print layout)
PANEL_T = 3.0         # panel thickness
HINGE_L = 12.0        # free length of living-hinge strip between panels
HINGE_T = 0.8         # living-hinge strip thickness (4 layers @0.2)
HINGE_INSET = 2.0     # strip inset from panel side edges
TENT_ANGLE = 55.0     # included angle between panels in use (deg)
TEXT_A = "In a call"
TEXT_B = "Free to talk"
TEXT_SIZE = 6.0
TEXT_DEPTH = 0.6
TEXT_OFFSET = 4.0     # text centre shifted from panel centre toward the hinge

BASE_T = 3.0          # spreader frame thickness
SLOT_CLR = 0.4        # clearance each side of slots
OUTER_RAIL = 5.0      # rail width outside slots
INNER_RAIL = 4.0      # rail width inside slots
END_BAR = 4.0         # frame end bar width
CROSS_BAR = 6.0       # centre cross bar width
GAP = 10.0            # spacing between sign and base on the plate

# Derived tent geometry (inner face of panel, hinge bend assumed circular)
HALF = math.radians(TENT_ANGLE / 2)               # panel tilt from vertical
BEND = math.pi - math.radians(TENT_ANGLE)          # total bend of the hinge
R_BEND = HINGE_L / BEND
FOOT_X = R_BEND * math.cos(HALF) + PANEL_H * math.sin(HALF)  # inner foot corner from centre
SLOT_IN = FOOT_X - BASE_T * math.tan(HALF) - SLOT_CLR
SLOT_OUT = (FOOT_X + PANEL_T / math.cos(HALF) + PANEL_T * math.sin(HALF) * math.tan(HALF)
            + SLOT_CLR)
SLOT_LEN = PANEL_W + 2 * SLOT_CLR
BASE_L = SLOT_LEN + 2 * END_BAR
BASE_W = 2 * (SLOT_OUT + OUTER_RAIL)


def _text(s: str, rot: float) -> Part:
    t = label(s, size=TEXT_SIZE, depth=TEXT_DEPTH)
    bb = t.bounding_box()
    t = Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, 0) * t
    return Rot(0, 0, rot) * t


def sign() -> Part:
    cy = HINGE_L / 2 + PANEL_H / 2
    a = Pos(0, -cy, 0) * rounded_box(PANEL_W, PANEL_H, PANEL_T, radius=2)
    b = Pos(0, cy, 0) * rounded_box(PANEL_W, PANEL_H, PANEL_T, radius=2)
    strip = Box(PANEL_W - 2 * HINGE_INSET, HINGE_L + 4, HINGE_T, align=ON_BED)
    ty = HINGE_L / 2 + PANEL_H / 2 - TEXT_OFFSET
    ta = Pos(0, -ty, PANEL_T) * _text(TEXT_A, 0)     # panel A: up = +Y (toward hinge)
    tb = Pos(0, ty, PANEL_T) * _text(TEXT_B, 180)    # panel B: up = -Y (toward hinge)
    return a + b + strip + ta + tb


def base() -> Part:
    frame = rounded_box(BASE_L, BASE_W, BASE_T, radius=3)
    sw = SLOT_OUT - SLOT_IN
    sc = (SLOT_OUT + SLOT_IN) / 2
    for s in (-1, 1):
        frame -= Pos(0, s * sc, -1) * Box(SLOT_LEN, sw, BASE_T + 2, align=ON_BED)
    win_w = 2 * (SLOT_IN - INNER_RAIL)
    win_l = (SLOT_LEN - CROSS_BAR) / 2
    for s in (-1, 1):
        frame -= Pos(s * (CROSS_BAR / 2 + win_l / 2), 0, -1) * Box(
            win_l, win_w, BASE_T + 2, align=ON_BED)
    return frame


def build():
    sx = PANEL_W / 2 + GAP / 2
    bx = BASE_L / 2 + GAP / 2
    return [Pos(-sx, 0, 0) * sign(), Pos(bx, 0, 0) * base()]
