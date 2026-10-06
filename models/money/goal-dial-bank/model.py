"""goal-dial-bank: gable-roof coin bank with a hand-turned 0-100 % goal dial on the front.

Spec: 110 x 80 x 140 mm house-shaped bank. Coin slot on the roof ridge (takes €2 and all
smaller coins). Front face carries a raised 270° dial: ticks every 10 %, labels 0/25/50/75/100,
"GOAL %" underneath. A separate pointer (printed flat) snaps into a teardrop hole in the front
wall with a split barbed pin; the snug pin fit keeps it where you set it.
Removable bottom: a shallow tray snaps into the open bottom (45° ridge in a 45° groove);
pry it out with a coin at the notch in the back wall.
The gable roof doubles as the 45° ceiling, so the body prints upright with no supports.

MEASURE BEFORE PRINTING: €2 coin 25.75 mm diameter, 2.20 mm thick (SLOT_L / SLOT_W).
Assumptions: 2.4 mm walls; pin hole snug (PIN_FIT) so the pointer holds position by
friction; if it spins freely, reprint pointer with PIN_D + 0.1.
Supports off: only ~1 cm2 of 0.6 mm raised-tick undersides remain. 3 bodies = body, tray,
pointer (intended).
"""

import math

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm. Pointer is laid flat beside the body for printing.
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 0, 20), grams=800)],
    print_orientation="auto",
    supports="off",
    brim="auto",
)

# Body
L = 110.0                   # along X (front face width)
D = 80.0                    # along Y
WALL_H = 100.0              # vertical walls, then 45° gable roof
WALL = 2.4

# Coin slot (€2)
SLOT_L = 29.0
SLOT_W = 3.4

# Dial
DIAL_Z = 50.0
TICK_R0 = 29.0
TICK_R1 = 35.0
TICK_MAJOR_R1 = 37.0
TICK_W = 1.4
LABEL_R = 43.0
TEXT_SIZE = 7.0
RAISE = 0.6
SWEEP = 270.0

# Pointer + pin
PIN_D = 6.0
PIN_FIT = 0.15              # diametral, snug: holds by friction
PIN_SLOT = 1.6
BARB = 0.5                  # barb lip radial
HUB_D = 16.0
PTR_T = 3.0
PTR_LEN = 30.0
PTR_W = 7.0

# Bottom tray
TRAY_FLOOR = 2.4
TRAY_RIM = 1.6
TRAY_H = 10.0
TRAY_FIT = 0.15             # per side, snug
SNAP = 0.6                  # 45° snap ridge height
NOTCH_W = 14.0
NOTCH_H = 2.0


def gable(inset=0.0):
    hw = D / 2 - inset
    zt = WALL_H + D / 2 - inset * math.sqrt(2)
    return Polygon((-hw, 0), (hw, 0), (hw, zt - hw), (0, zt), (-hw, zt - hw), align=None)


def on_front(shape, x, z):
    """shape built in XY (z 0..h) -> raised on the front face at (x, z)."""
    return Pos(x, -D / 2 + 0.2, z) * (Rot(90, 0, 0) * shape)


def centered_label(txt):
    t = label(txt, size=TEXT_SIZE, depth=RAISE + 0.2)
    bb = t.bounding_box()
    return Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, 0) * t


def ang(p):
    return math.radians(225 - SWEEP * p / 100)


def build_body():
    body = extrude(Plane.YZ * gable(), L / 2, both=True)
    body = chamfer(body.edges().group_by(Axis.Z)[0], 0.4)
    cavity = extrude(Plane.YZ * gable(WALL), L / 2 - WALL, both=True)
    cavity += Pos(0, 0, -1) * Box(L - 2 * WALL, D - 2 * WALL, 2, align=ON_BED)  # open bottom
    body -= cavity
    # dial
    for p in range(0, 101, 10):
        a = ang(p)
        r1 = TICK_MAJOR_R1 if p % 25 == 0 else TICK_R1
        rm = (TICK_R0 + r1) / 2
        tick = Rot(0, 0, math.degrees(a)) * Box(r1 - TICK_R0, TICK_W, RAISE + 0.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        body += on_front(Pos(rm * math.cos(a), rm * math.sin(a), 0) * tick, 0, DIAL_Z)
    for p in (0, 25, 50, 75, 100):
        a = ang(p)
        body += on_front(centered_label(str(p)), LABEL_R * math.cos(a), DIAL_Z + LABEL_R * math.sin(a))
    body += on_front(centered_label("GOAL %"), 0, 11)
    # pointer pin hole
    body -= Pos(0, -D / 2 + WALL / 2, DIAL_Z) * teardrop_hole(PIN_D + PIN_FIT - 0.2, WALL + 2, along="Y")
    # coin slot through the ridge
    body -= Pos(0, 0, WALL_H + D / 2 + 1) * Box(SLOT_L, SLOT_W, 20, align=(Align.CENTER, Align.CENTER, Align.MAX))
    # snap groove for the tray (45° both faces) + pry notch at the back
    zg = TRAY_H - SNAP - 1.5
    gl, gw = L - 2 * WALL, D - 2 * WALL
    groove = Pos(0, 0, zg) * loft([Plane.XY * Rectangle(gl, gw), Plane.XY.offset(SNAP) * Rectangle(gl + 2 * SNAP, gw + 2 * SNAP)])
    groove += Pos(0, 0, zg + SNAP) * loft([Plane.XY * Rectangle(gl + 2 * SNAP, gw + 2 * SNAP), Plane.XY.offset(SNAP) * Rectangle(gl, gw)])
    body -= groove
    nw = NOTCH_W / 2
    notch = Polygon((-nw, -1), (nw, -1), (nw, NOTCH_H), (0, NOTCH_H + nw), (-nw, NOTCH_H), align=None)  # 45° top
    body -= Pos(0, D / 2, 0) * extrude(Plane.XZ * notch, 2 * WALL, both=True)
    return body


def build_tray():
    tl, tw = L - 2 * WALL - 2 * TRAY_FIT, D - 2 * WALL - 2 * TRAY_FIT
    tray = rounded_box(tl, tw, TRAY_H, radius=0.5)
    tray -= Pos(0, 0, TRAY_FLOOR) * Box(tl - 2 * TRAY_RIM, tw - 2 * TRAY_RIM, TRAY_H, align=ON_BED)
    zg = TRAY_H - SNAP - 1.5 + TRAY_FIT
    ridge = Pos(0, 0, zg) * loft([Plane.XY * Rectangle(tl - 4 * TRAY_FIT, tw - 4 * TRAY_FIT), Plane.XY.offset(SNAP + TRAY_FIT) * Rectangle(tl + 2 * SNAP - 2 * TRAY_FIT, tw + 2 * SNAP - 2 * TRAY_FIT)])
    ridge += Pos(0, 0, zg + SNAP + TRAY_FIT) * loft([Plane.XY * Rectangle(tl + 2 * SNAP - 2 * TRAY_FIT, tw + 2 * SNAP - 2 * TRAY_FIT), Plane.XY.offset(SNAP) * Rectangle(tl - 1, tw - 1)])
    ridge -= Box(tl - 2 * TRAY_RIM, tw - 2 * TRAY_RIM, 100, align=ON_BED)
    return tray + ridge


def build_pointer():
    r = PIN_D / 2
    ptr = Cylinder(HUB_D / 2, PTR_T, align=ON_BED)
    arm = Polygon((0, -PTR_W / 2), (PTR_LEN - 6, -PTR_W / 2), (PTR_LEN, 0), (PTR_LEN - 6, PTR_W / 2), (0, PTR_W / 2), align=None)
    ptr += extrude(arm, PTR_T)
    ptr = chamfer(ptr.edges().group_by(Axis.Z)[0], 0.4)
    stem = WALL + 0.3
    pin = Pos(0, 0, PTR_T) * Cylinder(r, stem, align=ON_BED)
    pin += Pos(0, 0, PTR_T + stem - 0.01) * (
        Cone(r, r + BARB, BARB, align=ON_BED) + Pos(0, 0, BARB) * Cone(r + BARB, r - 0.6, 1.8, align=ON_BED))
    pin -= Pos(0, 0, PTR_T + 0.8) * Box(PIN_SLOT, 2 * PIN_D, 20, align=ON_BED)
    return ptr + pin


def build():
    body = build_body()
    tray = Pos(0, -D / 2 - 6 - (D - 2 * WALL) / 2, 0) * build_tray()
    ptr = Pos(L / 2 + 25, 0, 0) * build_pointer()
    return [body, tray, ptr]
