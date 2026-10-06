"""medicine-cabinet-riser: 2-step shelf riser for a 100 mm deep medicine cabinet.

Spec: 250 mm wide, 100 mm deep. Front step top at 40 mm, rear step top at 80 mm, each step
50 mm deep, with a 6 mm front lip on each step so bottles don't slide off.
Construction (chosen for zero supports): a hollow closed 2D stepped profile (YZ plane:
Y = depth, Z = height) extruded along the full width X, with an internal diagonal web.
It is printed standing on its end (profile on the bed, width along print Z), so every wall
is vertical -- no overhangs, no bridges, no ceilings. Layers then run across the width,
so step bending loads act within layers (strong). The two ends are open tube ends.
Assumptions: cabinet shelf >= 250 mm wide and >= 100 mm deep; ~300 g of bottles per step;
2 mm walls are ample for small bottles.
"""

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm. The audit picks the print orientation.
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[
        dict(at=(0, 25, 46), grams=300),   # bottles on lower step
        dict(at=(0, 75, 86), grams=300),   # bottles on upper step
    ],
    print_orientation=(0, 90, 0),  # stand on end: width along print Z, profile on bed
    supports="off",
    brim="on",            # tall part (250 mm) on a thin-walled 8.5 cm2 footprint, ABS
)

# Parameters
WIDTH = 250.0        # along X (cabinet width direction)
DEPTH = 100.0        # along Y (front y=0 -> back y=DEPTH)
STEP1_H = 40.0       # lower (front) step top surface height
STEP2_H = 80.0       # upper (rear) step top surface height
STEP1_D = DEPTH / 2  # lower step depth
WALL = 2.0           # profile wall thickness
WEB = 2.0            # internal diagonal web thickness
LIP_H = 6.0          # lip height above each step surface
LIP_T = 2.4          # lip thickness
EDGE_CHAMFER = 0.4   # elephant-foot chamfer on the bed (end) face


def profile_outer() -> Face:
    return Polygon(
        (0, 0), (DEPTH, 0), (DEPTH, STEP2_H), (STEP1_D, STEP2_H),
        (STEP1_D, STEP1_H), (0, STEP1_H), align=None,
    )


def build() -> Part:
    outer = profile_outer()
    inner = offset(outer, -WALL, kind=Kind.INTERSECTION)
    sk = outer - inner
    # Lips at the front edge of each step
    sk += Pos(LIP_T / 2, STEP1_H + LIP_H / 2) * Rectangle(LIP_T, LIP_H)
    sk += Pos(STEP1_D + LIP_T / 2, STEP2_H + LIP_H / 2) * Rectangle(LIP_T, LIP_H)
    # Internal diagonal web: rear-bottom corner -> foot of the riser (triangulates the box)
    sk += diag_web()
    part = extrude(Plane.YZ * sk, WIDTH)
    part = Pos(-WIDTH / 2, 0, 0) * part
    ends = part.edges().group_by(Axis.X)[0]
    part = chamfer(ends, EDGE_CHAMFER)
    return part


def diag_web() -> Face:
    """Slanted web from the rear bottom inner corner up to the step riser's inner corner."""
    import math
    x0, y0 = DEPTH - WALL, WALL
    x1, y1 = STEP1_D + WALL / 2, STEP1_H
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    length = math.hypot(x1 - x0, y1 - y0) + WEB
    return Pos((x0 + x1) / 2, (y0 + y1) / 2) * Rot(0, 0, ang) * Rectangle(length, WEB)
