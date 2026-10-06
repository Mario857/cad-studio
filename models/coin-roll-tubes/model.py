"""coin-roll-tubes: rack of 8 tubes, each holding exactly one standard euro coin roll.

Spec: one open-top tube per denomination standing on a common base. Each tube is as tall
as one standard roll (1c/2c/5c x50, 10c/20c/50c x40, €1/€2 x25) plus HEADROOM; a V-groove
fill line sits at exactly one roll height. Denomination and roll value are engraved in the
base in front of each tube. A front finger slot runs the full tube height down to the floor,
so a finger pushes the stack up and out (slot is narrower than every coin, so coins can't
fall out sideways).

MEASURE BEFORE PRINTING (calipers, Ø / thickness mm): 1c 16.25/1.67, 2c 18.75/1.67,
5c 21.25/1.67, 10c 19.75/1.93, 20c 22.25/2.14, 50c 24.25/2.38, €1 23.25/2.33, €2 25.75/2.20.

Assumptions: tube bore = coin Ø + TUBE_CLEAR (0.6 mm -> coins drop freely, stay stacked);
roll height = count x nominal thickness (worn coins stack slightly lower, so the line is a
minimum); single row rack ~ 245 x 50 mm.
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
)

# (label, value text, coin Ø, coin thickness, coins per roll)
COINS = [
    ("1c", "€0.50", 16.25, 1.67, 50), ("2c", "€1", 18.75, 1.67, 50),
    ("5c", "€2.50", 21.25, 1.67, 50), ("10c", "€4", 19.75, 1.93, 40),
    ("20c", "€8", 22.25, 2.14, 40), ("50c", "€20", 24.25, 2.38, 40),
    ("€1", "€25", 23.25, 2.33, 25), ("€2", "€50", 25.75, 2.20, 25),
]
TUBE_CLEAR = 0.6       # bore = coin Ø + this
WALL = 2.0             # tube wall
HEADROOM = 2.0         # tube taller than the roll by this
GAP = 2.0              # gap between neighbouring tube walls
BASE_H = 3.0           # base plate thickness (= tube floor)
BASE_FRONT = 22.0      # label area in front of the tubes
BASE_MARGIN = 3.0
SLOT_W = 8.0           # finger slot width (must be < smallest coin Ø)
GROOVE = 0.7           # fill-line V-groove depth
TEXT_SIZE = 5.0
TEXT_DEPTH = 0.6


def build() -> Part:
    ods = [c[2] + TUBE_CLEAR + 2 * WALL for c in COINS]
    xs, x = [], 0.0
    for i, od in enumerate(ods):
        x += od / 2 if i == 0 else ods[i - 1] / 2 + GAP + od / 2
        xs.append(x)
    shift = (xs[0] - ods[0] / 2 + xs[-1] + ods[-1] / 2) / 2
    xs = [v - shift for v in xs]
    length = xs[-1] + ods[-1] / 2 - xs[0] + ods[0] / 2 + 2 * BASE_MARGIN
    depth = max(ods) + BASE_FRONT + 2 * BASE_MARGIN
    yt = depth / 2 - BASE_MARGIN - max(ods) / 2          # tube centre line
    part = rounded_box(length, depth, BASE_H, radius=4)

    cuts = []
    for (name, value, d, t, n), od, xc in zip(COINS, ods, xs):
        stack = t * n
        h = BASE_H + stack + HEADROOM
        part += Pos(xc, yt, 0) * Cylinder(od / 2, h, align=ON_BED)
        bore = d + TUBE_CLEAR
        cuts.append(Pos(xc, yt, BASE_H) * Cylinder(bore / 2, h, align=ON_BED))
        # finger slot toward -Y, from the floor to the top
        cuts.append(Pos(xc, yt - od / 2, BASE_H) * Box(SLOT_W, od, h, align=ON_BED))
        # fill line: V-groove ring at roll height
        zf = BASE_H + stack
        r = od / 2
        v = Polygon((r - GROOVE, zf), (r + 1, zf - GROOVE - 1), (r + 1, zf + GROOVE + 1), align=None)
        cuts.append(Pos(xc, yt, 0) * revolve(Plane.XZ * v, Axis.Z, 360))
        # labels in the base, in front of the tube
        yl = yt - od / 2 - 3 - TEXT_SIZE / 2
        for txt, yy in ((name, yl), (value, yl - TEXT_SIZE - 2.5)):
            s = Text(txt, font_size=TEXT_SIZE, font_style=FontStyle.BOLD)
            cuts.append(Pos(xc, yy, BASE_H - TEXT_DEPTH) * extrude(s, TEXT_DEPTH + 1))
    part -= Part() + cuts
    return part
