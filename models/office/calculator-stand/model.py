"""calculator-stand: 20-degree desk stand for a desktop calculator, with a front pen groove.

Spec: wedge deck inclined DECK_ANGLE, sized for a calculator footprint CALC_W x CALC_L (default
100 x 160 mm) plus clearance; the calculator's front edge rests against a lip. In front of the lip
a shelf carries a pen groove (pens <= PEN_D). Diamond (45 deg) lightening holes run through the
wedge sideways so it prints upright with no supports.

Assumptions: calculator <= 400 g, footprint 100 x 160 mm, front edge <= LIP_H tall is fine.
MEASURE BEFORE PRINTING: calculator width and length (set CALC_W / CALC_L).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 12, 47), grams=400)],   # calculator COM at deck centre
    print_orientation="auto",
    supports="auto",
    brim="auto",
)

# Calculator / fits
CALC_W = 100.0
CALC_L = 160.0
CALC_CLEAR = 3.0       # per side (width) and at the top end
PEN_D = 11.0           # pen groove fits pens up to this diameter

# Stand
DECK_ANGLE = 20.0
H0 = 10.0              # deck height at the lip
LIP_H = 7.0            # lip above deck surface
LIP_T = 4.0
SHELF_L = 20.0         # pen shelf depth
SHELF_H = 14.0
SIDE = 3.0             # extra width beyond the calculator each side
HOLE_MARGIN = 5.0      # material around lightening holes

WIDTH = CALC_W + 2 * (CALC_CLEAR + SIDE)


def build() -> Part:
    a = math.radians(DECK_ANGLE)
    deck_l = CALC_L + CALC_CLEAR
    y_d = SHELF_L + LIP_T
    y_b = y_d + deck_l * math.cos(a)
    z_b = H0 + deck_l * math.sin(a)
    prof = Polygon((0, 0), (0, SHELF_H), (SHELF_L, SHELF_H), (SHELF_L, H0 + LIP_H), (y_d, H0 + LIP_H),
                   (y_d, H0), (y_b, z_b), (y_b, 0), align=None)
    part = extrude(Plane.YZ * prof, WIDTH / 2, both=True)

    # pen groove across the front shelf
    r = PEN_D / 2 + 0.5
    part -= Pos(0, SHELF_L / 2, SHELF_H + r - PEN_D / 2) * Rot(0, 90, 0) * Cylinder(r, WIDTH + 2)

    # diamond lightening holes through X
    y = y_d + 4
    while True:
        h_at = lambda yy: H0 + (yy - y_d) * math.tan(a)
        # half-diagonal s: diamond spans y..y+2s, z HOLE_MARGIN..HOLE_MARGIN+2s, top must clear the deck
        s = (h_at(y) - 2 * HOLE_MARGIN) / 2
        if s < 6:
            y += 4
            if y > y_b:
                break
            continue
        s = min(s, 30.0, (y_b - HOLE_MARGIN - y) / 2)
        if s < 6:
            break
        if y + 2 * s > y_b - HOLE_MARGIN:
            break
        d = Polygon((y, HOLE_MARGIN + s), (y + s, HOLE_MARGIN), (y + 2 * s, HOLE_MARGIN + s),
                    (y + s, HOLE_MARGIN + 2 * s), align=None)
        part -= extrude(Plane.YZ * d, WIDTH, both=True)
        y += 2 * s + HOLE_MARGIN
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    return Pos(0, -y_b / 2, 0) * part
