"""drain-hair-catcher: domed, slotted hair catcher that drops into a sink drain.

Spec: a cylindrical basket drops into the drain bore (DRAIN_D, radial FIT_CLEAR). Above it a
flange (FLANGE_D = DRAIN_D + 16) keeps it from falling in; a low spherical dome with radial
slots (SLOT_W) covers the top, with a pull tab (finger/nail grip hole) at the center. The
basket wall has vertical slots and the floor has radial slots. A central column carries the
dome center so the dome's underside is a 45-degree "inverted V" roof -> prints with no supports.

Print: in-use orientation (floor on bed, dome up). All slots are vertical through-cuts or have
45-degree pointed roofs, so nothing needs support.

Assumptions:
- Drain bore 40 mm; 0.75 mm radial clearance (basket OD 38.5) so it drops in loosely.
- The flange underside is a 45-degree cone (a flat 8 mm overhang can't print support-free in
  this orientation). It seats on the drain rim edge and self-centers; vertical slots through
  the flange cone let water that runs under the flange reach the drain.
- Basket depth 25 mm below the flange cone; most sink drains have >= 30 mm of straight bore.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # in-use orientation: floor on bed, dome up
    supports="off",
    brim="auto",
)

# Parameters
DRAIN_D = 40.0          # drain bore diameter
FIT_CLEAR = 0.75        # radial clearance basket <-> bore
FLANGE_D = DRAIN_D + 16.0
WALL = 2.0              # basket wall
FLOOR_T = 2.0           # basket floor
BASKET_H = 25.0         # floor bottom to start of flange cone
FLANGE_EDGE = 1.6       # vertical rim height at flange outer edge
DOME_H = 5.0            # dome rise above flange edge
DOME_MIN_T = 2.4        # min dome thickness above the inner roof
COL_D = 8.0             # central column carrying the dome center
SLOT_W = 2.5            # all water slots
N_TOP_SLOTS = 8         # radial slots in dome
N_FLOOR_SLOTS = 8       # radial slots in floor
N_WALL_SLOTS = 12       # vertical slots in basket wall
N_FLANGE_SLOTS = 16     # radial slots through flange cone
SLOT_R0 = 7.5           # inner radius of dome/floor slots
WALL_SLOT_MARGIN = 4.0  # solid wall kept above floor / below cone
TAB_L = 14.0            # pull tab length (X)
TAB_T = 3.5             # pull tab thickness (Y)
TAB_H = 13.0            # pull tab height above dome top
TAB_HOLE_D = 7.0        # grip hole

# Derived
R_OUT = DRAIN_D / 2 - FIT_CLEAR
R_IN = R_OUT - WALL
FR = FLANGE_D / 2
COL_R = COL_D / 2
Z_CONE_TOP = BASKET_H + (FR - R_OUT)       # 45-degree cone
Z_FL = Z_CONE_TOP + FLANGE_EDGE            # flange edge top
Z_TOP = Z_FL + DOME_H                      # dome apex
RS = (FR**2 + DOME_H**2) / (2 * DOME_H)    # dome sphere radius
R_M = (COL_R + R_IN) / 2                   # inner roof ridge radius


def dome_z(r):
    return Z_TOP - (RS - math.sqrt(RS**2 - r**2))


Z_V = dome_z(R_M) - DOME_MIN_T - (R_M - COL_R)  # inner void height at wall/column


def radial_slot(r0, r1, z0, z1, ang):
    """Vertical stadium slot from radius r0..r1 (overall), z0..z1, at angle ang (deg)."""
    s = slot(r1 - r0, SLOT_W, z1 - z0)  # long axis X, cutter z -depth..0
    return Rot(0, 0, ang) * Pos((r0 + r1) / 2, 0, z1) * s


def wall_slot(ang):
    z0 = FLOOR_T + WALL_SLOT_MARGIN
    z1 = BASKET_H - WALL_SLOT_MARGIN - SLOT_W / 2
    prof = Polygon(
        (-SLOT_W / 2, z0), (SLOT_W / 2, z0), (SLOT_W / 2, z1),
        (0, z1 + SLOT_W / 2), (-SLOT_W / 2, z1), align=None,
    )
    cut = extrude(Plane.YZ.offset(R_IN - 1) * prof, WALL + 2)
    return Rot(0, 0, ang) * cut


def build() -> Part:
    # Outer body of revolution, capped by the dome sphere
    outer = Polygon(
        (0, 0), (R_OUT - 0.4, 0), (R_OUT, 0.4), (R_OUT, BASKET_H),
        (FR, Z_CONE_TOP), (FR, Z_TOP + 5), (0, Z_TOP + 5), align=None,
    )
    body = revolve(Plane.XZ * outer, Axis.Z, 360)
    body = body & Pos(0, 0, Z_TOP - RS) * Sphere(RS)

    # Inner void: basket bore with 45-degree inverted-V roof between column and wall
    void = Polygon(
        (COL_R, FLOOR_T), (R_IN, FLOOR_T), (R_IN, Z_V),
        (R_M, Z_V + (R_M - COL_R)), (COL_R, Z_V), align=None,
    )
    body = body - revolve(Plane.XZ * void, Axis.Z, 360)

    cuts = []
    r1_in = R_IN - 1.0
    for i in range(N_TOP_SLOTS):
        a = 180 / N_TOP_SLOTS + i * 360 / N_TOP_SLOTS
        cuts.append(radial_slot(SLOT_R0, r1_in, Z_V - 1, Z_TOP + 1, a))
    for i in range(N_FLOOR_SLOTS):
        a = i * 360 / N_FLOOR_SLOTS
        cuts.append(radial_slot(SLOT_R0, r1_in, -1, FLOOR_T + 1, a))
    for i in range(N_WALL_SLOTS):
        cuts.append(wall_slot(i * 360 / N_WALL_SLOTS))
    for i in range(N_FLANGE_SLOTS):
        a = i * 360 / N_FLANGE_SLOTS + 180 / N_FLANGE_SLOTS
        cuts.append(radial_slot(R_OUT + 0.4, FR - 2.0, BASKET_H, Z_TOP + 1, a))
    for c in cuts:
        body = body - c

    # Pull tab with grip hole
    tab = Pos(0, 0, Z_TOP - 2) * Box(TAB_L, TAB_T, TAB_H + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    tab = fillet(tab.edges().group_by(Axis.Z)[-1].filter_by(Axis.Y), TAB_T * 0.45)
    tab = tab - Pos(0, 0, Z_TOP + TAB_H - TAB_HOLE_D / 2 - 2.5) * teardrop_hole(TAB_HOLE_D, TAB_T + 2, along="Y")
    return body + tab
