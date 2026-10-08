"""curtain-hook-clamp: screw-mounted J-hook for a light round curtain rod (pen-sized) on a uPVC
window frame, with a screw-tightened retention cap.  Variant: SCREW-CAP.

Spec: rod D9, bore D10.5 (1.5 clearance, slides freely). Base 20 x 38 x 4 with 2 countersunk
holes for 3.5 mm self-tapping screws (max 12 mm long). Rod axis 25 mm out from the frame face.
Frame face = z=0 plane (use orientation: base lies on it, hook rises in +Z, rod along X).

How it works: rod is dropped into the open-top cradle. A separate 3 mm cap bridges the mouth and is
clamped by ONE M3x8 screw into a heat-set M3 insert (short, D4.6 x 5.7) in the right-hand tower.
Loosen the screw ~3 turns and swing/slide the cap off to remove the rod; tighten = locked.
Screw depth: base 4 mm, countersunk head sits flush -> a 12 mm screw protrudes only 8 mm into the
frame: through the ~3 mm outer uPVC wall and into the first chamber, stopping short of the steel
reinforcement (normally >= 10 mm behind the face). Do not use screws longer than 12 mm.

Pros: positive lock, no rod escape under slamming; removable; strong (load along layers).
Cons: needs a screwdriver, an insert and small hardware; cap can be lost; 2 parts per hook.
Hold strength: print-limited, roughly 15+ kg pull-off per hook (screws in uPVC are the limit,
~30-50 kgf each); a light rod/curtain (<1.5 kg) is a very large margin.

Print: 2 hooks + 2 caps in one set (META copies=2: each copy = hook + cap side by side).
Orientation (0,90,0): rod axis (X) vertical, hook profile lies in the XY layer plane so layers never
cross the load-bearing curve. Zero supports. Slicer: 4 walls, 40% gyroid (or 100% - parts are tiny),
0.20 mm layer, no supports, brim ok. ABS+: enclosure closed, fan low.
Hardware per hook: 1x M3x8 screw (pan/button), 1x M3 heat-set insert (D4.6x5.7),
2x 3.5 mm countersunk self-tapping screws, 8-12 mm long.
Assumptions: ~3 mm uPVC outer wall, steel >= 10 mm deep; cap held by friction + screw only.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 90, 0),
    supports="off",
    brim="auto",
    copies=2,
)

ROD_D = 9.0
BORE_D = 10.5
BASE_W = 20.0
BASE_T = 4.0
BASE_Y0, BASE_Y1 = -8.0, 30.0
AXIS_Z = 25.0
AXIS_Y = 10.0
WALL = 3.0
HOOK_W = 12.0          # cradle width along X
TOP_Z = 29.0           # top of walls
TOWER_Y1 = 22.6
SCREW_Y = 18.9         # M3 insert axis
BASE_SCREW_Y = (-4.3, 27.0)
CAP_T = 3.0
CAP_Y0 = AXIS_Y - BORE_D / 2 - WALL
CAP_OFFSET_Y = 34.0
CAP_X = (BASE_W - HOOK_W) / 2   # cradle flush with the +X base side (the bed side when printed)


def x_cyl(r, length):
    return Rot(0, 90, 0) * Cylinder(r, length)


def hook():
    r_o = BORE_D / 2 + WALL
    yl = AXIS_Y - BORE_D / 2          # left bore edge
    yr = AXIS_Y + BORE_D / 2
    base = Pos(0, (BASE_Y0 + BASE_Y1) / 2, 0) * Box(BASE_W, BASE_Y1 - BASE_Y0, BASE_T, align=ON_BED)
    left = Pos(CAP_X, (CAP_Y0 + yl) / 2, 0) * Box(HOOK_W, yl - CAP_Y0, TOP_Z, align=ON_BED)
    tower = Pos(CAP_X, (yr + TOWER_Y1) / 2, 0) * Box(HOOK_W, TOWER_Y1 - yr, TOP_Z, align=ON_BED)
    ring = Pos(CAP_X, AXIS_Y, AXIS_Z) * x_cyl(r_o, HOOK_W)
    p = base + left + tower + ring
    # fill under the bore between walls with a 45 deg web (solid, no void): wedge below ring
    p = p - Pos(CAP_X, AXIS_Y, AXIS_Z) * x_cyl(BORE_D / 2, HOOK_W + 2)
    p = p - Pos(CAP_X, AXIS_Y, AXIS_Z + 3) * Box(HOOK_W + 2, BORE_D, 20, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # trim ring above wall tops
    p = p - Pos(CAP_X, AXIS_Y, TOP_Z) * Box(HOOK_W + 2, 40, 20, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # insert
    p = p - Pos(CAP_X, SCREW_Y, TOP_Z) * insert_hole("M3", 6.5)
    # base screws
    for y in BASE_SCREW_Y:
        p = p - Pos(0, y, BASE_T) * bolt_hole("M3", BASE_T + 1, head="csk")
    return p


def cap():
    ylen = TOWER_Y1 - CAP_Y0
    c = Pos(CAP_X, CAP_OFFSET_Y + ylen / 2, 0) * rounded_box(HOOK_W, ylen, CAP_T, radius=1.5)
    c = c - Pos(CAP_X, CAP_OFFSET_Y + (SCREW_Y - CAP_Y0), CAP_T) * bolt_hole("M3", CAP_T + 1, head=None)
    return c


def build():
    return [hook(), cap()]
