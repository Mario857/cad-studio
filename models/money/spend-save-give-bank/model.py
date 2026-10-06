"""spend-save-give-bank: kids' 3-chamber coin bank with SPEND / SAVE / GIVE labels.

Spec: 192 x 64 x 122 mm block under one 45° gable roof, split into three 59 mm chambers by
inner walls. Each chamber has its own €2-size coin slot on the ridge, a raised 9 mm label on
the front, and its own bayonet bottom cap (44 mm opening) so each pot is emptied separately.
Caps twist with a coin in the cross slot (deliberately not finger-easy for small kids).
Roof = 45° ceiling, so the body prints upright with no supports.

MEASURE BEFORE PRINTING: €2 coin 25.75 mm diameter, 2.20 mm thick (SLOT_L / SLOT_W).
Assumptions: 2.4 mm walls; bayonet clearance BAY_CLEAR suits ABS; turn caps 40° clockwise
(seen from below) to lock. 4 bodies = bank + 3 caps (intended). Supports off: only raised-letter undersides remain.
"""

import math

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm. Caps laid out beside the bank for printing.
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 0, 25), grams=900)],
    print_orientation="auto",
    supports="off",
    brim="on",                 # ABS, 192 mm long footprint
)

LABELS = ["SPEND", "SAVE", "GIVE"]

# Body
CH_W = 64.0                 # chamber pitch along X
D = 64.0
WALL_H = 90.0
WALL = 2.4
FLOOR_T = 3.0
TEXT_SIZE = 9.0
RAISE = 0.6
LABEL_Z = 45.0

# Coin slot (€2)
SLOT_L = 29.0
SLOT_W = 3.4

# Bayonet bottom
HOLE_D = 44.0
BOSS_D = 56.0
BOSS_H = 15.0
FLANGE_D = 52.0
FLANGE_T = 2.5
RECESS_CLEAR = 0.6          # diametral
SPIGOT_CLEAR = 0.5          # diametral
LUG_W = 8.0
LUG_H = 3.0
LUG_R = 1.6
BAY_CLEAR = 0.3
BAY_TURN = 40.0

N = len(LABELS)
L = N * CH_W
RR = (FLANGE_D + RECESS_CLEAR) / 2
CONE_H = RR - HOLE_D / 2
LUG_Z = FLANGE_T + CONE_H + 1.0      # lug bottom above cap bottom


def gable(inset=0.0):
    hw = D / 2 - inset
    zt = WALL_H + D / 2 - inset * math.sqrt(2)
    return Polygon((-hw, 0), (hw, 0), (hw, zt - hw), (0, zt), (-hw, zt - hw), align=None)


def chamber_x(i):
    return (i - (N - 1) / 2) * CH_W


def sector(r, a0, a1, h):
    pts = [(0, 0)] + [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in (a0, (a0 + a1) / 2, a1)]
    return extrude(Polygon(*pts, align=None), h)


def build_bank():
    body = extrude(Plane.YZ * gable(), L / 2, both=True)
    body = chamfer(body.edges().group_by(Axis.Z)[0], 0.4)
    rg = HOLE_D / 2 + LUG_R + BAY_CLEAR
    lug_half = math.degrees((LUG_W / 2 + BAY_CLEAR) / (HOLE_D / 2))
    g0 = LUG_Z - BAY_CLEAR
    gh = LUG_H + 2 * BAY_CLEAR
    for i, txt in enumerate(LABELS):
        x = chamber_x(i)
        cav = Pos(x, 0, 0) * extrude(Plane.YZ * gable(WALL), CH_W / 2 - WALL, both=True)
        cav -= Pos(x, 0, 0) * Box(CH_W, D, FLOOR_T, align=ON_BED)
        body -= cav
        p = Pos(x, 0, 0)
        body += p * Cylinder(BOSS_D / 2, BOSS_H, align=ON_BED)
        body -= p * Pos(0, 0, -1) * Cylinder(HOLE_D / 2, BOSS_H + 2, align=ON_BED)
        body -= p * Pos(0, 0, -1) * Cylinder(RR, FLANGE_T + 1, align=ON_BED)
        body -= p * Pos(0, 0, FLANGE_T) * Cone(RR, HOLE_D / 2, CONE_H, align=ON_BED)
        for base in (90, 270):
            body -= p * Pos(0, 0, -1) * (sector(2 * rg, base - lug_half, base + lug_half, g0 + gh + 1)
                                         & Cylinder(rg, g0 + gh + 1, align=ON_BED))
            groove = Cylinder(rg, gh, align=ON_BED) + Pos(0, 0, gh) * Cone(rg, HOLE_D / 2 - 0.5, rg - HOLE_D / 2 + 0.5, align=ON_BED)
            body -= p * Pos(0, 0, g0) * (groove & sector(2 * rg, base - lug_half, base + lug_half + BAY_TURN, gh + rg))
        # slot through the ridge
        body -= Pos(x, 0, WALL_H + D / 2 + 1) * Box(SLOT_L, SLOT_W, 20, align=(Align.CENTER, Align.CENTER, Align.MAX))
        # raised front label
        t = label(txt, size=TEXT_SIZE, depth=RAISE + 0.2)
        bb = t.bounding_box()
        t = Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, 0) * t
        body += Pos(x, -D / 2 + 0.2, LABEL_Z) * (Rot(90, 0, 0) * t)
    return body


def build_cap():
    sp_r = (HOLE_D - SPIGOT_CLEAR) / 2
    cap = Cylinder(FLANGE_D / 2, FLANGE_T, align=ON_BED)
    cap = chamfer(cap.edges().group_by(Axis.Z)[0], 0.4)
    cap += Pos(0, 0, FLANGE_T) * Cone(FLANGE_D / 2, HOLE_D / 2 - 0.3, FLANGE_D / 2 - HOLE_D / 2 + 0.3, align=ON_BED)
    top = LUG_Z + LUG_H + 2.0
    cap += Cylinder(sp_r, top, align=ON_BED)
    cap = chamfer(cap.edges().group_by(Axis.Z)[-1], 1.0)
    cap -= Pos(0, 0, FLANGE_T + 1) * Cylinder(sp_r - 2.4, top, align=ON_BED)  # cup, saves plastic
    for a in (90, 270):
        prof = Polygon((sp_r - 1, 0), (sp_r, 0), (sp_r + LUG_R, LUG_R), (sp_r + LUG_R, LUG_H), (sp_r - 1, LUG_H),
                       align=None)   # 45° underside
        cap += Rot(0, 0, a) * Pos(0, 0, LUG_Z) * extrude(Plane.XZ * prof, LUG_W / 2, both=True)
    v = Polygon((-1.6, -1), (1.6, -1), (1.6, 0.8), (0, 2.4), (-1.6, 0.8), align=None)  # 45° roof, no bridge
    for a in (0, 90):
        cap -= Rot(0, 0, a) * extrude(Plane.YZ * v, 15, both=True)
    return cap


def build():
    bank = build_bank()
    caps = [Pos(chamber_x(i), -D / 2 - 8 - FLANGE_D / 2, 0) * build_cap() for i in range(N)]
    return [bank] + caps
