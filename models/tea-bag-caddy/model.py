"""tea-bag-caddy: open-top box holding 20 enveloped tea bags on edge.

Spec: bags (75 x 65 mm envelopes) stand on their 75 mm edge in one row along Y,
faces toward +-Y. Walls are 50 mm tall so 15 mm of each bag sticks out; U-shaped
finger notches in both side walls let you pinch the last bags. Front wall carries a
"TEA" label recessed 0.6 mm.
Assumptions: envelope thickness ~4 mm -> 20 bags = 80 mm row, +6 mm play;
1.5 mm side play on the 75 mm width.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 0, 25), grams=40)],
    print_orientation="auto",
    supports="auto",
    brim="auto",
)

# Parameters
BAG_W = 75.0
BAG_H = 65.0
BAG_T = 4.0
N_BAGS = 20
PLAY_W = 1.5
PLAY_L = 6.0
WALL = 2.4
FLOOR = 2.0
HEIGHT = 50.0
CORNER_R = 5.0
NOTCH_W = 30.0
NOTCH_D = 25.0
LABEL = "TEA"
LABEL_SIZE = 12.0

IN_X = BAG_W + 2 * PLAY_W
IN_Y = N_BAGS * BAG_T + PLAY_L


def build() -> Part:
    ox, oy = IN_X + 2 * WALL, IN_Y + 2 * WALL
    part = rounded_box(ox, oy, HEIGHT, radius=CORNER_R)
    part -= Pos(0, 0, FLOOR) * rounded_box(IN_X, IN_Y, HEIGHT, radius=CORNER_R - WALL,
                                          bottom_chamfer=0)
    # U finger notches through both side walls (X walls)
    r = NOTCH_W / 2
    u = Pos(0, 0, HEIGHT - NOTCH_D + r) * (Box(ox + 2, NOTCH_W, NOTCH_D, align=(Align.CENTER, Align.CENTER, Align.MIN))
                                           + Rot(0, 90, 0) * Cylinder(r, ox + 2))
    part -= u
    # front label (-Y face), recessed
    txt = label(LABEL, size=LABEL_SIZE, depth=0.6 + 0.01)
    part -= Pos(0, -oy / 2 + 0.6, HEIGHT / 2) * Rot(90, 0, 0) * Pos(0, 0, 0) * txt
    return part
