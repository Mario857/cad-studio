"""napkin-holder: upright table napkin holder for folded paper napkins.

Spec: 190 x 90 x 5 mm rounded base with two 4 mm upright walls (175 x 110 mm) leaving a
42 mm slot. Each wall has 3 diamond windows (45 deg edges -> no supports, less plastic)
and rounded top corners. Napkins stand on edge and stick out ~55 mm above the walls.
Assumptions: standard 33 cm napkins folded in quarters = 165 x 165 mm, stack <= 40 mm.
Not a food-contact part.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 0, 80), grams=150)],
    print_orientation="auto",
    supports="auto",
    brim="auto",
)

# Parameters
BASE_L = 190.0
BASE_W = 90.0
BASE_T = 5.0
BASE_R = 15.0
WALL_L = 175.0
WALL_H = 110.0         # above the base
WALL_T = 4.0
SLOT = 42.0
TOP_R = 20.0
WIN = 32.0             # diamond window diagonal
WIN_PITCH = 52.0
WIN_Z = 55.0           # window centre above the base


def build() -> Part:
    part = rounded_box(BASE_L, BASE_W, BASE_T, radius=BASE_R)
    part = fillet(part.edges().group_by(Axis.Z)[-1], 1.5)
    wall = Box(WALL_L, WALL_T, WALL_H + 1, align=ON_BED)
    wall = fillet(wall.edges().filter_by(Axis.Y).group_by(Axis.Z)[-1], TOP_R)
    diamond = Rot(0, 45, 0) * Box(WIN / 1.4142, WALL_T * 3, WIN / 1.4142)
    for i in (-1, 0, 1):
        wall -= Pos(i * WIN_PITCH, 0, WIN_Z) * diamond
    for s in (-1, 1):
        part += Pos(0, s * (SLOT + WALL_T) / 2, BASE_T - 1) * wall
    return part
