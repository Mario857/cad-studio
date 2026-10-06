"""money-gift-holder: birthday cash-gift stand, banknotes fanned out in slots + name/age plate.

Spec: 150 x 60 x 32 mm wedge-shaped stand. Five thin slots on the flat top are tilted
-36..+36° along a virtual fan centre below the stand, so folded banknotes stand fanned
out like a peacock tail. Each slot has a 45° lead-in and grips a note folded in half or
accordion-pleated and pinched at the bottom. The 45° front face carries the raised name
(NAME) and "HAPPY <AGE>TH" (AGE) — the face slopes up, so the text prints without support.

Assumptions: notes folded to ~0.3-1 mm thickness at the bottom (SLOT_W 1.8 mm grips that
with a light pinch); for thick pleated fans raise SLOT_W. Text size >= 7 mm, 0.6 mm raised.
Supports off: the ~0.8 cm2 flagged are the 45° undersides of the 0.6 mm letters on the slope.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(x, 14, 60), grams=3) for x in (-35, -18, 0, 18, 35)],
    print_orientation="auto",
    supports="off",
    brim="auto",
)

NAME = "EMMA"
AGE = 30

# Stand
L = 150.0
D = 60.0
H = 32.0
FRONT_H = 4.0               # height of the front edge; 45° face rises from there
TOP_FILLET = 1.0

# Slots
N_SLOTS = 5
FAN_SPREAD = 36.0           # outer slot tilt, degrees from vertical
FAN_R = 60.0                # virtual fan centre this far below the top
SLOT_W = 1.8
SLOT_LEN = 26.0             # along Y
SLOT_DEPTH = 24.0           # along the tilted slot axis
SLOT_Y = 14.0               # slot centre (Y) on the flat top
LEAD_IN = 1.5

# Text
NAME_SIZE = 10.0
AGE_SIZE = 7.0
RAISE = 0.6


def ordinal(n):
    suf = "TH" if 10 <= n % 100 <= 20 else {1: "ST", 2: "ND", 3: "RD"}.get(n % 10, "TH")
    return f"{n}{suf}"


def slope_text(txt, size, s):
    """raised text on the 45° front face; s = distance up the slope from the front edge"""
    t = label(txt, size=size, depth=RAISE + 0.2)
    bb = t.bounding_box()
    t = Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -0.2) * t
    y = -D / 2 + s / math.sqrt(2)
    z = FRONT_H + s / math.sqrt(2)
    return Pos(0, y, z) * (Rot(45, 0, 0) * t)


def build():
    run = H - FRONT_H                                  # 45° face: equal run and rise
    prof = Polygon((-D / 2, 0), (D / 2, 0), (D / 2, H), (-D / 2 + run, H), (-D / 2, FRONT_H), align=None)
    stand = extrude(Plane.YZ * prof, L / 2, both=True)
    stand = chamfer(stand.edges().group_by(Axis.Z)[0], 0.4)
    stand = fillet(stand.edges().filter_by(Axis.X).group_by(Axis.Z)[-1], TOP_FILLET)

    slope_len = run * math.sqrt(2)
    stand += slope_text(NAME, NAME_SIZE, slope_len * 0.68)
    stand += slope_text(f"HAPPY {ordinal(AGE)}", AGE_SIZE, slope_len * 0.28)

    for i in range(N_SLOTS):
        th = -FAN_SPREAD + 2 * FAN_SPREAD * i / (N_SLOTS - 1)
        x = (FAN_R) * math.sin(math.radians(th))
        cut = Box(SLOT_W, SLOT_LEN, SLOT_DEPTH + 10, align=(Align.CENTER, Align.CENTER, Align.MAX))
        trap = Polygon((-SLOT_W / 2, 0), (SLOT_W / 2, 0), (SLOT_W / 2 + LEAD_IN, LEAD_IN + 0.01),
                       (-SLOT_W / 2 - LEAD_IN, LEAD_IN + 0.01), align=None)       # 45° lead-in
        lead = extrude(Plane.XZ * trap, SLOT_LEN / 2, both=True)
        cutter = Pos(0, 0, 10) * cut + Pos(0, 0, -LEAD_IN) * lead
        stand -= Pos(x, SLOT_Y, H) * (Rot(0, th, 0) * cutter)
    return stand
