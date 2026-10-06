"""lockable-money-box: 200 x 140 x 80 mm cash box, printed-pin hinge, padlock hasp, coin tray.

Spec: base (60 mm) + lid (20 mm) joined by a 5-knuckle hinge at the back on a printed 5 mm
D-profile pin with a head. Knuckles have 45° gussets to the wall, so base (upright) and lid
(printed top-down) need no supports; holes are teardrops. Hasp: two stacked ears with
7 mm vertical holes (one on the base, one on the lid) on the right side wall near the front
take a small padlock with a 4-5 mm shackle (side placement keeps the plate within the bed). Inside: removable 4-pocket coin tray resting on 45° ledges in the left half;
banknotes (up to €200, 153 x 77) lie flat underneath and in the right half (33 mm deep).

Assumptions: the far base knuckle hole is a press fit (PIN_PRESS) to retain the pin; add a
drop of glue if it walks out. Padlock shackle inner clearance >= 10 mm. A printed box is a
deterrent, not a safe. Supports off: the ear plates bridge ~9 mm between their ribs. Parts: base, lid, coin tray, pin (4 bodies, intended).
Print plate: base + lid side by side along Y, tray + pin in the strip beside them.
"""

import math

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm. Lid is laid top-down beside the base for printing.
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=True,
    loads=[dict(at=(0, 0, 20), grams=1000)],
    print_orientation="auto",
    supports="off",
    brim="on",                 # large flat ABS footprint
)

# Box
L = 200.0
D = 140.0
BASE_H = 60.0
LID_H = 20.0
WALL = 3.0
FLOOR = 3.0
CORNER_R = 6.0

# Hinge
KN_R = 5.0                  # knuckle outer radius
KN_GAP = 0.5                # knuckle axis offset beyond the back wall
KN_LEN = 30.0
KN_CLEAR = 1.0              # axial gap between knuckles
N_KN = 5
PIN_D = 5.0
PIN_SLIDE = FIT["slide"]    # diametral, rotating knuckles
PIN_PRESS = FIT["press"]    # diametral, far base knuckle keeps the pin
PIN_FLAT = 0.5              # flat on the printed pin's bed side
PIN_HEAD_D = 9.0
PIN_HEAD_L = 3.0

# Hasp ears (padlock 4-5 mm shackle)
EAR_W = 18.0
EAR_T = 4.0
EAR_L = 15.0
EAR_GAP = 0.5               # each ear stops this far from the parting plane
LOCK_HOLE_D = 7.0
RIB_T = 2.4
EAR_Y = -D / 2 + 30.0        # ears sit on the right side wall, near the front

# Coin tray
TRAY_L = 85.0
TRAY_H = 22.0
TRAY_FIT = 0.5              # per side, loose
LEDGE = 3.0
TRAY_FLOOR = 2.0
TRAY_WALL = 1.6

Y_W = D / 2                       # back wall outer face
Y_K = Y_W + KN_R + KN_GAP         # hinge axis
Z_K = BASE_H
SPAN = N_KN * KN_LEN + (N_KN - 1) * KN_CLEAR


def knuckle_x(i):
    return -SPAN / 2 + KN_LEN / 2 + i * (KN_LEN + KN_CLEAR)


def knuckle(lower):
    """knuckle profile (circle + 45° gusset to the back wall), extruded along X, length KN_LEN"""
    r = KN_R
    drop = math.sqrt(2) * r + (Y_K - Y_W + 1)
    s = 1 if not lower else -1
    gus = Polygon((Y_W - 1, Z_K + s * drop), (Y_K + 0.707 * r, Z_K + s * 0.707 * r), (Y_K, Z_K), (Y_W - 1, Z_K),
                  align=None)
    prof = gus + Pos(Y_K, Z_K) * Circle(r)
    return extrude(Plane.YZ * prof, KN_LEN / 2, both=True)


def ear(lid):
    """padlock ear on the front wall with two side ribs (45°) toward the wall"""
    s = 1 if lid else -1
    z0 = Z_K + s * EAR_GAP
    plate = Pos(0, -Y_W - EAR_L / 2 + 0.5, z0) * Box(EAR_W, EAR_L + 1, EAR_T,
                                                      align=(Align.CENTER, Align.CENTER, Align.MIN if lid else Align.MAX))
    zf = z0 + s * EAR_T
    rib_prof = Polygon((-Y_W + 1, zf), (-Y_W - EAR_L + 1, zf), (-Y_W + 1, zf + s * EAR_L), align=None)
    out = plate
    rx = LOCK_HOLE_D / 2 + 1.0 + RIB_T / 2      # ribs hug the hole: plate between them is a ~9 mm bridge
    for x in (-rx, rx):
        out += Pos(x, 0, 0) * extrude(Plane.YZ * rib_prof, RIB_T / 2, both=True)
    hole = Pos(0, -Y_W - EAR_L + 6, z0 - 10) * Cylinder(LOCK_HOLE_D / 2, 20, align=ON_BED)
    # built on the front face, moved to the right side wall near the front corner
    return Pos(L / 2 - Y_W, EAR_Y, 0) * (Rot(0, 0, 90) * (out - hole))


def build_base():
    base = rounded_box(L, D, BASE_H, radius=CORNER_R)
    base -= Pos(0, 0, FLOOR) * rounded_box(L - 2 * WALL, D - 2 * WALL, BASE_H, radius=CORNER_R - WALL, bottom_chamfer=0)
    # tray ledges (45° underside) along front and back walls
    zl = BASE_H - TRAY_H - 2
    led = Polygon((0, 0), (LEDGE, 0), (0, -LEDGE), align=None)
    for s in (-1, 1):
        lp = Polygon((s * (D / 2 - WALL + 0.5), zl), (s * (D / 2 - WALL - LEDGE), zl),
                     (s * (D / 2 - WALL + 0.5), zl - LEDGE - 0.5), align=None)
        base += extrude(Plane.YZ * lp, L / 2 - WALL - 1, both=True)
    for i in range(0, N_KN, 2):
        base += Pos(knuckle_x(i), 0, 0) * knuckle(lower=True)
    base += ear(lid=False)
    for i in range(0, N_KN, 2):
        fit = PIN_PRESS if i == N_KN - 1 else PIN_SLIDE
        base -= Pos(knuckle_x(i), Y_K, Z_K) * teardrop_hole(PIN_D + fit - 0.2, KN_LEN + 0.2, along="X")
    return base


def build_lid():
    lid = Pos(0, 0, Z_K) * rounded_box(L, D, LID_H, radius=CORNER_R, bottom_chamfer=0)
    lid = chamfer(lid.edges().group_by(Axis.Z)[-1], 0.4)   # becomes the bed edge when printed top-down
    lid -= Pos(0, 0, Z_K - 1) * rounded_box(L - 2 * WALL, D - 2 * WALL, LID_H - FLOOR + 1, radius=CORNER_R - WALL,
                                            bottom_chamfer=0)
    for i in range(1, N_KN, 2):
        lid += Pos(knuckle_x(i), 0, 0) * knuckle(lower=False)
    lid += ear(lid=True)
    for i in range(1, N_KN, 2):
        lid -= Pos(knuckle_x(i), Y_K, Z_K) * teardrop_hole(PIN_D + PIN_SLIDE - 0.2, KN_LEN + 0.2, along="X", tip="-Z")
    return lid


def build_tray():
    tw = D - 2 * WALL - 2 * TRAY_FIT
    tray = rounded_box(TRAY_L, tw, TRAY_H, radius=3)
    pl = (TRAY_L - 3 * TRAY_WALL) / 2
    pw = (tw - 3 * TRAY_WALL) / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            pocket = rounded_box(pl, pw, TRAY_H, radius=4, bottom_chamfer=0)
            tray -= Pos(sx * (pl + TRAY_WALL) / 2, sy * (pw + TRAY_WALL) / 2, TRAY_FLOOR) * pocket
    return tray


def build_pin():
    r = PIN_D / 2
    length = SPAN + 1.0
    prof = Circle(r) & Pos(0, PIN_FLAT) * Rectangle(2 * r, 2 * r)          # flat at local y = -r + PIN_FLAT
    head = Circle(PIN_HEAD_D / 2) & Pos(0, -r + PIN_FLAT + PIN_HEAD_D / 2) * Rectangle(PIN_HEAD_D, PIN_HEAD_D)
    pin = extrude(Plane.XZ * prof, length) + Pos(0, PIN_HEAD_L, 0) * extrude(Plane.XZ * head, PIN_HEAD_L)
    pin = Pos(0, 0, r - PIN_FLAT) * pin                                        # flat on the bed
    return pin


def build():
    # plate: lid flipped with its knuckles interleaving the base knuckles (different X segments)
    base = build_base()
    lid_back = Y_W + 2 * KN_R + KN_GAP + 1.0
    lid = Pos(0, lid_back + Y_W, BASE_H + LID_H) * (Rot(180, 0, 0) * build_lid())
    xs = L / 2 + EAR_L + 8
    tray = Pos(xs + TRAY_L / 2, -Y_W + (D - 2 * WALL) / 2, 0) * build_tray()
    pin = Pos(xs + 5, -Y_W + (D - 2 * WALL) + 3 + SPAN + 1, 0) * build_pin()
    return [Rot(0, 0, 90) * p for p in (base, lid, tray, pin)]   # long side along the 320 mm bed axis
