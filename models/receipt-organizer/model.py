"""receipt-organizer: slanted desk organizer with 12 monthly slots (JAN-DEC) for folded A5 receipts.

Spec: 13 back-leaning dividers (TILT from vertical) form 12 slots for A5 sheets folded in half
(148 x 105 mm, standing on the 148 edge). Divider heights step up front-to-back so every slot is
visible. A stepped label column on the left carries a raised month label on each riser; a matching
stepped side wall closes the right side. Wide base extends behind the tallest divider for stability.

Assumptions: folded A5 = 148 x 105 mm; up to SLOT_T of receipts per month.
MEASURE BEFORE PRINTING: folded receipt width (A5 short side 148 mm) and stack thickness.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 20, 50), grams=400)],   # ~12 x 30 g of receipts, biased to the back
    print_orientation="auto",
    supports="off",          # only raised-text letter undersides (0.6 mm) flag; they print fine
    brim="on",               # ABS, ~175 x 190 mm flat base
)

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

# Receipts / fits
PAPER_W = 148.0          # folded A5 width (standing edge)
PAPER_CLEAR = 2.0        # per side
SLOT_T = 10.0            # slot thickness (receipt stack)

# Structure
DIV_T = 2.4
BASE_T = 3.0
WALL = 3.0
TILT = 12.0              # degrees back from vertical
H0 = 30.0                # front divider height above base
STEP = 6.5               # height step per divider
LBL_W = 20.0             # label column width
TEXT_SIZE = 5.0
TEXT_DEPTH = 0.6
FRONT_MARGIN = 4.0
BACK_MARGIN = 8.0

N = len(MONTHS)
IN_W = PAPER_W + 2 * PAPER_CLEAR
PITCH = SLOT_T + DIV_T


def build() -> Part:
    s = math.sin(math.radians(TILT))
    y0 = 0.0
    ys = [y0 + i * PITCH for i in range(N + 1)]                  # divider base centres
    hs = [H0 + i * STEP for i in range(N + 1)]                   # heights above base
    tys = [y + h * s for y, h in zip(ys, hs)]                    # divider top centres
    y_front = ys[0] - DIV_T - FRONT_MARGIN
    y_back = tys[-1] + DIV_T + BACK_MARGIN
    depth = y_back - y_front
    x_left = -IN_W / 2 - LBL_W
    x_right = IN_W / 2 + WALL
    width = x_right - x_left

    base = Pos((x_left + x_right) / 2, (y_front + y_back) / 2, 0) * rounded_box(width, depth, BASE_T, radius=4)

    # stepped side profile (Y, Z): riser i at tys[i] from hs[i] to hs[i+1]
    pts = [(y_front + 2, 0), (y_front + 2, BASE_T + hs[0]), (tys[0], BASE_T + hs[0])]
    for i in range(N):
        pts += [(tys[i], BASE_T + hs[i + 1]), (tys[i + 1], BASE_T + hs[i + 1])]
    pts += [(y_back - 2, BASE_T + hs[-1]), (y_back - 2, 0)]
    prof = Polygon(*pts, align=None)
    left = Pos(x_left + LBL_W, 0, 0) * extrude(Plane.YZ * prof, LBL_W - 2)  # extrudes toward -X
    right = Pos(IN_W / 2 + WALL, 0, 0) * extrude(Plane.YZ * prof, WALL + 1)
    part = base + left + right

    for y, h in zip(ys, hs):
        d = Box(IN_W + 2, DIV_T, h + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
        part += Pos(0, y, BASE_T - 0.5) * Rot(-TILT, 0, 0) * d

    for i, m in enumerate(MONTHS):
        z = BASE_T + (hs[i] + hs[i + 1]) / 2
        txt = label(m, size=TEXT_SIZE, depth=TEXT_DEPTH + 0.4)
        part += Pos(x_left + 1 + LBL_W / 2, tys[i] + 0.4, z) * Rot(90, 0, 0) * txt
    return part
