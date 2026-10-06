"""a4-document-tray: stackable A4 letter tray with front scoop and stacking posts.

Spec: inner floor A4 + 10 mm (220 x 307 mm), long side front-to-back, low front wall with a wide
U-scoop to grab sheets. Four stacking posts on the outside of the side walls rise STACK_PITCH
above the floor and end in Ø8 pins; each post has a matching socket underneath, so any number of
trays stack with a 25 mm hand gap. Large floor windows save plastic and reduce ABS warping.
One piece: 241 x 312 mm fits the 300 x 320 plate, so no split is needed.

Assumptions: paper A4 210 x 297 mm, up to ~300 sheets (WALL_H).
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 0, 15), grams=1500)],   # ~300 sheets A4 80 g/m2
    print_orientation="auto",
    supports="auto",
    brim="on",             # ABS, 241 x 312 mm flat footprint
)

# Paper / fits
PAPER_W = 210.0
PAPER_L = 297.0
PAPER_CLEAR = 5.0      # per side (A4 + 10 mm)
PIN_D = 8.0
PIN_H = 5.0
PIN_FIT = 0.4          # socket diameter = PIN_D + PIN_FIT (loose stacking fit)

# Tray
WALL = 2.4
FLOOR = 2.4
WALL_H = 45.0
CORNER_R = 6.0
FRONT_H = 15.0         # front wall height at the scoop bottom
SCOOP_W = 130.0
STACK_PITCH = 70.0     # floor-to-floor distance when stacked
POST_W = 8.0           # sticks out of the side wall (X)
POST_L = 16.0          # along Y
POST_INSET = 20.0      # post centre from tray front/back end
WIN_NX, WIN_NY = 2, 3
WIN_W, WIN_L, WIN_R = 80.0, 75.0, 10.0

IN_W = PAPER_W + 2 * PAPER_CLEAR
IN_L = PAPER_L + 2 * PAPER_CLEAR
OUT_W = IN_W + 2 * WALL
OUT_L = IN_L + 2 * WALL


def build() -> Part:
    tray = rounded_box(OUT_W, OUT_L, FLOOR + WALL_H, radius=CORNER_R)
    cav = Pos(0, 0, FLOOR) * Box(IN_W, IN_L, WALL_H + 1, align=ON_BED)
    cav = fillet(cav.edges().filter_by(Axis.Z), CORNER_R - WALL)
    tray -= cav

    # front scoop (front = -Y): U-cut in the front wall
    r = SCOOP_W / 2
    scoop = Pos(0, -OUT_L / 2, FLOOR + FRONT_H + r) * Rot(90, 0, 0) * Cylinder(r, 4 * WALL)
    scoop += Pos(0, -OUT_L / 2, FLOOR + FRONT_H + r) * Box(SCOOP_W, 4 * WALL, 2 * WALL_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    tray -= scoop

    # floor windows
    for ix in range(WIN_NX):
        for iy in range(WIN_NY):
            x = (ix - (WIN_NX - 1) / 2) * (IN_W / WIN_NX)
            y = (iy - (WIN_NY - 1) / 2) * (IN_L / WIN_NY)
            win = Pos(x, y, -1) * extrude(RectangleRounded(WIN_W, WIN_L, WIN_R), FLOOR + 2)
            tray -= win

    # stacking posts with pins on top and sockets underneath
    for sx in (-1, 1):
        for sy in (-1, 1):
            x = sx * (OUT_W / 2 + POST_W / 2 - 1)
            y = sy * (OUT_L / 2 - POST_INSET)
            post = Pos(x, y, 0) * rounded_box(POST_W + 2, POST_L, STACK_PITCH, radius=2)
            pin = Pos(x, y, STACK_PITCH - 0.01) * Cylinder(PIN_D / 2, PIN_H, align=ON_BED)
            pin = chamfer(pin.edges().group_by(Axis.Z)[-1], 0.8)
            tray += post + pin
            sock = Pos(x, y, -0.01) * Cylinder((PIN_D + PIN_FIT) / 2, PIN_H + 1, align=ON_BED)
            rs = (PIN_D + PIN_FIT) / 2
            sock += Pos(x, y, PIN_H + 0.99) * Cone(rs, 0.5, rs - 0.5, align=ON_BED)  # 45 deg roof, no support
            tray -= sock
    return tray
