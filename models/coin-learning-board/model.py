"""coin-learning-board: kids' euro coin board — 8 coin recesses with values + 'make €1' wells.

Spec: 220 x 150 x 6 mm board. Top row: a recess for each euro coin (1c ... €2), sized to the
coin + clearance and as deep as the coin, with a finger notch to lift it out and the value
engraved underneath (7 mm text, 0.6 mm deep). Bottom half: "MAKE €1" header and three 60 mm
practice wells (4 mm deep) where kids lay out coin combinations that add up to €1.
Prints flat, face up, no supports.

MEASURE BEFORE PRINTING: euro coin diameter/thickness (COINS table): 1c 16.25/1.67,
2c 18.75/1.67, 5c 21.25/1.67, 10c 19.75/1.93, 20c 22.25/2.14, 50c 24.25/2.38,
€1 23.25/2.33, €2 25.75/2.20.
Assumptions: COIN_CLEAR 0.5 mm diametral lets coins drop in without sticking.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation="auto",
    supports="off",
    brim="on",                 # 220 x 150 flat ABS board
)

# (label, diameter, thickness)
COINS = [("1c", 16.25, 1.67), ("2c", 18.75, 1.67), ("5c", 21.25, 1.67), ("10c", 19.75, 1.93),
         ("20c", 22.25, 2.14), ("50c", 24.25, 2.38), ("€1", 23.25, 2.33), ("€2", 25.75, 2.20)]

# Board
L = 220.0
W = 150.0
T = 6.0
CORNER_R = 8.0
TOP_FILLET = 1.5

# Coin recesses
COIN_CLEAR = 0.5            # diametral
COIN_ROW_Y = 45.0
COIN_GAP = 4.6              # edge-to-edge between recesses
NOTCH_D = 10.0              # finger notch
NOTCH_EXTRA = 0.6           # notch deeper than the recess

# Text
TEXT_SIZE = 7.0
ENGRAVE = 0.6
LABEL_DY = 22.0             # label centre below the coin row centre
HEADER = "MAKE €1"
HEADER_Y = 2.0
HEADER_SIZE = 9.0

# Practice wells
WELL_D = 60.0
WELL_DEPTH = 4.0
WELL_Y = -38.0
WELL_DX = 70.0
WELL_CHAMFER = 1.0


def engraved(txt, x, y, size=TEXT_SIZE):
    t = label(txt, size=size, depth=ENGRAVE + 1)
    bb = t.bounding_box()
    return Pos(x - (bb.min.X + bb.max.X) / 2, y - (bb.min.Y + bb.max.Y) / 2, T - ENGRAVE) * t


def build():
    board = extrude(RectangleRounded(L, W, CORNER_R), T)
    board = chamfer(board.edges().group_by(Axis.Z)[0], 0.4)
    board = fillet(board.edges().group_by(Axis.Z)[-1], TOP_FILLET)

    total = sum(d + COIN_CLEAR for _, d, _ in COINS) + COIN_GAP * (len(COINS) - 1)
    x = -total / 2
    for name, d, t in COINS:
        r = (d + COIN_CLEAR) / 2
        cx = x + r
        board -= Pos(cx, COIN_ROW_Y, T - t) * Cylinder(r, t + 1, align=ON_BED)
        board -= Pos(cx, COIN_ROW_Y + r - 1.5, T - t - NOTCH_EXTRA) * Cylinder(NOTCH_D / 2, t + NOTCH_EXTRA + 1, align=ON_BED)
        board -= engraved(name, cx, COIN_ROW_Y - LABEL_DY)
        x += 2 * r + COIN_GAP

    board -= engraved(HEADER, 0, HEADER_Y, HEADER_SIZE)
    for i in (-1, 0, 1):
        well = Cylinder(WELL_D / 2, WELL_DEPTH + 1, align=ON_BED)
        well += Pos(0, 0, WELL_DEPTH - WELL_CHAMFER) * Cone(WELL_D / 2, WELL_D / 2 + WELL_CHAMFER + 1,
                                                          WELL_CHAMFER + 1, align=ON_BED)
        board -= Pos(i * WELL_DX, WELL_Y, T - WELL_DEPTH) * well
    return board
