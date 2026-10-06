"""coin-roll-loader: funnel tube that loads a counted stack into a paper coin wrapper.

Spec: a weighted stand (cup on a wide foot) plus one insert per denomination. Each insert
is a sleeve whose bore holds a pre-formed paper wrapper (wrapper Ø = coin Ø + 0.5 mm);
its top is a 45° funnel that guides coins into the wrapper. The insert stands on the cup
floor, so the wrapper bottom rests on the floor while you pour. Insert length = full roll
height + funnel, so coins level with the funnel throat = full roll (1c/2c/5c x50,
10c/20c/50c x40, €1/€2 x25). A full-length side slot lets you push the filled wrapper out.
Denomination engraved on each insert.

Fits: wrapper Ø = coin + WRAP_EXTRA (0.5); insert bore = wrapper Ø + 2 x PAPER_T + BORE_FIT;
stand bore = INSERT_OD + CUP_FIT.

MEASURE BEFORE PRINTING (calipers, Ø / thickness mm): 1c 16.25/1.67, 2c 18.75/1.67,
5c 21.25/1.67, 10c 19.75/1.93, 20c 22.25/2.14, 50c 24.25/2.38, €1 23.25/2.33, €2 25.75/2.20;
also your wrapper paper thickness (PAPER_T).

Assumptions: pre-formed (tube) wrappers, paper 0.15 mm; open-ended wrappers get their
bottom folded after removal; all 9 parts on one plate.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="auto",
    # 9 bodies intended: stand + 8 inserts; the ~1 cm2 "support" is the letter ceilings
    # of the engraved side labels (short bridges)
)

# (label, Ø, thickness, coins per roll)
COINS = [
    ("1c", 16.25, 1.67, 50), ("2c", 18.75, 1.67, 50), ("5c", 21.25, 1.67, 50),
    ("10c", 19.75, 1.93, 40), ("20c", 22.25, 2.14, 40), ("50c", 24.25, 2.38, 40),
    ("€1", 23.25, 2.33, 25), ("€2", 25.75, 2.20, 25),
]
WRAP_EXTRA = 0.5       # wrapper Ø = coin Ø + this
PAPER_T = 0.15
BORE_FIT = 0.4         # wrapper slides in/out freely
INSERT_OD = 34.0
CUP_FIT = 0.6          # diametral clearance insert <-> stand cup
FUNNEL_H = 8.0
RIM = 1.2              # wall at the funnel lip
HEADROOM = 2.0
SLOT_W = 9.0           # push-out slot
SLOT_BOTTOM = 0.0
TEXT_SIZE = 6.0
TEXT_DEPTH = 0.6
CUP_WALL = 2.4
CUP_DEPTH = 40.0
CUP_FLOOR = 3.0
FOOT_D = 70.0
FOOT_H = 4.0
GRID = 76.0


def insert(name, d, t, n) -> Part:
    bore = d + WRAP_EXTRA + 2 * PAPER_T + BORE_FIT
    stack = t * n
    L = stack + HEADROOM + FUNNEL_H
    r = INSERT_OD / 2
    prof = Polygon((bore / 2, 0), (r - 0.4, 0), (r, 0.4), (r, L), (r - RIM, L),
                   (bore / 2, L - FUNNEL_H), align=None)
    body = revolve(Plane.XZ * prof, Axis.Z, 360)
    top = L - FUNNEL_H - SLOT_W / 2 - 1
    body -= Pos(0, r, -1) * Box(SLOT_W, INSERT_OD, top + 1, align=ON_BED)
    body -= Pos(0, r, top) * Rot(0, 45, 0) * Box(SLOT_W / 1.4142, INSERT_OD, SLOT_W / 1.4142)  # 45° gable
    sag = r - (r * r - 12.0 ** 2 / 4) ** 0.5
    txt = Rot(0, 0, 90) * Text(name, font_size=TEXT_SIZE, font_style=FontStyle.BOLD)
    body -= extrude(Plane.XZ.offset(r - TEXT_DEPTH - sag) * Pos(0, L * 0.45) * txt, 3)
    return body


def stand() -> Part:
    cup_od = INSERT_OD + CUP_FIT + 2 * CUP_WALL
    s = Cylinder(FOOT_D / 2, FOOT_H, align=ON_BED)
    s = chamfer(s.edges().group_by(Axis.Z)[0], 0.4)
    s = fillet(s.edges().group_by(Axis.Z)[-1], 2.0)
    s += Cylinder(cup_od / 2, CUP_FLOOR + CUP_DEPTH, align=ON_BED)
    s -= Pos(0, 0, CUP_FLOOR) * Cylinder((INSERT_OD + CUP_FIT) / 2, CUP_DEPTH + 1, align=ON_BED)
    return s


def build():
    parts = [stand()]
    for i, c in enumerate(COINS):
        k = i + 1
        parts.append(Pos((k % 3 - 1) * GRID, (k // 3 - 1) * GRID, 0) * insert(*c))
    parts[0] = Pos(-GRID, -GRID, 0) * parts[0]
    return parts
