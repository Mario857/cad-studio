"""cutting-board-stand: counter stand holding 3 cutting boards upright.

Spec: rounded base plate with 4 dividers forming three 30 mm slots; dividers lean
back 10 deg so boards rest tilted and stay put. Drain holes in each slot floor let
wet boards drip dry. Dividers are tapered (10 -> 5 mm) and filleted at the top.
Assumptions: boards up to 28 mm thick, up to ~45 cm tall and 1 kg each (COM ~180 mm
up); stand placed with the boards' width along X; 0.4 mm chamfer on the base.
"""

import math

from build123d import *

from cadlib import *

# Parameters
N_SLOTS = 3
SLOT_W = 30.0
DIV_BOT = 10.0
DIV_TOP = 5.0
DIV_H = 70.0
LEAN = 10.0              # deg, top of dividers toward +Y
BASE_T = 6.0
LENGTH = 130.0           # along X (board width direction)
CORNER_R = 8.0
MARGIN = 4.0             # base overhang past the outer dividers
DRAIN_D = 6.0
DRAIN_PITCH = 25.0
BOARD_G = 1000

PITCH = SLOT_W + DIV_BOT
DEPTH = N_SLOTS * PITCH + DIV_BOT + 2 * MARGIN
SHIFT = DIV_H * math.tan(math.radians(LEAN))

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, (i - (N_SLOTS - 1) / 2) * PITCH + SHIFT, 180), grams=BOARD_G)
           for i in range(N_SLOTS)],
    print_orientation="auto",
    supports="auto",
    brim="on",               # ABS, 130 x 138 flat base
)


def divider(y0) -> Part:
    pts = [(y0 - DIV_BOT / 2, 0), (y0 + DIV_BOT / 2, 0),
           (y0 + DIV_TOP / 2 + SHIFT, DIV_H), (y0 - DIV_TOP / 2 + SHIFT, DIV_H)]
    d = extrude(Plane.YZ * Polygon(*pts, align=None), (LENGTH - 2 * MARGIN) / 2, both=True)
    return Pos(0, 0, BASE_T - 0.5) * d


def build() -> Part:
    part = rounded_box(LENGTH, DEPTH, BASE_T, radius=CORNER_R)
    y_first = -(N_SLOTS * PITCH) / 2
    for i in range(N_SLOTS + 1):
        part += divider(y_first + i * PITCH)
    try:
        part = fillet(part.edges().group_by(Axis.Z)[-1], DIV_TOP / 2 - 0.3)
    except Exception:
        pass
    n_d = int((LENGTH - 2 * CORNER_R) // DRAIN_PITCH)
    for i in range(N_SLOTS):
        yc = y_first + i * PITCH + PITCH / 2 + 2.0
        for j in range(n_d):
            x = (j - (n_d - 1) / 2) * DRAIN_PITCH
            part -= Pos(x, yc, BASE_T + 1) * pin_hole(DRAIN_D, BASE_T + 2)
    return part
