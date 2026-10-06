"""ornament-storage-tray: stackable 12-cell storage tray for Ø80 mm Christmas baubles.

Spec:
- 12 cells for Ø80 baubles in ONE piece on the 300x320 plate. A square 4x3 grid at ~84 mm pitch
  would be ~340 mm long, so the cells are hex-staggered instead: 4 rows of 3, alternate rows shifted
  by half a pitch. Row spacing = pitch*sin(60°), so the outline is ~293 x 301 mm.
- Each cell is a low ring (ID = bauble + 2*CELL_CLR) standing on a flat floor; neighbouring rings
  share their wall. Baubles rest on the floor and are kept apart by the rings.
- Stacking: a locating lip under the floor (inset by WALL + STACK_CLR) drops inside the tray below;
  a 45° flare above the lip sits on the lower tray's rim. Tray height is derived from bauble height
  + hanger cap + headroom so the stacked tray never touches the baubles.
- Finger cut-outs: U-notches from the rim on the two short (±X) sides; when stacked they leave
  room to hook fingers under the flare of the tray above.
- Support-free: floor on the bed, 45° flare, notches open at the top, no bridges.

Assumptions:
- Bauble Ø80 incl. tolerance, total height incl. metal cap + hanger loop = 80 + CAP_H (12) mm.
- Bauble mass ~30 g each (only used for the stability audit).
- Thin (1.3-1.6 mm) walls are fine: the load is a few hundred grams of baubles / stacked trays.
- Fits the 300x320 bed with brim off (outline 293 x 301 mm); prints in one piece.
"""

import math

from build123d import *

from cadlib import *

# Parameters — cells
BAUBLE_D = 80.0        # bauble diameter
CAP_H = 12.0           # cap + hanger loop above the ball
CELL_CLR = 1.0         # radial clearance bauble -> ring
RING_T = 1.3           # cell ring wall
RING_H = 15.0          # ring height above floor
ROWS = 4
COLS = 3
# Parameters — tray
FLOOR = 1.3            # floor thickness
WALL = 1.6             # outer wall
CORNER_R = 10.0        # outer corner radius
HEADROOM = 3.0         # gap bauble top -> floor of the tray stacked above
# Parameters — stacking
STACK_CLR = 0.4        # per-side clearance lip -> inner wall of the tray below
LIP_H = 6.0            # locating lip depth
# Parameters — finger cut-outs (±X walls)
NOTCH_W = 70.0
NOTCH_D = 45.0

# Derived
CELL_ID = BAUBLE_D + 2 * CELL_CLR
PITCH = CELL_ID + RING_T
ROW_PITCH = PITCH * math.sqrt(3) / 2
INNER_X = (COLS - 1) * PITCH + PITCH / 2 + CELL_ID
INNER_Y = (ROWS - 1) * ROW_PITCH + CELL_ID
OUTER_X = INNER_X + 2 * WALL
OUTER_Y = INNER_Y + 2 * WALL
FLARE = WALL + STACK_CLR                     # lip inset per side
HEIGHT = FLOOR + BAUBLE_D + CAP_H + HEADROOM + LIP_H + STACK_CLR


def cell_centers():
    pts = []
    for r in range(ROWS):
        y = (r - (ROWS - 1) / 2) * ROW_PITCH
        shift = -PITCH / 4 if r % 2 == 0 else PITCH / 4
        for c in range(COLS):
            pts.append(((c - (COLS - 1) / 2) * PITCH + shift, y))
    return pts


META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(x, y, FLOOR + BAUBLE_D / 2), grams=30) for x, y in cell_centers()],
    print_orientation=(0, 0, 0),   # floor on the bed: support-free
    supports="off",
    brim="off",                    # outline 293x301 already uses most of the plate
)


def build() -> Part:
    top = HEIGHT
    # outer solid: lip + 45° flare + full-size body
    body = Pos(0, 0, LIP_H) * rounded_box(OUTER_X, OUTER_Y, top - LIP_H, radius=CORNER_R,
                                          bottom_chamfer=FLARE)
    lip = rounded_box(OUTER_X - 2 * FLARE, OUTER_Y - 2 * FLARE, LIP_H + 1,
                      radius=CORNER_R - FLARE, bottom_chamfer=0.4)
    outer = body + lip

    # cavities
    lip_cav = Pos(0, 0, FLOOR) * rounded_box(OUTER_X - 2 * FLARE - 2 * WALL,
                                              OUTER_Y - 2 * FLARE - 2 * WALL,
                                              LIP_H + FLARE - FLOOR + 0.01,
                                              radius=CORNER_R - FLARE - WALL, bottom_chamfer=0)
    main_cav = Pos(0, 0, LIP_H + FLARE) * rounded_box(INNER_X, INNER_Y, top,
                                                       radius=CORNER_R - WALL, bottom_chamfer=0)
    tray = outer - lip_cav - main_cav

    # cell rings, clipped to the outer solid
    rings = None
    for x, y in cell_centers():
        ring = Pos(x, y, FLOOR - 0.01) * (Cylinder(CELL_ID / 2 + RING_T, RING_H + 0.01, align=ON_BED)
                                          - Cylinder(CELL_ID / 2, RING_H + 0.01, align=ON_BED))
        rings = ring if rings is None else rings + ring
    tray = tray + (rings & outer)

    # finger cut-outs on ±X walls (U-notch open at the rim)
    r = NOTCH_W / 2
    cut = (Pos(0, 0, top - NOTCH_D + r) * Rot(0, 90, 0) * Cylinder(r, OUTER_X + 10)
           + Pos(0, 0, top - NOTCH_D + r) * Box(OUTER_X + 10, NOTCH_W, NOTCH_D, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    # keep the cut only through the X walls (not across the whole tray: it is open-topped anyway)
    tray = tray - cut
    return tray
