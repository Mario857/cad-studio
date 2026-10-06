"""coin-ramp-sorter: gravity ramp that sorts mixed euro coins into 8 labelled bins.

Spec: two parts. (1) Bin box, 290 x 70 mm, 8 compartments in a row; its top is cut on a
plane sloping RAMP_ANGLE (10°) down along +X and CROSS_ANGLE toward the guide rail (-Y),
with a LIP of outer wall standing above that plane. (2) Ramp plate (printed flat) that drops
inside the lip and rests on the dividers: a guide rail along -Y, a front lip, a back stop
at the high end and 7 slots against the rail whose width (measured from the rail) grows
toward the low end. Coins poured at the top slide/roll down against the rail; each falls
through the first slot wider than itself into its bin; €2 coins run off the end into bin 8.
Bin order (high -> low end): 1c, 2c, 10c, 5c, 20c, €1, 50c, €2. Denomination engraved
beside each slot.

Slot width = coin Ø + SLOT_MARGIN (0.5 mm): passes its own coin, still 0.5 mm narrower than
the next-larger coin (closest pairs differ by 1.0 mm). Slot length along travel = Ø + 4.

MEASURE BEFORE PRINTING (coin Ø mm): 1c 16.25, 2c 18.75, 5c 21.25, 10c 19.75, 20c 22.25,
50c 24.25, €1 23.25, €2 25.75.

Assumptions: coins slide on ABS at 10° once moving — pour them in and give the box a light
shake/tap; raise RAMP_ANGLE if your coins stall. Both parts on one plate (in-use: lift the
plate into the lip of the box).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="on",              # long flat ABS parts
    # 2 bodies intended: bin box + ramp plate
)

# sorted smallest -> largest: (label, Ø)
COINS = [("1c", 16.25), ("2c", 18.75), ("10c", 19.75), ("5c", 21.25),
         ("20c", 22.25), ("€1", 23.25), ("50c", 24.25), ("€2", 25.75)]
SLOT_MARGIN = 0.5
SLOT_EXTRA_LEN = 4.0
RAMP_ANGLE = 10.0
CROSS_ANGLE = 8.0
BOX_L = 290.0
BOX_W = 70.0
WALL = 2.4
DIV = 2.0              # bin divider thickness
FLOOR = 2.0
MIN_DEPTH = 26.0       # bin depth at the low/rail corner
LIP = 6.0              # outer wall above the ramp plane
PLATE_T = 3.0
PLATE_CLEAR = 0.5      # gap plate <-> lip, each side
RAIL_T = 3.0
RAIL_H = 12.0
FRONT_LIP_H = 6.0
TEXT_SIZE = 6.0
TEXT_DEPTH = 0.6
PRINT_GAP = 8.0


def build():
    a, c = math.radians(RAMP_ANGLE), math.radians(CROSS_ANGLE)
    hc = MIN_DEPTH + FLOOR + (BOX_L / 2) * math.tan(a) + (BOX_W / 2) * math.tan(c)
    T = Pos(0, 0, hc) * Rot(CROSS_ANGLE, RAMP_ANGLE, 0)
    hmax = hc + (BOX_L / 2) * math.tan(a) + (BOX_W / 2) * math.tan(c) + LIP + 5

    # --- bin box
    box = rounded_box(BOX_L, BOX_W, hmax, radius=4)
    box -= T * Pos(0, 0, LIP) * Box(2 * BOX_L, 2 * BOX_W, hmax, align=(Align.CENTER, Align.CENTER, Align.MIN))
    inner_l, inner_w = BOX_L - 2 * WALL, BOX_W - 2 * WALL
    box -= (T * Box(2 * BOX_L, 2 * BOX_W, hmax, align=(Align.CENTER, Align.CENTER, Align.MIN))) & \
        Box(inner_l, inner_w, 2 * hmax, align=ON_BED)
    bw = (inner_l - 7 * DIV) / 8
    x0 = -inner_l / 2
    centers = []
    for k in range(8):
        xs = x0 + k * (bw + DIV)
        centers.append(xs + bw / 2)
        box -= Pos(xs + bw / 2, 0, FLOOR) * Box(bw, inner_w, hmax, align=ON_BED)

    # --- ramp plate, local frame (plane z=0, x downhill, rail at -Y)
    ca, cc = math.cos(a), math.cos(c)
    xa = (x0 + PLATE_CLEAR) / ca
    xb = (x0 + 7 * bw + 7 * DIV) / ca          # ends on divider 7, bin 8 open
    wp = (inner_w - 2 * PLATE_CLEAR) / cc
    plate = Pos((xa + xb) / 2, 0, 0) * Box(xb - xa, wp, PLATE_T, align=ON_BED)
    plate = chamfer(plate.edges().group_by(Axis.Z)[0], 0.4)
    yr = -wp / 2 + RAIL_T                       # rail inner face
    plate += Pos((xa + xb) / 2, -wp / 2 + RAIL_T / 2, 0) * Box(xb - xa, RAIL_T, PLATE_T + RAIL_H, align=ON_BED)
    plate += Pos((xa + xb) / 2, wp / 2 - 1, 0) * Box(xb - xa, 2, PLATE_T + FRONT_LIP_H, align=ON_BED)
    plate += Pos(xa + 1, 0, 0) * Box(2, wp, PLATE_T + RAIL_H, align=ON_BED)
    for k in range(7):
        name, d = COINS[k]
        w = d + SLOT_MARGIN
        ln = d + SLOT_EXTRA_LEN
        xc = centers[k] / ca
        plate -= Pos(xc, yr, -1) * Box(ln, w, PLATE_T + 2, align=(Align.CENTER, Align.MIN, Align.MIN))
        t = Text(name, font_size=TEXT_SIZE, font_style=FontStyle.BOLD)
        plate -= Pos(xc, wp / 2 - 2 - 2 - TEXT_SIZE / 2, PLATE_T - TEXT_DEPTH) * extrude(t, 1)
    t = Text(COINS[7][0], font_size=TEXT_SIZE, font_style=FontStyle.BOLD)
    plate -= Pos(xb - 10, wp / 2 - 4 - TEXT_SIZE / 2, PLATE_T - TEXT_DEPTH) * extrude(t, 1)

    plate = Pos(0, -(BOX_W / 2 + PRINT_GAP + wp / 2), 0) * plate
    return [box, plate]
