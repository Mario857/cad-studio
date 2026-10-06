"""led-tealight-house: Christmas village-house lantern over a removable base for an LED tealight.

Spec: hollow house 80 (X) x 70 (Y) x 110 mm total (incl. 4 mm base), pitched roof with the
ridge along X and roof slopes of ~49 deg (>= 45 deg, prints without support). Front: door +
two windows; back: three windows; each gable: one window + a diamond attic window. All
openings have ~54 deg pointed tops (self-supporting, steeper than 45 deg); windows have a
vertical mullion only, so there are no bridges.
The house is open at the bottom and lifts off a separate base plate. The base has a
rectangular locating lip that slips inside the house walls and a ring that centres a
battery LED tealight (dia 38 x 15 mm). Both parts are printed together on one plate.

SAFETY: LED tealights ONLY - never use a real candle. Printed in ABS, which softens and can
burn near an open flame.

Assumptions:
- Tealight is dia 38 mm (ring has 0.5 mm radial clearance); switch on its underside, so the
  house is lifted off to switch it on/off.
- House-to-base lip fit: 0.3 mm per side clearance (easy lift-off, still located).
- Walls 2.0 mm; door bottom kept 3 mm above the house rim so the bottom ring stays closed.
- 2 separate bodies are intended (house + base). Both are modeled on z=0 side by side (base
  at +X) for printing together; in use the house sits on the base (total 110 mm).
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,  # house alone stands on its full 80x70 rim (COM ~50 mm high -> very stable);
                     # the audit would treat house+base side-by-side print layout as one body
    loads=[],
    print_orientation="auto",
    supports="auto",
    brim="auto",
)

# Overall
WIDTH = 80.0          # X, along ridge
DEPTH = 70.0          # Y
TOTAL_H = 110.0       # base + house
BASE_T = 4.0          # base plate thickness
ROOF_RISE = 40.0      # eave -> ridge (atan(40/35) ~ 48.8 deg)
WALL = 2.0
HOUSE_H = TOTAL_H - BASE_T
WALL_H = HOUSE_H - ROOF_RISE

# Openings: pointed tops, apex = rect height + PEAK * width/2 (PEAK 1.4 -> ~54 deg from horizontal)
PEAK = 1.4
DOOR_W, DOOR_H, DOOR_Z = 16.0, 26.0, 3.0
WIN_W, WIN_H, WIN_Z = 14.0, 18.0, 30.0
WIN_X = 24.0
BAR = 1.6             # vertical window mullion width (no horizontal bar -> no bridges)
GABLE_WIN_W, GABLE_WIN_H, GABLE_WIN_Z = 14.0, 18.0, 30.0
ATTIC_D = 12.0        # diamond attic window, corner-to-corner
ATTIC_Z = WALL_H + 10.0

# Base
LIP_CLEAR = 0.3       # per side, lip inside house walls
LIP_T = 1.6
LIP_H = 5.0
TEALIGHT_D = 38.0
TEALIGHT_CLEAR = 0.5  # radial
RING_T = 1.6
RING_H = 4.0
BASE_GAP = 10.0       # gap between house and base on the print plate
BASE_X = WIDTH + BASE_GAP


def arch(w, h):
    a = w / 2 * PEAK
    return Polygon((-w / 2, 0), (w / 2, 0), (w / 2, h), (0, h + a), (-w / 2, h), align=None)


def window(w, h):
    s = arch(w, h)
    s -= Rectangle(BAR, 3 * h)
    return s


def cut_front_back(sketch, x, z, y):
    return Pos(x, y, z) * extrude(Plane.XZ * sketch, WALL * 2, both=True)


def cut_gable(sketch, y, z, x):
    return Pos(x, y, z) * extrude(Plane.YZ * sketch, WALL * 2, both=True)


def house() -> Part:
    prof = Polygon((-DEPTH / 2, 0), (DEPTH / 2, 0), (DEPTH / 2, WALL_H), (0, HOUSE_H),
                   (-DEPTH / 2, WALL_H), align=None)
    body = extrude(Plane.YZ * prof, WIDTH / 2, both=True)
    body = offset(body, -WALL, openings=body.faces().sort_by(Axis.Z)[0])
    fy, by = -DEPTH / 2, DEPTH / 2
    cuts = [cut_front_back(arch(DOOR_W, DOOR_H), 0, DOOR_Z, fy)]
    for x in (-WIN_X, WIN_X):
        cuts.append(cut_front_back(window(WIN_W, WIN_H), x, WIN_Z, fy))
    for x in (-WIN_X, 0, WIN_X):
        cuts.append(cut_front_back(window(WIN_W, WIN_H), x, WIN_Z, by))
    h = ATTIC_D / 2
    diamond = Polygon((0, -h * PEAK), (h, 0), (0, h * PEAK), (-h, 0), align=None)
    for x in (-WIDTH / 2, WIDTH / 2):
        cuts.append(cut_gable(window(GABLE_WIN_W, GABLE_WIN_H), 0, GABLE_WIN_Z, x))
        cuts.append(cut_gable(diamond, 0, ATTIC_Z, x))
    for c in cuts:
        body -= c
    outer = [e for e in body.edges().group_by(Axis.Z)[0]
             if abs(abs(e.center().X) - WIDTH / 2) < 0.01 or abs(abs(e.center().Y) - DEPTH / 2) < 0.01]
    body = chamfer(outer, 0.4)  # outer only: an inner rim chamfer would be a downward overhang
    return body  # on bed for printing; in use it sits on the base (z += BASE_T)


def base() -> Part:
    plate = rounded_box(WIDTH, DEPTH, BASE_T, radius=1)
    lo_x = WIDTH - 2 * WALL - 2 * LIP_CLEAR
    lo_y = DEPTH - 2 * WALL - 2 * LIP_CLEAR
    lip = Box(lo_x, lo_y, LIP_H, align=ON_BED) - Box(lo_x - 2 * LIP_T, lo_y - 2 * LIP_T, LIP_H, align=ON_BED)
    ri = TEALIGHT_D / 2 + TEALIGHT_CLEAR
    ring = Cylinder(ri + RING_T, RING_H, align=ON_BED) - Cylinder(ri, RING_H, align=ON_BED)
    part = plate + Pos(0, 0, BASE_T) * (lip + ring)
    return Pos(BASE_X, 0, 0) * part


def build():
    return [house(), base()]
