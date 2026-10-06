"""pet-food-can-lid: stepped snap-on lid that reseals opened Ø73 / Ø85 mm pet food cans in the fridge.

Spec: one hat-shaped lid with a stepped underside. The wide lower bore (CAN_D_LARGE = 85 mm)
seats on the large can's rim against a 45° shoulder; the narrow upper bore (CAN_D_SMALL = 73 mm)
takes the small can, whose rim passes through the wide section and seats under the top plate.
Each bore has a continuous inward snap bead (BEAD radial interference, 45° lead-in both sides)
that clicks under the rolled can rim. A wedge-shaped pull tab on the lower edge levers it off.
Printed upside down (top plate on the bed): no supports, all slopes 45°.
Approx. Ø89.6 x 26 mm plus a 10 mm tab.

Use / care: hand-wash only (warm water, no dishwasher - ABS softens and warps). Do NOT use as
a feeding dish. ABS must not hold food/water directly and is not a chew toy: the lid only
covers the can; keep food below the rim so it does not touch the lid, and keep the lid away
from pets when it is off the can. All exposed edges rounded/chamfered; the plate edge, which
sits on the bed, has a 45° chamfer.

Assumptions: nominal can sizes are the rolled-rim outer diameters (73 mm ~ 300-series,
85 mm ~ 307/400 g cans). The snap bead sits RIM_DROP below the rim seat (rim bead ~3 mm tall).
0.3 mm radial clearance on the bores, 0.7 mm bead -> ~0.4 mm snap interference; increase
BEAD for a tighter grip, decrease if too hard to push on. Not airtight - a fridge cover.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(180, 0, 0),  # top plate on the bed, cavity up
    supports="off",
    brim="auto",
)

# Parameters
CAN_D_SMALL = 73.0     # small can rim OD
CAN_D_LARGE = 85.0     # large can rim OD
RIM_CLEAR = 0.3        # radial clearance bore vs rim
BEAD = 0.7             # inward snap bead (radial)
RIM_DROP = 3.5         # bead centre below the rim seat
WALL = 2.0             # skirt / shoulder wall
PLATE_T = 2.0          # top plate
H_LARGE = 9.0          # height of the wide bore section (to shoulder start)
H_SMALL = 9.0          # height of the narrow bore section above the shoulder
LEAD_IN = 0.8          # entry chamfer on the lower bore edge
TOP_CHAMFER = 1.0      # 45° chamfer on the plate edge (bed edge when printing)
EDGE_FILLET = 0.6      # skirt lip rounding

TAB_W = 22.0           # pull tab width
TAB_L = 10.0           # pull tab reach beyond the skirt
TAB_T = 2.5            # pull tab tip thickness
TAB_R = 5.0            # tab corner radius in plan
TAB_FILLET = 0.8

R1 = CAN_D_SMALL / 2 + RIM_CLEAR
R2 = CAN_D_LARGE / 2 + RIM_CLEAR
Z_SHOULDER = H_LARGE + (R2 - R1)          # top of the 45° shoulder (inside)
Z_CEIL = Z_SHOULDER + H_SMALL             # underside of the plate
H_TOTAL = Z_CEIL + PLATE_T
Z_SEAT_LARGE = H_LARGE + RIM_CLEAR        # where an 85 mm rim meets the shoulder
Z_BEAD_LARGE = Z_SEAT_LARGE - RIM_DROP
Z_BEAD_SMALL = Z_CEIL - RIM_DROP
OUT_K = WALL * (math.sqrt(2) - 1)         # outer 45° offset of the shoulder


def lid_body():
    pts = [
        (R2 + LEAD_IN, 0),
        (R2, LEAD_IN),
        (R2, Z_BEAD_LARGE - BEAD),
        (R2 - BEAD, Z_BEAD_LARGE),
        (R2, Z_BEAD_LARGE + BEAD),
        (R2, H_LARGE),
        (R1, Z_SHOULDER),
        (R1, Z_BEAD_SMALL - BEAD),
        (R1 - BEAD, Z_BEAD_SMALL),
        (R1, Z_BEAD_SMALL + BEAD),
        (R1, Z_CEIL),
        (0, Z_CEIL),
        (0, H_TOTAL),
        (R1 + WALL - TOP_CHAMFER, H_TOTAL),
        (R1 + WALL, H_TOTAL - TOP_CHAMFER),
        (R1 + WALL, Z_SHOULDER + OUT_K),
        (R2 + WALL, H_LARGE + OUT_K),
        (R2 + WALL, 0),
    ]
    body = revolve(Plane.XZ * Polygon(*pts, align=None), Axis.Z, 360)
    lip = body.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[0] \
        .filter_by(lambda e: e.radius > R2 + LEAD_IN + 0.5)
    return fillet(lip, EDGE_FILLET)


def pull_tab():
    x0 = R2 + 0.2
    x1 = R2 + WALL + TAB_L
    prof = Polygon((x0, 0), (x1, 0), (x1, TAB_T), (x0, TAB_T + (x1 - x0)), align=None)
    tab = extrude(Plane.XZ * prof, TAB_W / 2, both=True)
    tab = fillet(tab.edges().filter_by(Axis.Z).group_by(Axis.X)[-1], TAB_R)
    tab = fillet(tab.edges().filter_by_position(Axis.X, x0 + 1, x1 + 1)
                 .filter_by(lambda e: e.center().Z > 0.1), TAB_FILLET)
    tab = fillet(tab.edges().group_by(Axis.Z)[0]
                 .filter_by(lambda e: e.center().X > x0 + 1), EDGE_FILLET)
    return tab


def build():
    tab = pull_tab()
    lid = lid_body() + tab
    return lid
