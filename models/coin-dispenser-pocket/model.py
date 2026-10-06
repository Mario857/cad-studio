"""coin-dispenser-pocket: slim pocket dispenser for €1 and €2 coins, no metal spring.

Spec: two side-by-side coin columns (€2 left, €1 right) holding COUNT coins each.
Load: press coins in from the top past two flex fingers per column (outer side + front),
each with a 45° lead-in lip. Dispense: hold it upright, put your thumb on the bottom coin
through the floor window and slide it out sideways through the front exit slot (exactly
one coin high, so the coin above stays). Retention: the floor at the exit is a cantilever
tongue with a small bump the coin must push down, so coins don't slip out in a pocket.
Labels engraved on the top face behind the columns.

Fits: bore = coin Ø + BORE_CLEAR; exit slot height = coin t + BUMP_H + SLOT_CLEAR (< 2 coins);
finger lip LIP = 0.5 mm per side.

MEASURE BEFORE PRINTING (calipers, Ø / thickness mm): €1 23.25/2.33, €2 25.75/2.20.

Assumptions: COUNT = 8 coins per column (€24 total); flex parts sized for ABS (<1 % strain).
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",       # only 'support' = the exit-slot lintels: 24-26 mm bridges over a
                          # 3 mm slot, anchored on both side walls; they bridge cleanly
    brim="auto",
)

COINS = [("€2", 25.75, 2.20), ("€1", 23.25, 2.33)]   # left, right
COUNT = 8
BORE_CLEAR = 0.6
WALL = 1.6
FLOOR = 1.6
LABEL_W = 8.0          # solid strip behind the columns for the labels
TOP_EXTRA = 2.0        # space above the stack (lip + loading)
LIP = 0.5              # finger lip, radial
FINGER_L = 12.0        # flex finger length from the top
FINGER_W = 10.0
SLIT = 0.8
BUMP_H = 0.5
SLOT_CLEAR = 0.4
TONGUE_W = 10.0
TONGUE_L = 12.0
THUMB_W = 12.0         # floor thumb window
TEXT_SIZE = 5.0
TEXT_DEPTH = 0.6


def build() -> Part:
    bores = [d + BORE_CLEAR for _, d, _ in COINS]
    h = FLOOR + COUNT * max(t for *_, t in COINS) + TOP_EXTRA + 1.0
    W = bores[0] + bores[1] + 3 * WALL
    D = max(bores) + 2 * WALL + LABEL_W
    xs = [-W / 2 + WALL + bores[0] / 2, W / 2 - WALL - bores[1] / 2]
    ycs = [-D / 2 + WALL + b / 2 for b in bores]          # front walls flush, WALL thick
    body = Pos(0, 0, 0) * rounded_box(W, D, h, radius=6)
    body = fillet(body.edges().group_by(Axis.Z)[-1], 1.5)

    cuts = []
    for (name, d, t), b, x, side, yc in zip(COINS, bores, xs, (-1, 1), ycs):
        r = b / 2
        cuts.append(Pos(x, yc, FLOOR) * Cylinder(r, h, align=ON_BED))
        # front exit slot, one coin high
        sh = t + BUMP_H + SLOT_CLEAR
        cuts.append(Pos(x, yc - r, FLOOR) * Box(b, b, sh, align=ON_BED))
        # thumb window in the floor (rear half)
        cuts.append(
            Pos(x, yc + r * 0.35, -1) * extrude(Rot(0, 0, 90) * SlotOverall(r * 1.1, THUMB_W), FLOOR + 2))
        # floor tongue at the exit: U-slit
        y0 = -D / 2
        for dx in (-1, 1):
            cuts.append(Pos(x + dx * (TONGUE_W / 2 + SLIT / 2), y0 - 1, -1)
                        * Box(SLIT, TONGUE_L + 1, FLOOR + 2, align=(Align.CENTER, Align.MIN, Align.MIN)))
        # flex fingers at the top: outer side (x) and front (-y)
        for ang in ((180 if side < 0 else 0), 270):
            fz = h - FINGER_L
            for s in (-1, 1):
                cuts.append(Pos(x, yc, fz) * Rot(0, 0, ang) * Pos(r - 3, s * (FINGER_W / 2 + SLIT / 2), 0)
                            * Box(WALL + 8, SLIT, FINGER_L + 1, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        # label
        tx = Text(name, font_size=TEXT_SIZE, font_style=FontStyle.BOLD)
        cuts.append(Pos(x, D / 2 - LABEL_W / 2 - 0.5, h - TEXT_DEPTH) * extrude(tx, 2))
    body -= Part() + cuts

    adds = []
    for (name, d, t), b, x, side, yc in zip(COINS, bores, xs, (-1, 1), ycs):
        r = b / 2
        # finger lips: 45° lead-in on top, 45° underside
        for ang in ((180 if side < 0 else 0), 270):
            prof = Polygon((r + 0.01, h - 1.0 - 2 * LIP), (r - LIP, h - 1.0 - LIP), (r + 0.01, h - 1.0), align=None)
            lip = revolve(Plane.XZ * prof, Axis.Z, 360) & Pos(r, 0, h / 2) * Box(2 * r, FINGER_W, h)
            adds.append(Pos(x, yc, 0) * Rot(0, 0, ang) * lip)
        # retention bump on the tongue tip, ramped both ways
        y0 = -D / 2
        bump = extrude(Plane.YZ * Polygon((0, 0), (2 * BUMP_H, 0), (BUMP_H, BUMP_H), align=None),
                       TONGUE_W / 2 - 0.5, both=True)
        adds.append(Pos(x, y0 + WALL + 1.0, FLOOR) * bump)
    body += Part() + adds
    return body
