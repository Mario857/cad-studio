"""cash-drawer-insert: 300x200 mm till insert, 5 upright note slots + 8 scooped coin cups, labelled.

Spec: drop-in insert (298x198 mm, 1 mm play per side) for a cash drawer with a 300x200 mm inner floor. Back section: 5 note
compartments (5, 10, 20, 50, 100) ~57 mm wide x 154 mm long; notes stand on their long edge
(up to 147 mm long, 62-77 mm tall) so their top edges stick out 17-32 mm above the 45 mm rim,
easy to flick through. Front row: 8 coin cups (1c..2E) 35 x 30 mm, 43 mm deep with a 12 mm
scooped bottom so coins slide out with one finger. Labels (6 mm text, 0.6 mm engraved) sit on two
7 mm wide label bands: front band for coins, middle band (in front of each note slot) for notes.
Prints open side up, no supports; rotated 90 deg on the bed (300 mm runs along the 320 mm axis).

MEASURE BEFORE PRINTING: inner floor of your drawer (DRAWER_L x DRAWER_W), €100/€200 note length
(147/153 mm; €200 needs NOTE_LEN 156), largest coin €2 25.75 mm (must fit COIN_Y).
Assumptions: drawer inner >= 300x200x45 mm; notes stored upright rather than flat (5 flat €100
notes need >= 390 mm width, which 300 mm cannot give). '€' rendered as 'E' to be font-safe.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 90),  # long side along the 320 mm bed axis
    supports="off",
    brim="on",                     # large flat ABS footprint
)

# Parameters
DRAWER_L = 300.0         # X, drawer inner width
DRAWER_W = 200.0         # Y, drawer inner depth
FIT_GAP = 2.0            # total play per axis (also keeps it inside the H2C single-nozzle area)
OUTER_L = DRAWER_L - FIT_GAP
OUTER_W = DRAWER_W - FIT_GAP
HEIGHT = 45.0
CORNER_R = 4.0
WALL = 2.0               # outer + divider walls
FLOOR = 2.0
FRONT_BAND = 7.0         # coin label band (solid, full height)
MID_BAND = 7.0           # note label band between coins and notes
COIN_Y = 30.0            # coin cup depth front-to-back (>= 25.75 + slack)
COIN_SCOOP_R = 12.0      # scooped bottom radius of coin cups
N_COINS = 8
N_NOTES = 5
TEXT_SIZE = 6.0
TEXT_DEPTH = 0.6
COIN_LABELS = ["1c", "2c", "5c", "10c", "20c", "50c", "1E", "2E"]
NOTE_LABELS = ["5", "10", "20", "50", "100"]


def _cell_cutter(lx, ly, depth, bottom_r):
    """Cell cutter pointing down from z=0; bottom rounded front-to-back (scoop), square in X."""
    prof = Rectangle(ly, depth, align=(Align.CENTER, Align.MAX))
    prof = fillet(prof.vertices().group_by(Axis.Y)[0], bottom_r)
    return extrude(Plane.YZ * prof, lx / 2, both=True)


def _row_centers(n):
    cell = (OUTER_L - 2 * WALL - (n - 1) * WALL) / n
    x0 = -OUTER_L / 2 + WALL + cell / 2
    return cell, [x0 + i * (cell + WALL) for i in range(n)]


def build() -> Part:
    part = rounded_box(OUTER_L, OUTER_W, HEIGHT, radius=CORNER_R)
    labels, cells = [], []
    y_front = -OUTER_W / 2
    depth = HEIGHT - FLOOR

    # coin cups
    coin_x, xs = _row_centers(N_COINS)
    coin_cy = y_front + FRONT_BAND + COIN_Y / 2
    for x, t in zip(xs, COIN_LABELS):
        cells.append(Pos(x, coin_cy, HEIGHT) * _cell_cutter(coin_x, COIN_Y, depth, COIN_SCOOP_R))
        labels.append(Pos(x, y_front + FRONT_BAND / 2, HEIGHT - TEXT_DEPTH) * label(t, size=TEXT_SIZE, depth=TEXT_DEPTH + 0.1))

    # note slots
    note_y0 = y_front + FRONT_BAND + COIN_Y + MID_BAND
    note_len = OUTER_W / 2 - WALL - note_y0
    note_x, xs = _row_centers(N_NOTES)
    for x, t in zip(xs, NOTE_LABELS):
        cells.append(Pos(x, note_y0 + note_len / 2, HEIGHT) * _cell_cutter(note_x, note_len, depth, 3))
        labels.append(Pos(x, note_y0 - MID_BAND / 2, HEIGHT - TEXT_DEPTH) * label(t, size=TEXT_SIZE, depth=TEXT_DEPTH + 0.1))
    for c in labels + cells:  # engrave first, then cut cells (keeps the mesh watertight)
        part -= c
    return part
