"""stamp-rack: desk rack for 6 rubber stamps plus an ink-pad bay, with labelled slots.

Spec: 2 x 3 conical sockets hold stamps handle-down (rubber face up stays clean and readable);
the cone self-centres any knob/handle from Ø20 to Ø30 mm. Each socket has an engraved label
(STAMP_LABELS) in front of it. A lower front bay holds a standard ink pad, with finger notches on
both sides to lift it out.

Assumptions: stamp handles Ø20-30 mm, stamp bodies <= SOCKET_PITCH_X wide; ink pad 110 x 70 x 15 mm.
MEASURE BEFORE PRINTING: handle diameters, widest stamp body, ink pad L x W x H.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 30, 60), grams=600)],   # 6 stamps ~100 g each
    print_orientation="auto",
    supports="auto",
    brim="on",                 # ABS, 160 x 200 mm block footprint
)

STAMP_LABELS = ["PAID", "COPY", "RECVD", "DATE", "URGENT", "FILED"]

# Stamps / fits
HANDLE_MAX_D = 30.0
HANDLE_MIN_D = 20.0
SOCKET_CLEAR = 1.5     # on diameter, at the top
SOCKET_DEPTH = 24.0
SOCKET_PITCH_X = 50.0
SOCKET_PITCH_Y = 55.0
COLS, ROWS = 3, 2

# Ink pad / fits
INK_L = 110.0
INK_W = 70.0
INK_H = 15.0
INK_CLEAR = 1.0        # per side
NOTCH_D = 26.0

# Body
MARGIN = 6.0
FLOOR = 3.0
CORNER_R = 6.0
TEXT_SIZE = 5.0
TEXT_DEPTH = 0.6
LABEL_DY = -22.0       # label centre from socket centre (toward the front)

WIDTH = COLS * SOCKET_PITCH_X + 2 * MARGIN
RACK_D = ROWS * SOCKET_PITCH_Y + MARGIN
RACK_H = SOCKET_DEPTH + FLOOR
BAY_D = INK_W + 2 * INK_CLEAR + 2 * MARGIN
BAY_H = INK_H - 2 + FLOOR   # pad sticks out 2 mm for grip


def build() -> Part:
    depth = RACK_D + BAY_D
    y_front = -depth / 2
    y_split = y_front + BAY_D
    rack = Pos(0, (y_split + depth / 2) / 2, 0) * rounded_box(WIDTH, depth / 2 - y_split, RACK_H, radius=CORNER_R)
    bay = Pos(0, (y_front + y_split) / 2 + 3, 0) * rounded_box(WIDTH, BAY_D + 6, BAY_H, radius=CORNER_R)
    part = rack + bay

    # ink pad pocket with finger notches
    cy = y_front + BAY_D / 2
    pl, pw = INK_L + 2 * INK_CLEAR, INK_W + 2 * INK_CLEAR
    pocket = Pos(0, cy, FLOOR) * Box(pl, pw, 50, align=ON_BED)
    pocket = fillet(pocket.edges().filter_by(Axis.Z), 4)
    for sx in (-1, 1):
        pocket += Pos(sx * pl / 2, cy, FLOOR) * Cylinder(NOTCH_D / 2, 50, align=ON_BED)
    part -= pocket

    # conical sockets + engraved labels
    r_top = (HANDLE_MAX_D + SOCKET_CLEAR) / 2
    r_bot = (HANDLE_MIN_D - 2) / 2
    for i, text in enumerate(STAMP_LABELS[: COLS * ROWS]):
        r, c = divmod(i, COLS)
        x = (c - (COLS - 1) / 2) * SOCKET_PITCH_X
        y = y_split + MARGIN / 2 + (r + 0.5) * SOCKET_PITCH_Y + 4
        sock = Pos(x, y, RACK_H - SOCKET_DEPTH) * Cone(r_bot, r_top, SOCKET_DEPTH + 0.01, align=ON_BED)
        sock += Pos(x, y, RACK_H) * Cylinder(r_top, 1, align=ON_BED)
        part -= sock
        part -= Pos(x, y + LABEL_DY, RACK_H - TEXT_DEPTH) * label(text, size=TEXT_SIZE, depth=TEXT_DEPTH + 0.1)
    return part
