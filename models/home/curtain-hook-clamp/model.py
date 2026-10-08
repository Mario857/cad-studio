"""curtain-hook-clamp: screw-mounted J-hook for a light round curtain rod (pen-sized) on a uPVC
window frame, with a screw-tightened retention cap.  Variant: SCREW-CAP.

Spec: rod D9, bore D10.5 (1.5 clearance, slides freely). Base 12 x 26 x 4 with ONE countersunk hole
for a 3.5 mm self-tapping screw (10 mm recommended, 12 mm max). Rod axis 25 mm out from the frame face.
Frame face = z=0 plane (use orientation: base lies on it, hook rises in +Z, rod along X).

One screw: the screw sits exactly under the cradle centre line (y=10, rod axis), so the rod load acts
through the screw axis and does not twist the base. It is driven through a D7.5 access hole in the
cradle floor (open cavity under the cradle), reached from the open cradle top with the cap and rod off.
The 12 mm wide base equals the cradle width so the whole part sits flush on the print bed side; 13 mm of
flat bearing face lies each side of the screw (y -3..23) to resist prying from the 25 mm lever arm.
Rotation caveat: a single screw does not stop the hook rotating about the screw axis; the flat base
bearing on the frame and the 13 mm bearing length resist it, but tighten firmly, and for heavy
or sideways-pulled curtains use a second screw (or a dab of adhesive/double-sided tape under the base).

How it works: rod is dropped into the open-top cradle. A separate 3 mm cap bridges the mouth and is
clamped by ONE M3x8 screw into a heat-set M3 insert (short, D4.6 x 5.7) in the right-hand tower.
Loosen the screw ~3 turns and swing/slide the cap off to remove the rod; tighten = locked.
Screw depth: base 4 mm, countersunk head sits flush -> a 12 mm screw protrudes only 8 mm into the
frame: through the ~3 mm outer uPVC wall and into the first chamber, stopping short of the steel
reinforcement (normally >= 10 mm behind the face). Do not use screws longer than 12 mm.

Pros: positive lock, no rod escape under slamming; removable; strong (load along layers).
Cons: needs a screwdriver, an insert and small hardware; cap can be lost; 2 parts per hook.
Hold strength: print-limited, roughly 10+ kg pull-off per hook (one screw in uPVC ~30-50 kgf; prying
from the 25 mm arm reduces it); a light rod/curtain (<1.5 kg) is a very large margin.

Print: 2 hooks + 2 caps in one set, laid out explicitly in build() (copies=1; second set offset in Z).
Orientation (0,90,0): rod axis (X) vertical, hook profile lies in the XY layer plane so layers never
cross the load-bearing curve. Zero supports. Slicer: 4 walls, 40% gyroid (or 100% - parts are tiny),
0.20 mm layer, no supports, brim ok. ABS+: enclosure closed, fan low.
Hardware per hook: 1x M3x8 screw (pan/button), 1x M3 heat-set insert (D4.6x5.7),
1x 3.5 mm countersunk self-tapping screw, 10 mm (12 mm max).
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
    copies=1,
)

ROD_D = 9.0
BORE_D = 10.5
BASE_W = 12.0
BASE_T = 4.0
BASE_Y0, BASE_Y1 = -3.0, 23.0
AXIS_Z = 25.0
AXIS_Y = 10.0
WALL = 3.0
HOOK_W = 12.0          # cradle width along X
TOP_Z = 29.0           # top of walls
TOWER_Y1 = 22.6
SCREW_Y = 18.9         # M3 insert axis
ACCESS_D = 7.5          # driver/head access hole through cradle floor
SET_DZ = 34.0           # second set offset (Z is a print-horizontal axis)
CAP_T = 3.0
CAP_Y0 = AXIS_Y - BORE_D / 2 - WALL
CAP_OFFSET_Y = 27.0
CAP_X = 0.0   # base and cradle share the same X extent (both flush on the bed side)


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
    # single base screw under the rod axis + access hole through the cradle floor (teardrop toward -X = print up)
    p = p - Pos(CAP_X, AXIS_Y, BASE_T) * bolt_hole("M3", BASE_T + 1, head="csk")
    r = ACCESS_D / 2
    h = AXIS_Z
    k = r / 2 ** 0.5
    tri = extrude(Polygon((-k, k), (-k, -k), (-2 * k, 0), align=None), h)
    tear = tri & (Pos(-2, 0, 0) * Box(4, 20, h, align=ON_BED))
    acc = Cylinder(r, h, align=ON_BED) + tear
    p = p - Pos(CAP_X, AXIS_Y, BASE_T) * acc
    return p


def cap():
    ylen = TOWER_Y1 - CAP_Y0
    c = Pos(CAP_X, CAP_OFFSET_Y + ylen / 2, 0) * rounded_box(HOOK_W, ylen, CAP_T, radius=1.5)
    c = c - Pos(CAP_X, CAP_OFFSET_Y + (SCREW_Y - CAP_Y0), CAP_T) * bolt_hole("M3", CAP_T + 1, head=None)
    return c


def build():
    parts = []
    for k in range(2):
        parts += [Pos(0, 0, k * SET_DZ) * hook(), Pos(0, 0, k * SET_DZ) * cap()]
    return parts
