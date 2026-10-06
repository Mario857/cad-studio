"""travel-wrist-rest: foldable TPU keyboard wrist rest, 300 x 80 mm, two hinged halves.

Spec: 300 (X) x 80 (Y) mm wrist rest split at x=0 into two 150 x 80 halves joined by a
5-knuckle hinge (A = left half owns knuckles 1/3/5, B = right half owns 2/4) with a
1.75 mm filament pin. The hinge axis runs along Y, parallel to the sloped top surface and
0.5 mm above it, so the halves fold top-to-top like a book (comfort surfaces protected).
Lock: two snap latches on the underside - a 6 mm tab with a 5 mm hook on half A slides into a
gable-roofed channel + pocket in half B's bottom; unfolding to flat snaps the pocket over the hook,
and the abutting seam faces stop over-travel, so it locks open flat.
Top: 10 deg slope, LOW edge toward the user (front, y=0, 10 mm), HIGH edge toward the
keyboard (back, y=80, ~24 mm) so the wrist meets typical keyboard front height.
Honeycomb: open-top hex pockets (12 mm cells, 2 mm walls, 2 mm floor) for flex/comfort,
kept clear of the outer 5 mm border and the central hinge/latch band.
Print: flat, as in use; both halves on one plate, B placed behind A (y + 90) -
2 separate bodies is intended (they are assembled with the pin after printing).
Assumptions: keyboard behind (+Y); 1.75 mm PLA filament as hinge pin (hole 2.2 mm,
melt/flare ends to retain); TPU flex is what makes the latch snap; knuckles stand
4.5 mm proud of the top at the centre seam (between the hands, not under the wrists).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm TPU 95A @BBL H2C 0.4 nozzle",  # stock TPU preset is 0.6-nozzle only
    quality="standard",
    standing=True,
    loads=[dict(at=(-75, 40, 18), grams=600), dict(at=(-75, 130, 18), grams=600)],
    print_orientation=(0, 0, 0),
    supports="auto",
    brim="auto",
)

# Parameters
HALF_W = 150.0          # X length of each half
DEPTH = 80.0            # Y
SLOPE = 10.0            # deg, top rises toward keyboard (+Y)
H_FRONT = 10.0          # height at user edge
SEAM_GAP = 0.25         # each half ends this far from x=0
KN_R = 4.0              # knuckle radius
KN_N = 5                # knuckle count
KN_GAP = 0.4            # axial gap between knuckles
AXIS_LIFT = 0.5         # hinge axis above the top surface
GROOVE_CLR = 0.4        # radial clearance for the other half's knuckles
PIN_D = 2.2             # hole for 1.75 mm filament pin
CELL_R = 6.9            # hex circumradius (across flats ~12)
CELL_WALL = 2.0
FLOOR = 2.0
BORDER = 5.0
CENTER_KEEP = 26.0      # no cells within this |x| of the seam
LATCH_Y = (25.0, 60.0)
TAB_L = 20.0            # tab reach past the seam
TAB_W = 6.0
TAB_T = 2.5
HOOK_X = 15.0           # hook starts at this x
HOOK_L = 4.0
HOOK_H = 5.0
LATCH_CLR = 0.4
PLATE_GAP = 10.0        # Y gap between the two halves on the plate

TAN = math.tan(math.radians(SLOPE))
H_BACK = H_FRONT + DEPTH * TAN
AX_LEN = DEPTH / math.cos(math.radians(SLOPE)) + 2
TIP = KN_R * math.sqrt(2)
GROOVE_R = TIP + GROOVE_CLR


def wedge(x0: float) -> Part:
    prof = Polygon((0, 0), (DEPTH, 0), (DEPTH, H_BACK), (0, H_FRONT), align=None)
    w = extrude(Plane.YZ.offset(x0) * prof, amount=HALF_W - SEAM_GAP)
    w = chamfer(w.edges().group_by(Axis.Z)[0], 0.4)
    return w


def to_axis(local: Part) -> Part:
    """Local frame: axis = Y axis from y=-1; map onto the sloped hinge axis."""
    return Pos(0, 0, H_FRONT + AXIS_LIFT) * Rot(SLOPE, 0, 0) * local


def seg_span(i: int):
    seg = AX_LEN / KN_N
    return i * seg - 1 + (KN_GAP / 2 if i else 0), (i + 1) * seg - 1 - (KN_GAP / 2 if i < KN_N - 1 else 0)


def knuckle(i: int) -> Part:
    y0, y1 = seg_span(i)
    c = KN_R / math.sqrt(2)
    sec = Circle(KN_R) + Polygon((0, -TIP), (c, -c), (0, 0), (-c, -c), align=None)
    k = extrude(Plane.XZ * sec, amount=-(y1 - y0))
    k = Pos(0, y0 - k.bounding_box().min.Y, 0) * k
    return to_axis(k)


def groove(i: int) -> Part:
    y0, y1 = seg_span(i)
    g = Pos(0, (y0 + y1) / 2, 0) * Rot(90, 0, 0) * Cylinder(GROOVE_R, y1 - y0 + 2 * KN_GAP)
    return to_axis(g)


def pin_hole() -> Part:
    h = Pos(0, AX_LEN / 2 - 1, 0) * teardrop_hole(PIN_D, AX_LEN + 10, along="Y")
    return to_axis(h)


def honeycomb(sign: int) -> Part:
    a = CELL_R * math.sqrt(3) / 2
    pitch = 2 * a + CELL_WALL
    dx, dy = pitch * math.cos(math.radians(30)), pitch
    cells = []
    hexa = extrude(RegularPolygon(CELL_R, 6), amount=60)
    n = int(HALF_W / dx) + 2
    for ci in range(n):
        x = sign * (CENTER_KEEP + CELL_R + ci * dx)
        for ri in range(-1, int(DEPTH / dy) + 2):
            y = ri * dy + (dy / 2 if ci % 2 else 0) + 4
            if abs(x) + CELL_R > HALF_W - BORDER or y - a < BORDER or y + a > DEPTH - BORDER:
                continue
            cells.append(Pos(x, y, FLOOR) * hexa)
    return Part() + cells if cells else None


def gabled(x0: float, length: float, yc: float, w: float, h: float) -> Part:
    """Bottom channel cutter with a 45 deg gable roof (no flat bridge)."""
    prof = Polygon((yc - w / 2, -1), (yc + w / 2, -1), (yc + w / 2, h), (yc, h + w / 2),
                   (yc - w / 2, h), align=None)
    return extrude(Plane.YZ.offset(x0) * prof, amount=length)


def build():
    a = wedge(-HALF_W)
    b = wedge(SEAM_GAP)
    for i in range(KN_N):
        if i % 2 == 0:
            a = a + knuckle(i)
            b = b - groove(i)
        else:
            b = b + knuckle(i)
            a = a - groove(i)
    trim = Box(400, DEPTH, 100, align=(Align.CENTER, Align.MIN, Align.MIN))
    a = a & trim
    b = b & trim
    a = a - pin_hole()
    b = b - pin_hole()

    for ly in LATCH_Y:
        tab = Pos(-SEAM_GAP - 1, ly - TAB_W / 2, 0) * Box(TAB_L + 1, TAB_W, TAB_T, align=(Align.MIN, Align.MIN, Align.MIN))
        hook = Pos(HOOK_X, ly - TAB_W / 2, 0) * Box(HOOK_L, TAB_W, HOOK_H, align=(Align.MIN, Align.MIN, Align.MIN))
        a = a + tab + hook
        cw = TAB_W + 2 * LATCH_CLR
        chan = gabled(0, TAB_L + LATCH_CLR, ly, cw, TAB_T + LATCH_CLR)
        pocket = gabled(HOOK_X - LATCH_CLR, HOOK_L + 2 * LATCH_CLR + 1, ly, cw, HOOK_H + LATCH_CLR)
        b = b - chan - pocket

    a = a - honeycomb(-1)
    b = b - honeycomb(1)

    # plate layout: B behind A, both flat as in use
    b = Pos(-HALF_W - SEAM_GAP, DEPTH + PLATE_GAP, 0) * b
    return [a, b]
