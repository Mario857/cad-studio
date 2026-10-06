"""budget-dial: desk budget wheel with 6 categories, each with a turnable % spent indicator.

Spec: 190 mm round base, 5 mm thick. Outer ring: 6 raised category labels (CATEGORIES param)
at 60° spacing. Inside, one indicator per category: a raised 270° scale (ticks every 10 %,
major at 0/50/100, "0" and "100" at the ends) and a rotating pointer disc on a split barbed
snap pin (snug fit, holds by friction). "BUDGET" in the middle. Turn each pointer to show
how much of that category's monthly budget is spent; reset to 0 on the 1st.
One disc per category is used because a single disc can only show one value.

Assumptions: pins snap through the 5 mm base; the barb sits in a 45° countersink under the
base so it stands flat. If a pointer is too stiff/loose, change PIN_FIT by 0.05.
7 bodies = base + 6 pointers (intended), pointers print flat with the pin up.
"""

import math

from build123d import *

from cadlib import *

# Coordinates = in-use orientation for the base; pointers laid out pin-up for printing.
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation="auto",
    supports="off",
    brim="on",                 # 190 mm flat ABS disc
)

CATEGORIES = ["RENT", "FOOD", "BILLS", "TRAVEL", "FUN", "SAVE"]

# Base
BASE_D = 190.0
BASE_T = 5.0
LABEL_R = 80.0
DIAL_R = 47.0               # indicator centres
TEXT_SIZE = 7.0
RAISE = 0.6

# Indicator scale
SWEEP = 270.0
TICK_R0 = 13.5
TICK_R1 = 16.5
TICK_MAJOR_R1 = 18.0
TICK_W = 1.2
END_LABEL_R = 21.0

# Pointer + pin
PIN_D = 5.0
PIN_FIT = 0.15              # diametral, snug
PIN_SLOT = 1.4
BARB = 0.5
CSK_D = 9.0                 # 45° countersink under the base for the barb
PTR_HUB_D = 16.0
PTR_T = 3.0
PTR_TIP_R = 16.0
PTR_TAB_W = 6.0
COLLAR_D = 9.0
COLLAR_H = 1.0              # lifts the pointer over the raised ticks


def flat_text(txt, size=TEXT_SIZE):
    t = label(txt, size=size, depth=RAISE + 0.2)
    bb = t.bounding_box()
    return Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, 0) * t


def polar(r, a_deg):
    a = math.radians(a_deg)
    return r * math.cos(a), r * math.sin(a)


def build_base():
    base = Cylinder(BASE_D / 2, BASE_T, align=ON_BED)
    base = chamfer(base.edges().group_by(Axis.Z)[0], 0.4)
    base = fillet(base.edges().group_by(Axis.Z)[-1], 1.5)
    top = BASE_T - 0.2
    csk_h = (CSK_D - PIN_D - PIN_FIT) / 2
    for k, name in enumerate(CATEGORIES):
        a = 90 - k * 360 / len(CATEGORIES)
        lx, ly = polar(LABEL_R, a)
        base += Pos(lx, ly, top) * (Rot(0, 0, a - 90) * flat_text(name))
        cx, cy = polar(DIAL_R, a)
        # scale: gap (0 / 100 labels) faces outward, toward the category label
        start = a - (360 - SWEEP) / 2                    # 0 %, clockwise sweep to 100 %
        for p in range(0, 101, 10):
            ta = start - SWEEP * p / 100
            r1 = TICK_MAJOR_R1 if p % 50 == 0 else TICK_R1
            mx, my = polar((TICK_R0 + r1) / 2, ta)
            tick = Rot(0, 0, ta) * Box(r1 - TICK_R0, TICK_W, RAISE + 0.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
            base += Pos(cx + mx, cy + my, top) * tick
        for p, txt in ((0, "0"), (100, "100")):
            ta = start - SWEEP * p / 100 + (12 if p == 0 else -12)
            ex, ey = polar(END_LABEL_R + (3 if p == 100 else 0), ta)
            base += Pos(cx + ex, cy + ey, top) * (Rot(0, 0, a - 90) * flat_text(txt))
        base -= Pos(cx, cy, -1) * Cylinder((PIN_D + PIN_FIT) / 2, BASE_T + 2, align=ON_BED)
        base -= Pos(cx, cy, 0) * Cone(CSK_D / 2, (PIN_D + PIN_FIT) / 2 - 0.01, csk_h, align=ON_BED)
        base -= Pos(cx, cy, -1) * Cylinder(CSK_D / 2, 1, align=ON_BED)
    base += Pos(0, 0, top) * flat_text("BUDGET")
    return base


def build_pointer():
    """print pose: pointer face on the bed, collar + pin upward (pin points down in use)"""
    r = PIN_D / 2
    tab = Polygon((0, -PTR_TAB_W / 2), (PTR_TIP_R - 4, -PTR_TAB_W / 2), (PTR_TIP_R, 0),
                  (PTR_TIP_R - 4, PTR_TAB_W / 2), (0, PTR_TAB_W / 2), align=None)
    ptr = extrude(Circle(PTR_HUB_D / 2) + tab, PTR_T)
    ptr = chamfer(ptr.edges().group_by(Axis.Z)[0], 0.4)
    ptr += Pos(0, 0, PTR_T) * Cylinder(COLLAR_D / 2, COLLAR_H, align=ON_BED)
    csk_h = (CSK_D - PIN_D - PIN_FIT) / 2
    z = PTR_T + COLLAR_H
    stem = BASE_T - csk_h + 0.2
    pin = Pos(0, 0, z) * Cylinder(r, stem, align=ON_BED)
    pin += Pos(0, 0, z + stem - 0.01) * (Cone(r, r + BARB, BARB, align=ON_BED)
                                          + Pos(0, 0, BARB) * Cone(r + BARB, r - 0.7, 1.0, align=ON_BED))
    pin -= Pos(0, 0, z + 0.6) * Box(PIN_SLOT, 2 * PIN_D, 20, align=ON_BED)
    return ptr + pin


def build():
    parts = [build_base()]
    for i in range(len(CATEGORIES)):
        parts.append(Pos(BASE_D / 2 + 22, -85 + i * 34, 0) * build_pointer())
    return parts
