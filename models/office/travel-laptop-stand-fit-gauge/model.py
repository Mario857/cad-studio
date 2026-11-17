"""travel-laptop-stand-fit-gauge: comb of 7 hook slots for the front edge of a MacBook's base.

Feature under test: the hook slot of travel-laptop-stand over the laptop's base front edge (lid open).
Slot widths 10, 11, 12, 13, 14, 15, 16 mm (the number embossed under each slot is its width in mm),
each SLOT_DEPTH 10 mm deep, with a 0.6 mm lead-in chamfer, in a plate as thick as the real hook bar.
How to use: open the lid, slide each slot over the front edge of the palm rest near a corner, on BOTH
laptops. Report, per laptop, the smallest slot that goes on and off with no force and no scraping.
The stand's hook is then sized from the larger of the two.

Dimensions
  slot widths 10..16, step 1.0     MEASURED (modelled sizes, no compensation added: that is what is gauged)
  laptop base front-edge thickness UNVERIFIED (~11 guessed; the reason this gauge exists)
Assumptions: the edge is the same thickness along the front, so one corner is representative; the plate's
  5 mm thickness matches the planned hook bar.
Risks: a tight slot can scuff anodising - stop at the first resistance, do not force it. Elephant foot on
  the first layer makes slots read ~0.1 mm tight: try the slot from the top (embossed) side.
Accept: one slot per laptop slides on freely while the next smaller one does not.
"""

from build123d import *

from cadlib import *

META = dict(
    material="PLA",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="off",
)

SIZES = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0]   # slot widths (mm)
SLOT_DEPTH = 10.0     # how far the hook reaches onto the palm rest
TOOTH = 4.0           # wall between slots
SPINE = 9.0           # solid strip under the slots (carries the numbers)
PLATE_T = 5.0         # = planned hook bar thickness
LEAD_IN = 0.6         # chamfer at each slot mouth
NUM_SIZE = 5.5
NUM_H = 0.6


def build() -> Part:
    length = sum(SIZES) + TOOTH * (len(SIZES) + 1)
    height = SPINE + SLOT_DEPTH
    part = Pos(length / 2, height / 2, 0) * Box(length, height, PLATE_T, align=ON_BED)
    part = fillet(part.edges().filter_by(Axis.Z), 1.5)
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)

    x = TOOTH
    for size in SIZES:
        # slot open towards +Y, with a chamfered mouth
        mouth = Polygon((x, SPINE), (x + size, SPINE), (x + size, height - LEAD_IN), (x + size + LEAD_IN, height + 0.01),
                        (x - LEAD_IN, height + 0.01), (x, height - LEAD_IN), align=None)
        part -= Pos(0, 0, -1) * extrude(mouth, PLATE_T + 2)
        text = label(f"{size:g}", size=NUM_SIZE, depth=NUM_H)
        box = text.bounding_box()
        part += Pos(x + size / 2 - (box.min.X + box.max.X) / 2, SPINE / 2 - (box.min.Y + box.max.Y) / 2, PLATE_T) * text
        x += size + TOOTH
    return part
