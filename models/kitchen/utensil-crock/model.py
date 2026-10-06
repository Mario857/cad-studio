"""utensil-crock: 120 mm kitchen utensil crock with draining floor and divider.

Spec: 120 mm OD x 160 mm tall cylinder, 2.4 mm wall, 4 mm floor. 1.6 mm cross divider
(100 mm tall) makes 4 compartments. Drainage: 13 x 5 mm floor holes sit on 8 radial
45 deg V-grooves (5 wide, 2.5 deep) under the floor, so water runs out to the edge even on a flat counter
(V roofs print without supports). Rim edge rounded.
Assumptions: utensils up to ~350 mm long, total ~800 g. ABS is not food-safe: fine for
holding clean utensils, not for storing food.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 0, 120), grams=800)],
    print_orientation="auto",
    supports="auto",
    brim="auto",
)

# Parameters
OD = 120.0
HEIGHT = 160.0
WALL = 2.4
FLOOR = 4.0
DIVIDER_T = 1.6
DIVIDER_H = 100.0
GROOVES = 8
GROOVE_W = 5.0
DRAIN_D = 5.0
DRAIN_R = (25.0, 45.0)  # hole radii along alternating grooves


def build() -> Part:
    import math
    part = Cylinder(OD / 2, HEIGHT, align=ON_BED)
    part -= Pos(0, 0, FLOOR) * Cylinder(OD / 2 - WALL, HEIGHT, align=ON_BED)
    part = fillet(part.edges().group_by(Axis.Z)[-1], 1.0)
    for a in (0, 90):
        part += Rot(0, 0, a) * Box(OD - WALL, DIVIDER_T, DIVIDER_H, align=ON_BED)
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    # drain grooves under the floor + holes
    groove = Rot(45, 0, 0) * Box(OD + 2, GROOVE_W / 1.414, GROOVE_W / 1.414,
                                 align=(Align.MIN, Align.CENTER, Align.CENTER))  # 45 deg V roof
    holes = [Pos(0, 0, 0)]
    for i in range(GROOVES):
        a = i * 360 / GROOVES + 360 / GROOVES / 2  # between divider walls
        part -= Rot(0, 0, a) * groove
        for r in DRAIN_R:
            holes.append(Pos(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), 0))
    for p in holes:
        part -= p * Cylinder(DRAIN_D / 2, FLOOR * 3)
    return part
