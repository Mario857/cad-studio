"""book-rest: nightstand reading stand with a 2-angle back, page-holder lip and flexible page clips.

Spec
- Base plate with a front page-holder lip; the book's lower edge sits on the ledge between the lip
  and the back panel. Ledge depth fits books up to BOOK_MAX = 50 mm thick.
- Back panel stands in a hinge slot that runs through the base, its bottom edge on the table.
- A separate prop (strut) braces the panel: its top seats under a 50-degree catch on the panel back,
  its foot drops into one of two through-slots in the base:
  front slot -> back at ANGLE_1 (70 deg from horizontal), rear slot -> ANGLE_2 (60 deg).
- Two flexible page clips (C-clips, slide onto the outer edge of each book half): a stiff back jaw
  goes behind the cover, a 1.6 mm diagonal spring finger presses the pages. Because the finger is
  diagonal it self-adapts to page stacks of ~3..50 mm.
- Print-in-place: everything is modelled assembled in the 70-deg position (Z up, in-use pose) and
  printed exactly like that, no supports. Panel and prop stand on the bed inside their base slots
  (GAP clearance); the two clips lie flat on the bed inside the base window.
  The 70-deg pose is printable: panel leans 20 deg, prop 19 deg, catch underside 40 deg from vertical.

Assumptions
- 600 g book, open book width ~ PANEL_W or more (the panel only needs to back the spine area).
- Book centre of mass ~ 10 mm behind the hinge line at ~85 mm height (used in META loads).
- GAP = 0.6 mm print-in-place clearance (separate bodies must not fuse on the first layers).
- ABS: the 1.6 mm finger is meant to flex; if it is too stiff, reduce FINGER_T to 1.2.
Hardware: none.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 10, 85), grams=600)],   # the book, leaning on the panel
    print_orientation=(0, 0, 0),               # printed assembled in the 70-deg pose
    supports="off",
    brim="auto",
    # 5 separate bodies is intended: base, panel, prop and 2 clips are printed in place together.
)

# --- Parameters -------------------------------------------------------------------------------
BOOK_MAX = 50.0          # max book thickness
GAP = 0.6                # print-in-place clearance between separate bodies

ANGLE_1 = 70.0           # back angle from horizontal, prop in front slot (as printed)
ANGLE_2 = 60.0           # back angle from horizontal, prop in rear slot

BASE_W = 220.0
BASE_T = 5.0
LIP_T = 4.0              # page-holder lip thickness
LIP_H = 15.0             # lip height above the ledge
LEDGE_D = BOOK_MAX + 6.0  # ledge depth, lip to panel
BASE_REAR = 142.0        # base extends to y = BASE_REAR behind the hinge line
CORNER_R = 6.0

PANEL_W = 196.0
PANEL_H = 180.0          # along the slope
PANEL_T = 5.0

CATCH_S = 120.0          # catch position along the panel back (from bottom edge)
CATCH_L = 16.0           # length of the 50-deg catch underside
CATCH_W = 60.0
CATCH_ANGLE = 50.0       # catch underside angle from horizontal (as printed)

PROP_W = 40.0
PROP_T = 8.0
PROP_FOOT_Y = 85.0       # prop foot position (front slot) behind the hinge line

WIN_X = 124.0            # clip / material-saving window in the base
WIN_Y0 = 14.0
WIN_Y1 = 76.0

CLIP_H = 10.0            # clip extrusion (printed flat)
CLIP_JT = 2.4            # back jaw thickness
CLIP_JL = 30.0           # back jaw length
CLIP_SPINE = 3.0
CLIP_REACH = BOOK_MAX + 4.0
FINGER_T = 1.6
FINGER_X = 50.0          # how far inward the spring finger reaches
FINGER_END_Y = 2.0       # finger tip height above the back jaw


# --- 2D helpers in the side (Y, Z) plane ------------------------------------------------------
def poly(pts):
    return Polygon(*pts, align=None)


def side_extrude(sketch, width):
    return extrude(Plane.YZ * sketch, amount=width / 2, both=True)


def rot(p, pivot, deg):
    a = math.radians(deg)
    y, z = p[0] - pivot[0], p[1] - pivot[1]
    return (pivot[0] + y * math.cos(a) - z * math.sin(a), pivot[1] + y * math.sin(a) + z * math.cos(a))


def add(p, q, k=1.0):
    return (p[0] + k * q[0], p[1] + k * q[1])


BIG = 1000.0
BELOW_TABLE = poly([(-BIG, 0), (BIG, 0), (BIG, -BIG), (-BIG, -BIG)])

a1 = math.radians(ANGLE_1)
D = (math.cos(a1), math.sin(a1))          # up the panel
N = (math.sin(a1), -math.cos(a1))         # panel back normal


def front(u):
    return (u * D[0], u * D[1])


def back(u):
    return add(front(u), N, PANEL_T)


PIVOT2 = (PANEL_T / math.sin(a1), 0.0)    # back-bottom edge: the panel rocks back on it
TILT = -(ANGLE_1 - ANGLE_2)               # clockwise = leaning further back

A1 = back(CATCH_S)                         # catch corner (prop contact)
F1 = (PROP_FOOT_Y, 0.0)
PROP_L = math.dist(A1, F1)
A2 = rot(A1, PIVOT2, TILT)
F2 = (A2[0] + math.sqrt(PROP_L**2 - A2[1] ** 2), 0.0)
DELTA = math.degrees(math.atan2(A2[1] - F2[1], A2[0] - F2[0]) - math.atan2(A1[1] - F1[1], A1[0] - F1[0]))


def panel_sketch():
    pts = [front(-20), front(PANEL_H), back(PANEL_H), back(-20)]
    return poly(pts) - BELOW_TABLE


def catch_sketch():
    c = math.radians(CATCH_ANGLE)
    e = add(A1, (math.cos(c), math.sin(c)), CATCH_L)
    b = back(CATCH_S + CATCH_L * 1.6)
    return poly([add(A1, N, -2), A1, e, b, add(b, N, -2)])


def prop_sketch():
    """Prop in the 70-deg pose: bar F1->A1, trimmed by table, panel back and catch underside."""
    ax = ((A1[0] - F1[0]) / PROP_L, (A1[1] - F1[1]) / PROP_L)
    nn = (-ax[1], ax[0])
    p0, p1 = add(F1, ax, -10), add(A1, ax, PROP_T)
    bar = poly([add(p0, nn, PROP_T / 2), add(p1, nn, PROP_T / 2),
                add(p1, nn, -PROP_T / 2), add(p0, nn, -PROP_T / 2)])
    # keep-outs: everything in front of the panel back, everything above the catch underside
    pb = add(A1, N, GAP)
    front_half = poly([add(pb, D, -BIG), add(pb, D, BIG), add(add(pb, D, BIG), N, -BIG),
                       add(add(pb, D, -BIG), N, -BIG)])
    c = math.radians(CATCH_ANGLE)
    cd = (math.cos(c), math.sin(c))
    cn = (math.sin(c), -math.cos(c))          # pointing below the catch face
    pc = add(A1, cn, GAP)
    above = poly([add(pc, cd, -BIG), add(pc, cd, BIG), add(add(pc, cd, BIG), cn, -BIG),
                  add(add(pc, cd, -BIG), cn, -BIG)])
    return bar - front_half - above - BELOW_TABLE


def moved_prop_sketch():
    """Prop in the 60-deg pose (for the rear slot): rotate about the contact, move contact A1->A2."""
    sk = prop_sketch()
    moved = Pos(0, A2[0], A2[1]) * Rot(DELTA, 0, 0) * Pos(0, -A1[0], -A1[1]) * (Plane.YZ * sk)
    return moved


def clip_part():
    jaw = Pos(CLIP_JL / 2, -CLIP_JT / 2) * Rectangle(CLIP_JL, CLIP_JT)
    spine = Pos(-CLIP_SPINE / 2, (CLIP_REACH - CLIP_JT) / 2) * Rectangle(CLIP_SPINE, CLIP_REACH + CLIP_JT)
    s = (0.0, CLIP_REACH)
    e = (FINGER_X, FINGER_END_Y)
    L = math.dist(s, e)
    ux, uy = (e[0] - s[0]) / L, (e[1] - s[1]) / L
    nx, ny = -uy, ux
    h = FINGER_T / 2
    finger = poly([(s[0] - CLIP_SPINE * ux + nx * h, s[1] - CLIP_SPINE * uy + ny * h),
                   (e[0] + nx * h, e[1] + ny * h), (e[0] - nx * h, e[1] - ny * h),
                   (s[0] - CLIP_SPINE * ux - nx * h, s[1] - CLIP_SPINE * uy - ny * h)])
    root = poly([(-CLIP_SPINE, CLIP_REACH), (6.0, CLIP_REACH - 7.0), (0, CLIP_REACH - 9.0)])
    tip = Pos(*e) * Circle(1.4)
    part = None
    for sk in (jaw, spine, finger, root, tip):
        solid = extrude(Plane.XY * sk, CLIP_H, dir=(0, 0, 1))
        part = solid if part is None else part + solid
    return part


def build():
    # Base plate with page-holder lip
    y_front = -(LEDGE_D + LIP_T)
    depth = BASE_REAR - y_front
    base = Pos(0, y_front + depth / 2, 0) * rounded_box(BASE_W, depth, BASE_T, radius=CORNER_R)
    lip = Pos(0, y_front + LIP_T / 2, 0) * rounded_box(BASE_W, LIP_T, BASE_T + LIP_H, radius=1.5)
    base = base + lip

    # Hinge slot: both panel poses, grown by GAP
    p1 = panel_sketch()
    p2 = Pos(0, PIVOT2[0], PIVOT2[1]) * Rot(TILT, 0, 0) * Pos(0, -PIVOT2[0], -PIVOT2[1]) * (Plane.YZ * p1)
    hinge_cut = side_extrude(offset(p1, GAP), PANEL_W + 2 * GAP)
    hinge_cut += extrude(offset(p2, GAP), amount=PANEL_W / 2 + GAP, both=True)

    # Prop slots
    ps = prop_sketch()
    slot1 = side_extrude(offset(ps, GAP), PROP_W + 2 * GAP)
    ps2 = moved_prop_sketch()
    slot2 = extrude(offset(ps2, GAP), amount=PROP_W / 2 + GAP, both=True)

    window = Pos(0, (WIN_Y0 + WIN_Y1) / 2, BASE_T + 1) * Box(WIN_X, WIN_Y1 - WIN_Y0, BASE_T + 4)
    window = fillet(window.edges().filter_by(Axis.Z), 5)
    base = base - hinge_cut - slot1 - slot2 - window

    # Back panel with catch
    panel = side_extrude(p1, PANEL_W) + side_extrude(catch_sketch(), CATCH_W)

    prop = side_extrude(ps, PROP_W)

    # Clips lying flat in the base window
    c = clip_part()
    clip_a = Pos(-WIN_X / 2 + 2 + CLIP_SPINE + GAP, WIN_Y0 + 1 + CLIP_JT, 0) * c
    clip_b = Pos(4 + CLIP_SPINE, WIN_Y0 + 1 + CLIP_JT, 0) * c

    return [base, panel, prop, clip_a, clip_b]
