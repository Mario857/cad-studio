"""bill-due-board: wall board with day pegs 1-31 and movable press-fit bill markers.

Spec: 7 x 5 calendar grid (days 1-31) with a raised day number and a Ø6 peg in each cell, header
"BILLS DUE", two keyhole slots for wall screws. 10 marker tags (RENT, POWER, ...) with a press-fit
hole slide onto the peg of the day the bill is due; pegs are long enough for 3 stacked markers.
Modeled in print coordinates (board back on the bed, pegs up) and rotated to in-use (vertical
on the wall, pegs toward -Y) at the end; markers are laid out below the board, coplanar.

Assumptions: wall screws Ø3.5-4 mm, head <= 8.5 mm. Marker hole fit tuned by MARKER_FIT.
MEASURE BEFORE PRINTING: screw head diameter.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",              # large board; marker fit tuned via MARKER_FIT
    standing=False,
    loads=[],
    print_orientation=(-90, 0, 0),   # board back on the bed, pegs and text up
    supports="off",                  # only the 9.4 mm keyhole head-channel bridge at the bed
    brim="on",                        # ABS, 268 x 196 mm flat board
)

MARKERS = ["RENT", "POWER", "WATER", "PHONE", "NET", "CARD", "LOAN", "INSUR", "TAX", "GAS"]

# Grid
COLS, ROWS = 7, 5
PITCH_X = 36.0
PITCH_Y = 32.0
MARGIN = 8.0
HEADER_H = 24.0
BOARD_T = 5.0
CORNER_R = 6.0
NUM_SIZE = 7.0
HEAD_SIZE = 10.0
TEXT_DEPTH = 0.6

# Pegs / markers (fits)
PEG_D = 6.0
PEG_L = 11.0           # 3 markers x 3 mm + 2 mm
PEG_DY = -7.0          # peg centre below cell centre
NUM_DY = 7.5           # number centre above cell centre
MARKER_FIT = 0.15      # snug press fit on the peg
MARKER_W = 34.0
MARKER_H = 13.0
MARKER_T = 3.0
MARKER_TEXT = 5.0
MARKER_HOLE_X = -11.0  # hole offset from marker centre

# Keyholes (fits)
KH_HEAD_D = 9.0
KH_SLOT_W = 4.6
KH_SLOT_L = 10.0
KH_RECESS = 2.5

BOARD_W = COLS * PITCH_X + 2 * MARGIN
BOARD_H = ROWS * PITCH_Y + HEADER_H + 2 * MARGIN


def make_board() -> Part:
    board = Pos(0, BOARD_H / 2, 0) * rounded_box(BOARD_W, BOARD_H, BOARD_T, radius=CORNER_R)
    board = fillet(board.edges().group_by(Axis.Z)[-1], 1.0)
    top = BOARD_T
    y_hdr = BOARD_H - MARGIN - HEADER_H / 2
    board += Pos(0, y_hdr, top - 0.01) * label("BILLS DUE", size=HEAD_SIZE, depth=TEXT_DEPTH)
    for d in range(31):
        r, c = divmod(d, COLS)
        x = (c - (COLS - 1) / 2) * PITCH_X
        y = BOARD_H - MARGIN - HEADER_H - (r + 0.5) * PITCH_Y
        board += Pos(x, y + NUM_DY, top - 0.01) * label(str(d + 1), size=NUM_SIZE, depth=TEXT_DEPTH)
        peg = Pos(x, y + PEG_DY, top - 0.01) * Cylinder(PEG_D / 2, PEG_L, align=ON_BED)
        board += chamfer(peg.edges().group_by(Axis.Z)[-1], 0.6)

    # keyholes left/right of the header: slot above the entry (board slides down onto the screw)
    for sx in (-1, 1):
        x = sx * (BOARD_W / 2 - 22)
        y0 = y_hdr - KH_SLOT_L / 2
        cut = Pos(x, y0, -1) * Cylinder(KH_HEAD_D / 2, BOARD_T + 2, align=ON_BED)
        cut += Pos(x, y0 + KH_SLOT_L / 2, -1) * Box(KH_SLOT_W, KH_SLOT_L, BOARD_T + 2, align=ON_BED)
        cut += Pos(x, y0 + KH_SLOT_L, -1) * Cylinder(KH_SLOT_W / 2, BOARD_T + 2, align=ON_BED)
        w = KH_HEAD_D + 0.4
        cut += Pos(x, y0 + KH_SLOT_L / 2, -1) * Box(w, KH_SLOT_L + w, KH_RECESS + 1, align=ON_BED)
        board -= cut
    return board


def make_marker(text: str) -> Part:
    m = rounded_box(MARKER_W, MARKER_H, MARKER_T, radius=MARKER_H / 2 - 0.5)
    m -= Pos(MARKER_HOLE_X, 0, MARKER_T + 1) * pin_hole(PEG_D + MARKER_FIT, MARKER_T + 2)
    x_txt = (MARKER_HOLE_X + PEG_D / 2 + 1.5 + MARKER_W / 2 - 2) / 2   # centre of the area right of the hole
    m += Pos(x_txt, 0, MARKER_T - 0.01) * label(text, size=MARKER_TEXT, depth=TEXT_DEPTH)
    return m


def build():
    parts = [make_board()]
    for i, t in enumerate(MARKERS):
        r, c = divmod(i, 5)
        x = (c - 2) * (MARKER_W + 6)
        y = -12 - r * (MARKER_H + 6)
        parts.append(Pos(x, y, 0) * make_marker(t))
    return [Rot(90, 0, 0) * p for p in parts]      # print coords -> in-use (vertical, pegs to -Y)
