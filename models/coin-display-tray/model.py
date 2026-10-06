"""coin-display-tray: collector tray for one country's 8-coin euro set, labelled, with year-card slot.

Spec: 144x100x6 mm tray, two rows of 4 coin recesses (1c..2 EURO), each Ø coin + COIN_CLEAR and
exactly coin-thick deep so coins sit flush; a Ø6 push-out hole under each recess. Denomination
engraved under each coin (5 mm text, 0.6 mm deep). Raised 10 mm ridge along the back with a
1.4 mm slot for a 60 mm wide year / country card standing upright.

MEASURE BEFORE PRINTING (calipers), Ø/thickness mm: 1c 16.25/1.67, 2c 18.75/1.67,
5c 21.25/1.67, 10c 19.75/1.93, 20c 22.25/2.14, 50c 24.25/2.38, €1 23.25/2.33, €2 25.75/2.20.
Assumptions: card <= 1 mm thick, <= 60 mm wide; COIN_CLEAR 0.4 mm on diameter (coins drop in,
push out from below).
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="auto",
)

# Parameters
COINS = [("1 CENT", 16.25, 1.67), ("2 CENT", 18.75, 1.67), ("5 CENT", 21.25, 1.67), ("10 CENT", 19.75, 1.93),
         ("20 CENT", 22.25, 2.14), ("50 CENT", 24.25, 2.38), ("1 EURO", 23.25, 2.33), ("2 EURO", 25.75, 2.20)]
COIN_CLEAR = 0.4         # on diameter
PUSH_D = 6.0             # push-out hole
TRAY_L = 144.0
TRAY_W = 100.0
TRAY_H = 6.0
PITCH_X = 34.0
ROW_Y = (-18.0, 20.0)    # front row, back row coin centres
LABEL_DY = -17.0         # label centre below the coin centre
TEXT_SIZE = 5.0
TEXT_DEPTH = 0.6
RIDGE_H = 10.0           # above the tray top
RIDGE_T = 6.0
CARD_SLOT_W = 1.4
CARD_SLOT_L = 62.0
CARD_SLOT_DEPTH = 12.0   # from the ridge top


def build() -> Part:
    part = rounded_box(TRAY_L, TRAY_W, TRAY_H, radius=6)
    part = fillet(part.edges().group_by(Axis.Z)[-1], 1.0)
    ry = TRAY_W / 2 - RIDGE_T / 2 - 3
    ridge = Pos(0, ry, TRAY_H - 0.5) * Box(CARD_SLOT_L + 16, RIDGE_T, RIDGE_H + 0.5, align=ON_BED)
    ridge = fillet(ridge.edges().group_by(Axis.Z)[-1], 1.5)
    part += ridge
    part -= Pos(0, ry, TRAY_H + RIDGE_H) * Box(CARD_SLOT_L, CARD_SLOT_W, CARD_SLOT_DEPTH, align=(Align.CENTER, Align.CENTER, Align.MAX))

    order = [COINS[4:], COINS[:4]]   # front row: 20c..2E, back row: 1c..10c
    for row, y in zip(order, ROW_Y):
        for i, (txt, d, t) in enumerate(row):
            x = (i - 1.5) * PITCH_X
            part -= Pos(x, y, TRAY_H) * Cylinder((d + COIN_CLEAR) / 2, t, align=(Align.CENTER, Align.CENTER, Align.MAX))
            part -= Pos(x, y, TRAY_H + 1) * Cylinder(PUSH_D / 2, TRAY_H + 2, align=(Align.CENTER, Align.CENTER, Align.MAX))
            part -= Pos(x, y + LABEL_DY, TRAY_H - TEXT_DEPTH) * label(txt, size=TEXT_SIZE, depth=TEXT_DEPTH + 0.5)
    return part
