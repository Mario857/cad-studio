"""coin-purse: 80 x 60 mm pocket clamshell coin purse with printed hinge pin and snap latch.

Spec: base tray (11 mm) + lid tray (5 mm) = 16 mm closed, R15 plan corners and 2 mm 45°
outer edge chamfers so it slides into a pocket. 5-knuckle hinge on the back (base knuckles
1/3/5 hold the pin snug, lid knuckles 2/4 turn on it loose), knuckles carried on 45°
corbels so nothing overhangs. Separate printed pin with a head, D-flat for printing.
Latch: a flex tab hangs from the lid front into a recess in the base front face; its 45°
bump clicks into a V-groove (thumb lifts the tab to open). Lid printed upside down.

Fits: pin hole in base knuckles PIN_D + FIT["snug"]·2, in lid knuckles PIN_D + LOOSE·2
(teardrop holes, tip up as printed); latch bump BUMP = 0.6 mm; tab recess clearance 0.3
(0.3 mm snap interference). Open with a thumbnail under the tab.

Assumptions: holds ~€20 in mixed coins (≈ 70 x 50 x 13 mm inside); pin Ø3 mm.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="auto",
    # 3 bodies intended: base, lid (upside down), hinge pin
)

L = 80.0
W = 60.0
PLAN_R = 15.0
EDGE_CH = 2.0          # outer bottom/top chamfer
BASE_H = 11.0
LID_H = 5.0
WALL = 1.8
FLOOR = 1.6
KR = 3.5               # knuckle radius
HINGE_L = 50.0
KNUCKLES = 5
K_GAP = 0.5
PIN_D = 3.0
PIN_SNUG = 0.15        # per side, base knuckles
PIN_LOOSE = 0.35       # per side, lid knuckles
PIN_HEAD_D = 6.0
PIN_HEAD_T = 1.5
TAB_W = 16.0
TAB_T = 1.6
TAB_L = 6.5            # below the parting line
BUMP = 0.6
RECESS_CLEAR = 0.3
PRINT_GAP = 6.0


def tray(h):
    t = rounded_box(L, W, h, radius=PLAN_R, bottom_chamfer=EDGE_CH)
    t -= Pos(0, 0, FLOOR) * rounded_box(L - 2 * WALL, W - 2 * WALL, h, radius=PLAN_R - WALL, bottom_chamfer=0)
    return t


def knuckle_set(za, ya, idx, hole_d, upper=False):
    """Knuckles at positions idx; corbel below (or above, mirrored) the axis to the back wall."""
    seg = (HINGE_L - (KNUCKLES - 1) * K_GAP) / KNUCKLES
    s = -1 if upper else 1
    yw = W / 2 - WALL
    cy, cz = ya + KR / math.sqrt(2), za - s * KR / math.sqrt(2)  # tangent point at 45°
    zw = cz - s * (cy - yw)
    prof = Polygon((yw, za), (yw, zw), (cy, cz), (ya, za), align=None)
    out = Part()
    for i in idx:
        x = -HINGE_L / 2 + seg / 2 + i * (seg + K_GAP)
        k = Pos(x, ya, za) * Rot(0, 90, 0) * Cylinder(KR, seg)
        k += Pos(x, 0, 0) * extrude(Plane.YZ * prof, seg / 2, both=True)
        out += k
    hole = teardrop_hole(hole_d, HINGE_L + 2, along="X")
    if upper:
        hole = Rot(180, 0, 0) * hole       # tip points up when the lid is printed flipped
    return out, Pos(0, ya, za) * hole


def build():
    za = BASE_H
    ya = W / 2 + KR + 0.3
    # --- base
    base = tray(BASE_H)
    base += Pos(0, -W / 2 + WALL, FLOOR) * Box(TAB_W + 8, 2.6, BASE_H - FLOOR, align=(Align.CENTER, Align.MIN, Align.MIN))
    kb, hb = knuckle_set(za, ya, [0, 2, 4], PIN_D + 2 * PIN_SNUG)
    base += kb
    base -= hb
    # latch recess + V-groove in the front face
    rw, rd = TAB_W + 2 * RECESS_CLEAR, TAB_T + RECESS_CLEAR
    base -= Pos(0, -W / 2, za - TAB_L - RECESS_CLEAR) * Box(rw, 2 * rd, TAB_L + 5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    q = (BUMP + 0.2) * math.sqrt(2)
    gz = za - TAB_L + 1.5
    base -= Pos(0, -W / 2 + rd, gz) * Rot(45, 0, 0) * Box(rw, q, q)

    # --- lid (in-use pose: z = za .. za + LID_H), then flipped for printing
    lid = Pos(0, 0, za + LID_H) * Rot(180, 0, 0) * tray(LID_H)
    kl, hl = knuckle_set(za, ya, [1, 3], PIN_D + 2 * PIN_LOOSE, upper=True)
    lid += kl & Box(2 * L, 3 * W, za + LID_H, align=ON_BED)   # corbels flush with the lid top
    lid -= hl
    yt = -W / 2 + rd - RECESS_CLEAR - TAB_T / 2
    tab = Pos(0, yt, za + 2) * Box(TAB_W, TAB_T, TAB_L + 2, align=(Align.CENTER, Align.CENTER, Align.MAX))
    lid += tab
    # bump on the tab inside face (towards +Y), 45° both sides
    yb = yt + TAB_T / 2
    bump = Pos(0, yb, gz) * Rot(45, 0, 0) * Box(TAB_W, BUMP * math.sqrt(2), BUMP * math.sqrt(2))
    lid += bump & Pos(0, yb, gz) * Box(TAB_W, 2 * BUMP, 4, align=(Align.CENTER, Align.MIN, Align.CENTER))
    lid = Pos(0, -(W + 2 * KR + PRINT_GAP), za + LID_H) * Rot(180, 0, 0) * lid

    # --- pin (printed lying along X, D-flat 0.4 mm on the bed)
    pl = HINGE_L + 1.0
    zc = PIN_D / 2 - 0.4
    pin = Pos(0, 0, zc) * Rot(0, 90, 0) * (
        Cylinder(PIN_D / 2, pl, align=(Align.CENTER, Align.CENTER, Align.MIN))
        + Pos(0, 0, -PIN_HEAD_T) * Cylinder(PIN_HEAD_D / 2, PIN_HEAD_T, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    pin &= Box(3 * pl, 20, 20, align=(Align.CENTER, Align.CENTER, Align.MIN))
    pin = Pos(-pl / 2, ya + KR + PRINT_GAP + PIN_HEAD_D / 2, 0) * pin
    return [base, lid, pin]
