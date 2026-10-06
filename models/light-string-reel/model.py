"""light-string-reel: flat H-shaped winder for ~20 m of Christmas light string.

Spec: one-piece flat board (prints flat, zero supports). The light string is wound
lengthwise through the two end notches, around the board's waist (like a kite-line
winder). A hand slot in the wide side rail is the carry handle (stays free of cable).
The narrow side rail has a cord-clip slot at each end: snap the plug (start) end into
one, and the socket/far end into the other once wound. A large window in the middle
saves material (the cable spans it).

Capacity: notch 100 (Y) x 40 (X) = 4000 mm2 cable cross-section per side. Loop length
~2 x 210 mm inner span + pile growth ~ 0.5 m avg -> 20 m ~ 40 loops x 64 mm2 / 0.8
packing ~ 3200 mm2 < 4000 mm2. Wound pile on each face ~35-40 mm high.

Assumptions:
- Light-string bundle effective diameter 8 mm incl. bulbs (wire + bulb sockets).
- Bare lead / plug-cord diameter ~4.5-5 mm (twin wire); clip slot 4.0 wide grips it.
- Plate 300x320: board 290 x 175 x 8 mm lies flat, X along the 300 side.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,            # hand-carried / stored lying or hanging
    loads=[],
    print_orientation="auto",  # flat on bed
    supports="auto",
    brim="auto",
)

# Parameters
LENGTH = 290.0          # overall, X (along winding direction)
THICK = 8.0             # board thickness
NOTCH_W = 100.0         # cable channel width (Y)
NOTCH_D = 40.0          # notch depth from each end (X)
NOTCH_R = 10.0          # notch inner corner radius (cable bend)
RAIL_A = 25.0           # narrow side rail width (cord clips)
RAIL_B = 50.0           # wide side rail width (carry handle)
CORNER_R = 4.0          # convex corner rounding
EDGE_FILLET = 1.5       # top edge rounding (cable-friendly)
BOTTOM_CHAMFER = 0.4    # elephant foot

WINDOW_L = 180.0        # central lightening window
WINDOW_W = 76.0
WINDOW_R = 15.0

HANDLE_L = 110.0        # hand slot in rail B
HANDLE_W = 28.0

CORD_D = 4.5            # assumed lead cord diameter
CORD_FIT = -0.5         # negative = interference so the cord clicks in and stays
CLIP_W = CORD_D + CORD_FIT   # 4.0 slot width
CLIP_LEN = 18.0         # slot length from the end edge
CLIP_SEAT_D = CORD_D + 0.5   # round seat at slot bottom
CLIP_ENTRY = 2.0        # chamfer half-width at slot mouth

WIDTH = RAIL_A + NOTCH_W + RAIL_B
Y0 = -WIDTH / 2                     # board spans Y0 .. -Y0
Y_NOTCH = Y0 + RAIL_A + NOTCH_W / 2  # notch / cable channel centre
Y_RAIL_A = Y0 + RAIL_A / 2
Y_RAIL_B = Y0 + RAIL_A + NOTCH_W + RAIL_B / 2


def outline() -> Sketch:
    s = Rectangle(LENGTH, WIDTH)
    for sx in (-1, 1):
        s -= Pos(sx * LENGTH / 2, Y_NOTCH) * RectangleRounded(2 * NOTCH_D, NOTCH_W, NOTCH_R)
        # cord clip: slot with a flared mouth and round seat
        x_end = sx * LENGTH / 2
        s -= Pos(x_end - sx * CLIP_LEN / 2, Y_RAIL_A) * Rectangle(CLIP_LEN, CLIP_W)
        s -= Pos(x_end - sx * CLIP_LEN, Y_RAIL_A) * Circle(CLIP_SEAT_D / 2)
        s -= Polygon(
            (x_end + sx * 0.1, Y_RAIL_A - CLIP_W / 2 - CLIP_ENTRY),
            (x_end + sx * 0.1, Y_RAIL_A + CLIP_W / 2 + CLIP_ENTRY),
            (x_end - sx * 3.0, Y_RAIL_A + CLIP_W / 2),
            (x_end - sx * 3.0, Y_RAIL_A - CLIP_W / 2),
            align=None,
        )
    # round convex corners
    s = offset(offset(s, -CORNER_R), CORNER_R)
    s -= Pos(0, Y_NOTCH) * RectangleRounded(WINDOW_L, WINDOW_W, WINDOW_R)
    s -= Pos(0, Y_RAIL_B) * SlotOverall(HANDLE_L, HANDLE_W)
    return s


def build() -> Part:
    part = extrude(Plane.XY * outline(), THICK)
    part = fillet(part.edges().group_by(Axis.Z)[-1], EDGE_FILLET)
    part = chamfer(part.edges().group_by(Axis.Z)[0], BOTTOM_CHAMFER)
    return part
