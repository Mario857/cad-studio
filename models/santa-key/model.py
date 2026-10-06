"""santa-key: decorative "magic key for Santa" Christmas ornament (houses without chimneys).

Spec: flat key, 120 mm overall length (X), ornate round bow with a scalloped rim and a
five-pointed star inside the ring, a hanging loop with a ribbon hole at the bow end, a shaft
with raised text TEXT (>= 5 mm cap height, 0.6 mm raised), and a toothed bit at the far end.
Lies flat in use = prints flat on its back, support-free (no overhangs, no bridges).

Assumptions:
- Body thickness 4 mm (stiff enough for an ornament, light, fast to print).
- Ribbon hole 5 mm diameter (fits typical 3-6 mm ribbon / string).
- Text font Arial Bold, size 7.5 -> ~5.7 mm tall, ~48 mm long; single-colour emboss.
- Decorative only: no loads, not free-standing.
- 0.4 mm 45 deg bottom chamfer made by tapered extrude (edge chamfer fails on scallops).
- Thinnest spot ~1 mm is the text strokes / star-to-ring junctions (decorative, unloaded).
"""

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm. The audit picks the print orientation.
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # flat on its back, text up
    supports="off",
    brim="auto",
)

# Parameters
TEXT = "SANTA'S KEY"
TEXT_SIZE = 7.5          # font size -> ~5.7 mm cap height
TEXT_DEPTH = 0.6         # raised height
TEXT_CENTER_X = 73.0

LENGTH = 120.0           # overall length
THICK = 4.0              # body thickness
BOTTOM_CHAMFER = 0.4     # elephant-foot chamfer

# hanging loop (ribbon)
LOOP_R = 6.0
LOOP_X = LOOP_R          # loop starts at x=0
RIBBON_HOLE_D = 5.0

# bow
BOW_X = 26.0
BOW_R = 17.0             # outer ring radius
BOW_RING_W = 3.0         # ring width
SCALLOP_N = 10
SCALLOP_R = 3.2          # bumps on the rim
STAR_R_OUT = BOW_R - BOW_RING_W / 2   # star tips end mid-ring (clean merge)
STAR_R_IN = 5.5
STAR_HOLE_D = 3.0        # small centre hole in star

# shaft
SHAFT_W = 10.0
SHAFT_X0 = BOW_X + BOW_R - 2.0
COLLAR_L = 3.0
COLLAR_X = BOW_X + BOW_R + COLLAR_L / 2 - 1.0   # overlaps ring 1 mm
COLLAR_W = 15.0
TIP_CHAMFER = 2.0        # rounded/chamfered key tip

# bit (teeth), hanging below the shaft (-Y)
BIT_X0 = 100.0
BIT_L = 16.0
BIT_DEPTH = 13.0         # below shaft edge
NOTCH_W = 3.0
NOTCH_D = 5.0
NOTCH_XS = (104.0, 111.0)


def _star(r_out, r_in, n=5):
    import math
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(90 + i * 180 / n)
        pts.append((r * math.cos(a), r * math.sin(a)))
    return Polygon(*pts, align=None)


def _outline():
    import math
    # bow: ring + scallops + star
    bow = Pos(BOW_X, 0) * Circle(BOW_R)
    for i in range(SCALLOP_N):
        if i == SCALLOP_N // 2:
            continue  # the hanging loop sits there
        a = 2 * math.pi * i / SCALLOP_N
        bow += Pos(BOW_X + BOW_R * math.cos(a), BOW_R * math.sin(a)) * Circle(SCALLOP_R)
    bow -= Pos(BOW_X, 0) * Circle(BOW_R - BOW_RING_W)
    star = Pos(BOW_X, 0) * Rot(0, 0, 18) * _star(STAR_R_OUT, STAR_R_IN)
    star -= Pos(BOW_X, 0) * Circle(STAR_HOLE_D / 2)
    bow += star
    # hanging loop
    loop = Pos(LOOP_X, 0) * Circle(LOOP_R)
    loop -= Pos(LOOP_X, 0) * Circle(RIBBON_HOLE_D / 2)
    # shaft with collar
    shaft_l = LENGTH - SHAFT_X0
    shaft = Pos(SHAFT_X0 + shaft_l / 2, 0) * Rectangle(shaft_l, SHAFT_W)
    shaft += Pos(COLLAR_X, 0) * Rectangle(COLLAR_L, COLLAR_W)
    # bit
    tip = Pos(LENGTH, 0) * Rot(0, 0, 45) * Rectangle(TIP_CHAMFER * 2 ** 0.5, TIP_CHAMFER * 2 ** 0.5)
    shaft -= Pos(0, SHAFT_W / 2) * tip + Pos(0, -SHAFT_W / 2) * tip
    bit = Pos(BIT_X0 + BIT_L / 2, -(SHAFT_W / 2 + BIT_DEPTH) / 2) * Rectangle(BIT_L, SHAFT_W / 2 + BIT_DEPTH)
    for nx in NOTCH_XS:
        bit -= Pos(nx, -(SHAFT_W / 2 + BIT_DEPTH) + NOTCH_D / 2) * Rectangle(NOTCH_W, NOTCH_D)
    return bow + loop + shaft + bit


def build() -> Part:
    outline = _outline()
    # 45 deg elephant-foot chamfer as a tapered extrude (edge chamfer() fails on the
    # scalloped outline)
    base = Plane.XY.offset(BOTTOM_CHAMFER) * outline
    key = extrude(base, BOTTOM_CHAMFER, dir=(0, 0, -1), taper=45)
    key += extrude(base, THICK - BOTTOM_CHAMFER)
    txt = label(TEXT, size=TEXT_SIZE, depth=TEXT_DEPTH)
    bb = txt.bounding_box()
    txt = Pos(TEXT_CENTER_X - (bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, THICK) * txt
    return key + txt
