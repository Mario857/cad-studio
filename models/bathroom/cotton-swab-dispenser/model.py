"""cotton-swab-dispenser: two-compartment countertop box with a lift-off lid.

Spec: left compartment holds a stack of 60 mm round cotton pads (64 mm square pocket),
right compartment holds 75 mm cotton swabs LYING FLAT, long axis along Y (front-to-back),
in an 80 mm long pocket. A lift-off lid with an inner skirt drops into the box opening
(slide fit via clearance(), FIT param); the divider stops below the skirt. The lid plate
overhangs the box walls by LID_OVERHANG so it can be gripped and lifted.
Printed together: box upright, lid upside-down (plate on bed, skirt up) beside it.
Assumptions: pads up to ~60 mm tall stack (about 80-100 pads); swabs lie flat so they
can be grabbed from the top, ~45 mm wide pile (~150 swabs). No supports needed.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[],
    print_orientation="auto",
    supports="off",
    brim="auto",
)

# Parameters
PAD_D = 60.0             # cotton pad diameter
PAD_POCKET = 64.0        # pad compartment interior (square, X and Y)
SWAB_L = 75.0            # cotton swab length
SWAB_POCKET_W = 45.0     # swab compartment interior width (X)
INNER_Y = 80.0           # interior depth (Y) of both compartments, >= SWAB_L + 5
WALL = 2.4               # outer walls and divider
FLOOR = 2.0
INNER_H = 62.0           # interior height (floor to rim)
CORNER_R = 5.0           # outer corner radius
FIT = "slide"            # lid skirt fit in box opening
SKIRT_H = 8.0            # lid skirt depth into box
SKIRT_T = 2.0            # lid skirt wall thickness
DIVIDER_GAP = 1.0        # divider top stops this far below skirt bottom
LID_T = 3.0              # lid plate thickness
LID_OVERHANG = 1.5       # lid plate overhang beyond box walls (grip lip)
LID_EDGE_CHAMFER = 1.0   # chamfer on lid top edges (in use)
GAP = 10.0               # spacing between box and lid on the bed

INNER_X = PAD_POCKET + WALL + SWAB_POCKET_W
OUTER_X = INNER_X + 2 * WALL
OUTER_Y = INNER_Y + 2 * WALL
OUTER_H = FLOOR + INNER_H
INNER_R = CORNER_R - WALL


def _rr(l, w, r, h, z=0.0):
    return Pos(0, 0, z) * extrude(RectangleRounded(l, w, r), h)


def build():
    # Box
    box = rounded_box(OUTER_X, OUTER_Y, OUTER_H, radius=CORNER_R)
    box -= _rr(INNER_X, INNER_Y, INNER_R, INNER_H + 1, FLOOR)
    div_h = INNER_H - SKIRT_H - DIVIDER_GAP
    div_x = -INNER_X / 2 + PAD_POCKET + WALL / 2
    box += Pos(div_x, 0, FLOOR - 0.5) * Box(WALL, INNER_Y + 0.2, div_h + 0.5, align=ON_BED)

    # Lid (modelled in print orientation: plate on bed, skirt pointing up)
    gap = clearance(INNER_X, FIT) - INNER_X   # total diametral clearance
    sk_x, sk_y = INNER_X - gap, INNER_Y - gap
    sk_r = max(INNER_R - gap / 2, 0.5)
    lid_x, lid_y = OUTER_X + 2 * LID_OVERHANG, OUTER_Y + 2 * LID_OVERHANG
    lid = _rr(lid_x, lid_y, CORNER_R + LID_OVERHANG, LID_T)
    lid = chamfer(lid.edges().group_by(Axis.Z)[0], LID_EDGE_CHAMFER)
    skirt = _rr(sk_x, sk_y, sk_r, SKIRT_H, LID_T) - _rr(
        sk_x - 2 * SKIRT_T, sk_y - 2 * SKIRT_T, max(sk_r - SKIRT_T, 0.5), SKIRT_H + 1, LID_T)
    lid += skirt
    lid = Pos(0, OUTER_Y / 2 + GAP + lid_y / 2, 0) * lid
    return [box, lid]
