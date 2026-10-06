"""place-card-holder: five-point star table place-card holder (Christmas decoration).

Spec: a solid 5-point star (point toward +Y) lying flat on the table, with a vertical through-slot
along X that holds a 90 x 55 mm place card upright (card's long edge along X). Top edges chamfered
for a faceted look; 0.4 mm elephant-foot chamfer on the bed edge. Printed flat, no supports.
Set of 6 printed together (META copies).

Assumptions:
- Card stock <= 0.5 mm thick; slot width = clearance(CARD_T, SLOT_FIT) ("slide" -> 1.0 mm, so the card
  slides in without scuffing; 8 mm deep slot limits lean to ~3.5 deg).
- Card stands with its 90 mm edge in the slot (landscape); card centre ~5 g at slot-bottom + 27.5 mm.
- Star outer radius 32 mm (64 mm tip to tip) is a pleasant table size and gives a wide base.
"""

import math

from build123d import *

from cadlib import *

# Card / fit
CARD_W = 90.0          # card length along slot (X)
CARD_H = 55.0          # card height standing up
CARD_T = 0.5           # card stock thickness (max)
SLOT_FIT = "slide"     # clearance class for the card slot (-> 1.0 mm slot)
SLOT_W = clearance(CARD_T, SLOT_FIT)
SLOT_DEPTH = 8.0       # how deep the card sits
CARD_GRAMS = 5.0

# Star
STAR_POINTS = 5
STAR_R_OUT = 32.0      # tip radius
STAR_R_IN = 14.0       # valley radius
STAR_H = 12.0          # thickness (height on table)
TOP_CHAMFER = 1.5      # decorative top-edge chamfer
BOTTOM_CHAMFER = 0.4   # elephant foot

SLOT_FLOOR_Z = STAR_H - SLOT_DEPTH

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0.0, 0.0, SLOT_FLOOR_Z + CARD_H / 2), grams=CARD_GRAMS)],
    print_orientation="auto",
    supports="off",
    brim="auto",
    copies=6,
)


def star_outline() -> Polygon:
    pts = []
    for i in range(2 * STAR_POINTS):
        r = STAR_R_OUT if i % 2 == 0 else STAR_R_IN
        a = math.radians(90 + i * 180 / STAR_POINTS)
        pts.append((r * math.cos(a), r * math.sin(a)))
    return Polygon(*pts, align=None)


def build() -> Part:
    star = extrude(Plane.XY * star_outline(), STAR_H)
    star = chamfer(star.edges().group_by(Axis.Z)[-1], TOP_CHAMFER)
    star = chamfer(star.edges().group_by(Axis.Z)[0], BOTTOM_CHAMFER)
    slot = Pos(0, 0, SLOT_FLOOR_Z) * Box(2 * STAR_R_OUT + 10, SLOT_W, SLOT_DEPTH + 1, align=ON_BED)
    return star - slot
