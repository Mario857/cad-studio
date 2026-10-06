"""lure-card-hanger: wall-less hanging holder for a 75x125 mm sticky trap / lure card.

Spec: 2.4 mm backplate, card slides in from the top between two edge slots (rail wall + 3 mm
retaining lip), bottom bar stops it. A 2.4 mm-wall C-spring hook on the top edge (open mouth up,
flexing arms) clips onto 8-25 mm branches/rails; a pointed drip tab at the bottom lets drips fall clear.
Printed flat (back on bed), no supports: lips are 3 mm bridges, hook is a plain extrusion.
Model coordinates = print orientation (plate flat, back at z=0); in use the plate hangs vertical,
branch axis runs along model Z (through the hook), card faces +Z.
Support WARN accepted: the 7.6 cm2 "overhang" is the two 3 mm x 1.6 mm lips, printed as short bridges off the rail walls.
Assumptions: card thickness <= 1.4 mm (pocket 1.6 mm); card 75 x 125; branch rests in hook bottom.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="auto",
)

CARD_W, CARD_H = 75.0, 125.0
CLR = 0.6                 # per-side card clearance
PLATE_T = 2.4
POCKET_T = 1.6            # card gap above plate
LIP_T = 1.6
LIP_W = 3.0               # card overlap
RAIL_W = 3.0
BAR_H = 3.0               # bottom stop bar

HOOK_T = 8.0              # hook thickness along branch axis
HOOK_WALL = 2.4
HOOK_RI = 12.5            # inner radius -> up to 25 mm branch
MOUTH_HALF = 7.0          # mouth 14 mm; arms flex to admit 25 mm
TAB_W, TAB_L = 14.0, 8.0  # drip tab

POCKET_W = CARD_W + 2 * CLR
PLATE_W = POCKET_W + 2 * RAIL_W
TOP_Y = BAR_H + CARD_H + 2 * CLR
RAIL_H = PLATE_T + POCKET_T + LIP_T


def build() -> Part:
    plate = Pos(0, TOP_Y / 2, 0) * Box(PLATE_W, TOP_Y, PLATE_T, align=ON_BED)
    plate = chamfer(plate.edges().group_by(Axis.Z)[0], 0.4)
    part = plate
    xo = POCKET_W / 2
    for s in (-1, 1):
        wall = Pos(s * (xo + RAIL_W / 2), TOP_Y / 2, 0) * Box(RAIL_W, TOP_Y, RAIL_H, align=ON_BED)
        lip_y0 = BAR_H
        lip = Pos(s * (xo - LIP_W / 2 + 0.01), (lip_y0 + TOP_Y) / 2, PLATE_T + POCKET_T) * Box(
            LIP_W + 0.02, TOP_Y - lip_y0, LIP_T, align=ON_BED)
        part += wall + lip
    part += Pos(0, BAR_H / 2, 0) * Box(PLATE_W, BAR_H, RAIL_H, align=ON_BED)

    # drip tab (pointed, below bottom edge)
    tab = extrude(Plane.XY * Polygon((-TAB_W / 2, 0.5), (TAB_W / 2, 0.5), (0, -TAB_L), align=None), PLATE_T)
    part += Pos(0, 0, PLATE_T) * tab

    # spring hook on top edge
    cy = TOP_Y + 1.0 + HOOK_RI
    ring = Pos(0, cy, 0) * (Cylinder(HOOK_RI + HOOK_WALL, HOOK_T, align=ON_BED)
                            - Cylinder(HOOK_RI, HOOK_T, align=ON_BED))
    # open the mouth upward
    mouth = Pos(0, cy + HOOK_RI, HOOK_T / 2) * Box(2 * MOUTH_HALF, 2 * (HOOK_RI + HOOK_WALL), HOOK_T + 1)
    ring = ring - mouth
    ring = ring + Pos(0, TOP_Y, 0) * Box(2 * HOOK_RI * 0.8, 3.0, HOOK_T, align=ON_BED)
    part += ring
    return part
