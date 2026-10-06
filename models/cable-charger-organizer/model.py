"""cable-charger-organizer: flat-pack travel case for a GaN charger, cables, dongle and SD cards.

Spec: one-piece print. Base tray (Y < 0 side) and lid (Y > 0 side) lie open, both opening up,
joined by a 0.65 mm living-hinge strip on the bed. Fold the lid over the base: the strip runs up
the base's back face (strip length = base height + lid height) and the lid closes flush on the
base rim. A tab on the lid's front edge with an inward 45° ridge snaps into a V-groove on the
base front face.
Base compartments (left -> right): GaN charger pocket (65x65x30 + clearance, with a finger notch),
3 cable wrap channels (20 mm wide, full depth), USB-C dongle pocket, SD card block with 2 slots.
Coordinates = print/open state (model is a flat-pack; in-use shape is the folded state).

Assumptions:
- Charger 65 x 65 x 30 mm -> pocket 68 x 68, 32 mm deep (1.5 mm side / 2 mm top clearance).
- Cables are coiled into 20 x 68 x 32 mm channels; dongle fits 30 x 52 x 32 mm.
- SD cards standard 24 x 32 x 2.1 mm, stored upright (slots 26 x 2.8, 20 mm deep, top at z=22
  so the protruding 12 mm clears the lid).
- PETG for living-hinge fatigue life. The 0.65 mm hinge strip (min the wall audit allows) is thinner than the
  1.2 mm wall rule (any thin-wall WARN at the hinge is expected). Flex it a few times after
  printing while warm-ish; do not print in PLA.
- Snap: 0.8 mm ridge into 1.0 mm V-groove; trim ridge if too tight.
"""

from build123d import *

from cadlib import *

META = dict(
    material="PETG",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # print exactly as modelled: open flat, hinge strip on bed
    supports="off",
    brim="auto",
)

# Parameters
WALL = 2.4            # outer walls
DIV = 2.0             # divider walls
FLOOR = 2.0
CHG = 68.0            # charger pocket (65 + 3 clearance)
INNER_H = 32.0        # interior depth (charger 30 + 2)
CABLE_W = 20.0        # cable channel width
N_CABLE = 3
COL_W = 30.0          # dongle / SD column width
SD_BLOCK_Y = 14.0     # SD block depth (Y)
SD_TOP = 22.0         # SD block top z
SD_SLOT_L, SD_SLOT_T, SD_SLOT_D = 26.0, 2.8, 20.0
NOTCH_R = 10.0        # finger notch radius in charger/cable divider
NOTCH_Z = 14.0        # notch bottom height above floor
LID_H = 8.0
LID_FLOOR = 2.0
CORNER_R = 3.0
HINGE_T = 0.65        # living hinge thickness (0.5 trips the <0.6 mm wall FAIL)
HINGE_W = 140.0       # hinge width (X)
TAB_W, TAB_T, TAB_EXTRA = 30.0, 1.6, 9.0  # snap tab: width, thickness, height above lid rim
RIDGE = 0.8           # snap ridge depth
GROOVE = 1.0          # groove depth in base front face

L = WALL + CHG + DIV + N_CABLE * CABLE_W + (N_CABLE - 1) * DIV + DIV + COL_W + WALL
W = WALL + CHG + WALL
H = FLOOR + INNER_H
GAP = H + LID_H       # hinge strip span so the lid folds flat on top
Y_BASE = -(W + GAP) / 2
Y_LID = (W + GAP) / 2


def _prism_x(y0, z0, d, length, direction):
    """Triangular 45° ridge/groove prism along X, apex at y0 + direction*d, height z0."""
    pts = [(y0, z0 - d), (y0 + direction * d, z0), (y0, z0 + d)]
    return extrude(Plane.YZ * Polygon(*pts, align=None), amount=length / 2, both=True)


def _base():
    b = rounded_box(L, W, H, radius=CORNER_R)
    x0 = -L / 2 + WALL
    # charger pocket
    b -= Pos(x0 + CHG / 2, 0, FLOOR) * Box(CHG, CHG, H, align=ON_BED)
    x = x0 + CHG + DIV
    div_x = x - DIV / 2
    # cable channels
    for _ in range(N_CABLE):
        b -= Pos(x + CABLE_W / 2, 0, FLOOR) * Box(CABLE_W, CHG, H, align=ON_BED)
        x += CABLE_W + DIV
    # finger notch through charger/cable divider
    b -= Pos(div_x, 0, FLOOR + NOTCH_Z) * Cylinder(NOTCH_R, H, align=ON_BED)
    # dongle pocket (back side) and SD block (front side)
    xc = x + COL_W / 2
    y_front = -CHG / 2
    dongle_y = CHG - SD_BLOCK_Y - DIV
    b -= Pos(xc, CHG / 2 - dongle_y / 2, FLOOR) * Box(COL_W, dongle_y, H, align=ON_BED)
    sd_y = y_front + SD_BLOCK_Y / 2
    b -= Pos(xc, sd_y, SD_TOP) * Box(COL_W, SD_BLOCK_Y, H, align=ON_BED)
    for dy in (-(SD_SLOT_T + DIV) / 2, (SD_SLOT_T + DIV) / 2):
        b -= Pos(xc, sd_y + dy, SD_TOP - SD_SLOT_D) * Box(SD_SLOT_L, SD_SLOT_T, H, align=ON_BED)
    # snap groove on front outer face; lid z maps to folded z = H + LID_H - z
    z_groove = H + LID_H - (LID_H + TAB_EXTRA * 0.55)
    b -= _prism_x(-W / 2, z_groove, GROOVE, TAB_W - 2 + 2 * GROOVE, +1)
    return Pos(0, Y_BASE, 0) * b


def _lid():
    lid = rounded_box(L, W, LID_H, radius=CORNER_R)
    lid -= Pos(0, 0, LID_FLOOR) * Box(L - 2 * WALL, W - 2 * WALL, LID_H, align=ON_BED)
    # snap tab on the far (front-when-closed) edge
    y_out = W / 2
    tab = Pos(0, y_out + TAB_T / 2, 0) * Box(TAB_W, TAB_T, LID_H + TAB_EXTRA, align=ON_BED)
    tab = chamfer(tab.edges().group_by(Axis.Z)[0], 0.4)
    lid += tab
    lid += _prism_x(y_out, LID_H + TAB_EXTRA * 0.55, RIDGE, TAB_W - 2, -1)
    return Pos(0, Y_LID, 0) * lid


def build() -> Part:
    y0 = Y_BASE + W / 2 - 1
    y1 = Y_LID - W / 2 + 1
    hinge = Pos(0, (y0 + y1) / 2, 0) * Box(HINGE_W, y1 - y0, HINGE_T, align=ON_BED)
    return _base() + _lid() + hinge
