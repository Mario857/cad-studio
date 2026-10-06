"""savings-column: 3-tube €2 coin savings column with € marks, slot top and bayonet caps.

Spec: three vertical tubes side by side, each taking a stack of €2 coins dropped through a
slot in the gabled top. A €500 goal per tube = 250 coins x 2.20 mm = 550 mm of stack, which
cannot print in one 320 mm piece, so the column is two stacking sections (each < 320 mm):
  - LOWER: wide anti-tip foot + plinth with bayonet sockets, tubes up to a socket collar.
  - UPPER: tongue that drops into the collar, tubes continue, gabled top with 3 coin slots.
  - 3 bayonet bottom caps (one per tube, empty one tube at a time; twist with a coin).
Raised € marks every €20 (= 10 coins, spacing computed from COIN_T) beside a segmented
viewing window on the front of each tube, from 20 up to the 500 goal (continues across both
sections). Assembled height ~582 mm; column 93 x 31 mm; foot 150 x 130 mm.

MEASURE BEFORE PRINTING: €2 coin diameter 25.75 mm, thickness 2.20 mm (COIN_D / COIN_T).
Assumptions: mark positions assume flat coins stacked tight from the cap top; real stacks
run ~1 % taller. Sections push-fit (SOCKET_CLEAR); add a drop of glue if wanted.
Print: no supports; the audit lists ~6 cm2 of 0.6 mm raised-digit undersides and 3 mm cap-slot
bridges, which print fine unsupported. 5 bodies = lower, upper, 3 caps (intended).
Bayonet: insert cap with lugs at the front/back channels, turn 40° clockwise (from below).
"""

import math

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm. Parts are laid out side by side for printing.
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,            # sections print separately; assembled tip check done by hand
    loads=[],
    print_orientation="auto",
    supports="off",            # only <=1.7 mm ledges remain (raised digits, bayonet groove)
    brim="on",                 # ABS, tall slender sections
)

# Coin + goal
COIN_D = 25.75
COIN_T = 2.20
COIN_VALUE = 2
MARK_STEP_EUR = 20
GOAL_EUR = 500
COIN_CLEAR = 0.85           # bore diametral clearance over coin
SLOT_W = 3.0                # top slot width (coin 2.2 thick)

# Tubes
N_TUBES = 3
WALL = 2.4
PITCH = 31.0
BORE_D = COIN_D + COIN_CLEAR
OD = BORE_D + 2 * WALL
COL_W = N_TUBES * PITCH + 8      # flat front wide enough for the outer tubes' labels
COL_D = OD
COL_R = 3.0

# Foot / plinth / bayonet
FOOT_L = 150.0
FOOT_W = 130.0
FOOT_T = 4.0
PLINTH_GROW = 4.0
PLINTH_H = 14.0
CAP_FLANGE_D = 29.0
CAP_FLANGE_T = 2.5
CAP_RECESS_CLEAR = 0.6      # diametral, flange recess in foot
CAP_SPIGOT_H = 8.0
CAP_SPIGOT_CLEAR = 0.5      # diametral, spigot in bore
LUG_W = 6.0
LUG_H = 3.0
LUG_R = 1.4                 # lug protrusion beyond spigot radius
BAY_CLEAR = 0.3             # groove clearance around lug
BAY_TURN = 40.0             # degrees of twist

# Sections
SOCKET_CLEAR = 0.25         # gap per side, tongue in collar
SOCKET_DEPTH = 10.0
COLLAR_GROW = 2.4
LOWER_TOP = 292.0
UPPER_H = 300.0
ROOF_T = 3.0

# Windows + marks
WIN_W = 7.0
WIN_SEG = 50.0
WIN_BRIDGE = 6.0
TEXT_SIZE = 7.0
TEXT_DEPTH = 0.6
TICK_L = 6.0
TICK_H = 1.2

STACK_Z0 = CAP_FLANGE_T + CAP_SPIGOT_H          # coin stack floor (cap top)
UPPER_Z0 = LOWER_TOP - SOCKET_DEPTH
MARK_DZ = MARK_STEP_EUR / COIN_VALUE * COIN_T   # 22 mm per €20
N_MARKS = int(GOAL_EUR / MARK_STEP_EUR)
GOAL_TOP = STACK_Z0 + N_MARKS * MARK_DZ


def tube_x(i):
    return (i - (N_TUBES - 1) / 2) * PITCH


def outline(grow=0.0):
    return RectangleRounded(COL_W + 2 * grow, COL_D + 2 * grow, COL_R + grow)


def prism(sk, z0, h):
    return Pos(0, 0, z0) * extrude(sk, h)


def sector(r, a0, a1, z0, h):
    pts = [(0, 0)] + [(2 * r * math.cos(math.radians(a)), 2 * r * math.sin(math.radians(a)))
                      for a in (a0, (a0 + a1) / 2, a1)]
    wedge = extrude(Polygon(*pts, align=None), h)
    return Pos(0, 0, z0) * (wedge & Cylinder(r, h, align=ON_BED))


def front_text(txt, x, zc):
    t = label(txt, size=TEXT_SIZE, depth=TEXT_DEPTH + 0.2)
    bb = t.bounding_box()
    t = Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, 0) * t
    return Pos(x, -COL_D / 2 + 0.2, zc) * (Rot(90, 0, 0) * t)


def windows(z_lo, z_hi):
    cut = None
    z = z_lo
    while z + 10 < z_hi:
        h = min(WIN_SEG, z_hi - z)
        for i in range(N_TUBES):
            w = WIN_W / 2
            pent = Polygon((-w, 0), (w, 0), (w, h - w), (0, h), (-w, h - w), align=None)  # 45° pointed top
            b = Pos(tube_x(i), -COL_D / 2, z) * extrude(Plane.XZ * pent, 2 * WALL, both=True)
            cut = b if cut is None else cut + b
        z += h + WIN_BRIDGE
    return cut


def marks(z_lo, z_hi):
    out = None
    for n in range(1, N_MARKS + 1):
        z = STACK_Z0 + n * MARK_DZ
        if not (z_lo + 4 < z < z_hi - 4):
            continue
        for i in range(N_TUBES):
            x = tube_x(i)
            tx = x - (WIN_W / 2 + (PITCH - WIN_W) / 4)
            tri = Polygon((0.2, -TICK_H), (0.2, TICK_H / 2), (-TEXT_DEPTH, TICK_H / 2), (-TEXT_DEPTH, 0),
                          align=None)   # 45° underside, no support
            tk = Pos(x + WIN_W / 2 + 0.3, -COL_D / 2, z) * extrude(Plane.YZ * tri, TICK_L)
            s = front_text(str(n * MARK_STEP_EUR), tx, z) + tk
            out = s if out is None else out + s
    return out


def build_lower():
    body = rounded_box(FOOT_L, FOOT_W, FOOT_T, radius=10)
    plinth = prism(outline(PLINTH_GROW), 0, PLINTH_H) + Pos(0, 0, PLINTH_H) * loft(
        [Plane.XY * outline(PLINTH_GROW), Plane.XY.offset(PLINTH_GROW) * outline()])
    body += plinth + prism(outline(), PLINTH_H, LOWER_TOP - PLINTH_H)
    cz = LOWER_TOP - SOCKET_DEPTH - 2 - COLLAR_GROW
    body += Pos(0, 0, cz) * loft([Plane.XY * outline(), Plane.XY.offset(COLLAR_GROW) * outline(COLLAR_GROW)])
    body += prism(outline(COLLAR_GROW), cz + COLLAR_GROW, LOWER_TOP - cz - COLLAR_GROW)
    body = body + marks(PLINTH_H + PLINTH_GROW, cz)
    body -= prism(outline(SOCKET_CLEAR), LOWER_TOP - SOCKET_DEPTH, SOCKET_DEPTH + 1)
    body -= windows(STACK_Z0 + 12, cz - 4)
    rg = BORE_D / 2 + LUG_R + BAY_CLEAR
    lug_half = math.degrees((LUG_W / 2 + BAY_CLEAR) / (BORE_D / 2))
    g0 = CAP_FLANGE_T + 1.0 - BAY_CLEAR
    for i in range(N_TUBES):
        p = Pos(tube_x(i), 0, 0)
        body -= p * Pos(0, 0, -1) * Cylinder(BORE_D / 2, LOWER_TOP + 2, align=ON_BED)
        rr = (CAP_FLANGE_D + CAP_RECESS_CLEAR) / 2
        body -= p * Pos(0, 0, -1) * Cylinder(rr, CAP_FLANGE_T + 1, align=ON_BED)
        body -= p * Pos(0, 0, CAP_FLANGE_T) * Cone(rr, BORE_D / 2, rr - BORE_D / 2, align=ON_BED)
        for base in (90, 270):   # channels front/back, grooves turn clockwise seen from below
            body -= p * sector(rg, base - lug_half, base + lug_half, -1, g0 + LUG_H + 2 * BAY_CLEAR + 1)
            gh = LUG_H + 2 * BAY_CLEAR
            gtop = Pos(0, 0, gh) * Cone(rg, BORE_D / 2 - 0.5, rg - BORE_D / 2 + 0.5, align=ON_BED)  # 45° ceiling
            wedge = sector(rg * 2, base - lug_half, base + lug_half + BAY_TURN, 0, gh + rg)
            body -= p * Pos(0, 0, g0) * ((Cylinder(rg, gh, align=ON_BED) + gtop) & wedge)
    return body


def build_upper():
    z1 = UPPER_H
    body = prism(outline(), 0, z1)
    body += marks(UPPER_Z0, UPPER_Z0 + z1 - 30).moved(Location((0, 0, -UPPER_Z0)))
    body += front_text(f"€{COIN_VALUE}", tube_x(0) - 9, z1 - 12)
    r = BORE_D / 2
    zg = z1 - ROOF_T - (r - SLOT_W / 2)       # gable springs here, 45° roof
    win_top = min(GOAL_TOP - UPPER_Z0 + 2, zg - 4)
    body -= windows(SOCKET_DEPTH + 12, win_top)
    for i in range(N_TUBES):
        x = tube_x(i)
        body -= Pos(x, 0, -1) * Cylinder(r, zg + 1, align=ON_BED)
        gable = Polygon((-r, 0), (r, 0), (r, zg), (SLOT_W / 2, z1 - ROOF_T), (-SLOT_W / 2, z1 - ROOF_T),
                        (-r, zg), align=None)
        body -= Pos(x, 0, 0) * (extrude(Plane.YZ * gable, r, both=True) & Cylinder(r, z1, align=ON_BED))
        body -= Pos(x, 0, z1 + 1) * Box(BORE_D - 0.4, SLOT_W, ROOF_T + 4, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return body


def build_cap():
    sp_r = (BORE_D - CAP_SPIGOT_CLEAR) / 2
    cap = Cylinder(CAP_FLANGE_D / 2, CAP_FLANGE_T, align=ON_BED)
    cap = chamfer(cap.edges().group_by(Axis.Z)[0], 0.4)
    cap += Pos(0, 0, CAP_FLANGE_T) * Cylinder(sp_r, CAP_SPIGOT_H, align=ON_BED)
    cap = chamfer(cap.edges().group_by(Axis.Z)[-1], 0.8)
    lz = CAP_FLANGE_T + 1.0
    for a in (90, 270):
        prof = Polygon((sp_r - 1, 0), (sp_r, 0), (sp_r + LUG_R, LUG_R), (sp_r + LUG_R, LUG_H), (sp_r - 1, LUG_H),
                       align=None)   # 45° underside
        cap += Rot(0, 0, a) * Pos(0, 0, lz) * extrude(Plane.XZ * prof, LUG_W / 2, both=True)
    cap -= Rot(180, 0, 0) * slot(20, 3.2, 1.4)   # twist with a coin from below
    return cap


def build():
    lower = build_lower()
    upper = Pos(0, FOOT_W / 2 + 6 + COL_D / 2, 0) * build_upper()
    caps = [Pos(-40 + 40 * i, -FOOT_W / 2 - 6 - CAP_FLANGE_D / 2, 0) * build_cap() for i in range(N_TUBES)]
    return [lower, upper] + caps
