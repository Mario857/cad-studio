"""battery-organizer: free-standing tray for 12x AA, 12x AAA and 4x 9V / CR2032 coin slots.

Spec: solid block with round pockets, batteries stand upright and stick out about half
their length, so they are easy to grab (no extra notches needed). From front (-Y) to back:
  row 0   : 4 rectangular slots 27.5 x 18.5 (9V stands upright; CR2032 coins lie stacked)
  rows 1-2: 2 x 6 AAA pockets (D 11.0, 22 mm deep, ~half of 44.5)
  rows 3-4: 2 x 6 AA pockets  (D 15.0, 25 mm deep, ~half of 50.5)
Pockets have a 1 mm lead-in chamfer. "AA" / "AAA" / "9V" are engraved 0.6 mm in the left
top margin. Prints as modelled: flat bottom on the bed, pockets open upward, zero supports.
Assumptions: AA 14.5 x 50.5, AAA 10.5 x 44.5, 9V 26.5 x 17.5 x 48.5, CR2032 20 x 3.2 mm;
slide fit = +0.25 mm radial on cells (pocket D = cell D + 0.5); 9V slot = +1 mm per side.
Solid body (low infill is fine, it is only a holder); ~half height so it cannot tip.
"""

from build123d import *

from cadlib import *

META = dict(
    material="PLA",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 0, 40), grams=600)],  # 24 loaded cells, roughly
    print_orientation="auto",
    supports="off",
    brim="auto",
)

# Parameters
WALL = 2.5
HEIGHT = 28.5
FLOOR_MIN = 2.5

AA_D, AA_L = 14.5, 50.5
AAA_D, AAA_L = 10.5, 44.5
SLIDE = 0.5                      # diametral slide clearance
AA_POCKET = AA_D + SLIDE
AAA_POCKET = AAA_D + SLIDE
AA_DEPTH = 25.0                  # ~half of 50.5
AAA_DEPTH = 22.0                 # ~half of 44.5

SLOT_X, SLOT_Y, SLOT_DEPTH = 27.5, 18.5, 26.0   # 9V footprint + clearance
N_SLOTS = 4
LEAD_IN = 1.0

ROW_PITCH_AA = AA_POCKET + WALL
ROW_PITCH_AAA = AAA_POCKET + WALL
N_PER_ROW = 6
LABEL_MARGIN = 14.0
TEXT_SIZE = 5.0

SLOT_REGION = N_SLOTS * (SLOT_X + WALL) + WALL
LENGTH = LABEL_MARGIN + SLOT_REGION
# Y layout from the front edge (y measured from front, converted below)
Y_SLOT = WALL + SLOT_Y / 2
Y_AAA1 = WALL + SLOT_Y + WALL + AAA_POCKET / 2
Y_AAA2 = Y_AAA1 + ROW_PITCH_AAA
Y_AA1 = Y_AAA2 + AAA_POCKET / 2 + WALL + AA_POCKET / 2
Y_AA2 = Y_AA1 + ROW_PITCH_AA
DEPTH = Y_AA2 + AA_POCKET / 2 + WALL


def round_pocket(d, depth, x, y):
    """Vertical round pocket from the top with a lead-in chamfer."""
    body = Pos(x, y, HEIGHT - depth) * Cylinder(d / 2, depth + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cone = Pos(x, y, HEIGHT - LEAD_IN) * Cone(d / 2, d / 2 + LEAD_IN + 0.01, LEAD_IN + 0.01,
                                              align=(Align.CENTER, Align.CENTER, Align.MIN))
    return body + cone


def build() -> Part:
    x0 = -LENGTH / 2
    y0 = -DEPTH / 2
    part = rounded_box(LENGTH, DEPTH, HEIGHT, radius=3, bottom_chamfer=0.4)

    # pocket grid X range (right of the label margin)
    gx0 = x0 + LABEL_MARGIN + WALL
    gw = SLOT_REGION - 2 * WALL
    pitch_x = (gw + WALL) / N_PER_ROW
    cx = [gx0 + (i + 0.5) * pitch_x - WALL / 2 for i in range(N_PER_ROW)]

    for yy, d, dep in ((Y_AAA1, AAA_POCKET, AAA_DEPTH), (Y_AAA2, AAA_POCKET, AAA_DEPTH),
                       (Y_AA1, AA_POCKET, AA_DEPTH), (Y_AA2, AA_POCKET, AA_DEPTH)):
        for x in cx:
            part = part - round_pocket(d, dep, x, y0 + yy)

    # 9V / coin slots
    for i in range(N_SLOTS):
        x = x0 + LABEL_MARGIN + WALL + SLOT_X / 2 + i * (SLOT_X + WALL)
        slot_cut = Pos(x, y0 + Y_SLOT, HEIGHT - SLOT_DEPTH) * extrude(
            RectangleRounded(SLOT_X, SLOT_Y, 2.0), SLOT_DEPTH + 0.01)
        part = part - slot_cut
        lead = Pos(x, y0 + Y_SLOT, HEIGHT - LEAD_IN) * loft([
            Plane.XY * RectangleRounded(SLOT_X, SLOT_Y, 2.0),
            Plane.XY.offset(LEAD_IN + 0.01) * RectangleRounded(SLOT_X + 2 * LEAD_IN + 0.02, SLOT_Y + 2 * LEAD_IN + 0.02, 3.0),
        ])
        part = part - lead

    # engraved labels in the left margin
    lx = x0 + LABEL_MARGIN / 2 + 0.5
    for text, yy in (("AA", (Y_AA1 + Y_AA2) / 2), ("AAA", (Y_AAA1 + Y_AAA2) / 2), ("9V", Y_SLOT)):
        part = part - Pos(lx, y0 + yy, HEIGHT - 0.6) * label(text, size=TEXT_SIZE, depth=0.6 + 0.01)
    return part
