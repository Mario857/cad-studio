"""banknote-sorter-tray: stepped 6-slot sorter for €5-€200 notes, each denomination visible.

Spec: staircase block with 6 slots, one per note (5, 10, 20, 50, 100, 200), front to back.
Each note stands on its long edge and leans back 10 deg, lying flat against the slot's back
wall. Slot floors are stepped so every note's top edge sits VIS_STEP (12 mm) higher than the note
in front of it -> each denomination shows a 12 mm strip (back notes) or fully (front €5).
Slots are cut to the note's own length + SLOT_LEN_CLEAR and hold a stack SLOT_W thick.
Labels (6 mm, 0.6 mm engraved) on an 11 mm tread in front of each slot.
Prints flat on its base, no supports (slot faces lean 10 deg).

MEASURE BEFORE PRINTING: note sizes €5 120x62, €10 127x67, €20 133x72, €50 140x77,
€100 147x77, €200 153x77 mm (NOTES table).
Assumptions: ~70 notes per slot (SLOT_W 8 mm); used on a counter/desk, notes stood upright.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="auto",
)

# Parameters
NOTES = [("5", 120, 62), ("10", 127, 67), ("20", 133, 72),
         ("50", 140, 77), ("100", 147, 77), ("200", 153, 77)]   # label, length, height (mm)
SLOT_LEN_CLEAR = 3.0     # total length play per slot
SLOT_W = 8.0             # stack thickness per slot
TILT = 10.0              # lean-back angle of the notes (deg)
TREAD = 11.0             # label tread in front of each slot
BACK_WALL = 8.0
END_WALL = 4.0           # material left at each end of the longest slot
HOLD = 20.0              # slot depth (how much of the note is gripped)
FLOOR = 3.0              # floor under the front slot
VIS_STEP = 12.0          # visible strip of each note above the one in front
TEXT_SIZE = 6.0
TEXT_DEPTH = 0.6


def build() -> Part:
    length = max(n[1] for n in NOTES) + SLOT_LEN_CLEAR + 2 * END_WALL
    pitch = TREAD + SLOT_W
    depth = len(NOTES) * pitch + BACK_WALL
    y0 = -depth / 2
    c = math.cos(math.radians(TILT))

    top0 = FLOOR + NOTES[0][2] * c
    floors = [top0 + i * VIS_STEP - h * c for i, (_, _, h) in enumerate(NOTES)]
    tops = [f + HOLD for f in floors]

    part = None
    for i, t in enumerate(tops):
        ys = y0 + i * pitch
        step = Pos(0, (ys + depth / 2) / 2, 0) * Box(length, depth / 2 - ys, t, align=(Align.CENTER, Align.CENTER, Align.MIN))
        part = step if part is None else part + step
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)

    for i, ((txt, ln, _), f, t) in enumerate(zip(NOTES, floors, tops)):
        ys = y0 + i * pitch
        # slot cutter: parallelogram leaning back, runs up through the next (higher) riser so
        # that riser's face continues the lean (no ledge/overhang)
        yf = ys + TREAD
        ztop = (tops[i + 1] if i + 1 < len(tops) else t) + 1
        sh = (ztop - f) * math.tan(math.radians(TILT))
        prof = Polygon((yf, f), (yf + SLOT_W, f), (yf + SLOT_W + sh, ztop), (yf + sh, ztop), align=None)
        cut = extrude(Plane.YZ * prof, (ln + SLOT_LEN_CLEAR) / 2, both=True)
        part -= cut
        part -= Pos(0, ys + TREAD / 2 - 2.5, t - TEXT_DEPTH) * label(txt, size=TEXT_SIZE, depth=TEXT_DEPTH + 0.1)
    return part
