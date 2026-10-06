"""ip15pm-bike-handlebar-mount: handlebar phone cradle for iPhone 15 Pro Max (31.8 or 22.2 mm bars).

Spec: three printed parts, laid out flat in their print orientation:
1. Cradle plate (5 mm) the phone (in its case) lies on, screen up, USB-C towards the rider.
   Two bottom corner lips (56 mm centre gap keeps USB-C + speakers clear) and side lips along
   the lower 50 mm only (Action/volume/side buttons sit higher and stay free). The plate ends
   CAM_FROM_TOP below the phone's top so the camera plateau overhangs free. A pair of 4 x 24 mm
   slots takes a 20 mm silicone strap/band across the phone just below the buttons.
2. Upper clamp block: teardrop (pointed) bore over the bar, flat top bolted under the plate.
3. Lower clamp half: the same pointed bore under the bar, hex nut pockets underneath.
   Both pointed bores print without support and act as V-blocks (4 line contacts on the bar).
Two M4 countersunk bolts go from the plate top (heads flush, under the phone) through the upper
block and lower half into the nuts: the same two bolts hold the plate and clamp the bar (2 mm
clamping gap). Tilt the cradle by rotating the clamp on the bar before tightening.
Bar size: set BAR_D = 31.8 (modern MTB/road) or 22.2 (BMX/older/flat bars) and re-run; the
bolt length is computed (M4 x BOLT_LEN countersunk: 55 mm for 31.8, 40 mm for 22.2).

Strength: the plate prints flat, so the phone's bump loads bend it along its layers; both clamp
halves print with the split face on the bed (bolt tension and bore hoop load run in-layer or in
compression). Design load: phone 251 g x 4 g bumps ~ 1 kg at the plate centre.

Assumptions:
- Phone + case 76.7 + 2*CASE by 159.9 + 2*CASE by 8.25 + 2*CASE.
- 1 mm rubber strip (inner tube) inside the clamp (RUBBER) for grip and bar protection.
- Lips/plate edges touching the phone are 0.8 mm chamfered. A thin silicone/foam pad on the
  plate damps vibration; note Apple warns that high-amplitude vibration (e.g. motorcycles) can
  damage the iPhone camera's OIS — this mount is meant for bicycles.

MEASURE BEFORE PRINTING (unverified values):
- BAR_D: measure the bar where the mount goes (calipers): 22.2, 25.4, 31.8 or 35 mm.
- PHONE_W/T, CASE: phone in its case (lip clearance PHONE_GAP).
- BUTTON_FREE_BOTTOM: phone bottom edge -> lowest button (side lips + strap must stay below).
- CAM_FROM_TOP: phone top edge -> lower edge of the camera plateau.
- STRAP_W: your silicone band width (slot length = STRAP_W + 4).
"""

import math

from build123d import *

from cadlib import *

# Phone / accessories
PHONE_W = 76.7
PHONE_H = 159.9
PHONE_T = 8.25
CASE = 2.5
PHONE_G = 221
BUTTON_FREE_BOTTOM = 80.0
CAM_FROM_TOP = 50.0
SPEAKER_GAP = 56.0
BAR_D = 31.8
RUBBER = 1.0
STRAP_W = 20.0

# Cradle
PLATE_T = 5.0
PHONE_GAP = 0.5
LIP_T = 3.0
SIDE_LIP_L = 50.0
STRAP_Y = 68.0               # strap centre above the phone's bottom edge
SLOT_W = 4.0
# Clamp
CL = 24.0                    # clamp length along the bar
SPLIT = 1.0                  # half of the clamping gap
M4_D, M4_HEAD_D = 4.5, 8.6
M4_NUT_AF, M4_NUT_T = 7.0, 3.2
LAYOUT = 30.0                # spacing of the parts on the bed

PW, PH, PT = PHONE_W + 2 * CASE, PHONE_H + 2 * CASE, PHONE_T + 2 * CASE
R = BAR_D / 2 + RUBBER
BOLT_Y = R + 6.0
CLAMP_W = 2 * (R + 12.0)
UP_H = R * math.sqrt(2) + 3 - SPLIT
LO_H = UP_H                 # both halves are V-blocks (pointed bores)
STACK = PLATE_T + UP_H + 2 * SPLIT + LO_H
BOLT_LEN = 5 * math.floor((STACK - 1.5) / 5)
NUT_POCKET = STACK - BOLT_LEN + M4_NUT_T + 0.3
PLATE_W = PW + 2 * (SLOT_W + 6.5)
YB = -PH / 2                 # phone bottom edge (plate centre = phone centre = bar)
PLATE_Y0, PLATE_Y1 = YB - LIP_T - PHONE_GAP, YB + PH - CAM_FROM_TOP

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[dict(at=(0, 0, PLATE_T + PT / 2), grams=4 * (PHONE_G + 30))],
    print_orientation=(0, 0, 0),  # each part is already laid out in its strongest print pose
    supports="auto",
    brim="on",                 # ABS, 98 x 121 mm flat plate
)


def plate() -> Part:
    p = Pos(0, (PLATE_Y0 + PLATE_Y1) / 2, 0) * rounded_box(PLATE_W, PLATE_Y1 - PLATE_Y0, PLATE_T, radius=6)
    p = chamfer(p.edges().group_by(Axis.Z)[-1], 0.8)
    lh = PT - 1.0
    xi = PW / 2 + PHONE_GAP
    for s in (-1, 1):
        side = Pos(s * (xi + LIP_T / 2), PLATE_Y0 + (SIDE_LIP_L + LIP_T + PHONE_GAP) / 2, PLATE_T - 0.5) * Box(LIP_T, SIDE_LIP_L + LIP_T + PHONE_GAP, lh + 0.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        bw = xi + LIP_T - SPEAKER_GAP / 2
        bot = Pos(s * (SPEAKER_GAP / 2 + bw / 2), PLATE_Y0 + LIP_T / 2, PLATE_T - 0.5) * Box(bw, LIP_T, lh + 0.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        lip = side + bot
        lip = chamfer(lip.edges().group_by(Axis.Z)[-1], 0.8)
        p = p + lip
        p = p - Pos(s * (xi + LIP_T + SLOT_W / 2 + 1), YB + STRAP_Y, PLATE_T) * slot(STRAP_W + 4 - SLOT_W, SLOT_W, PLATE_T + 2).rotate(Axis.Z, 90)
    for y in (-BOLT_Y, BOLT_Y):
        p = p - Pos(0, y, PLATE_T) * bolt_hole("M4", PLATE_T + 2, head="csk")
    return p


def upper() -> Part:
    b = Box(CL, CLAMP_W, UP_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    b = fillet(b.edges().filter_by(Axis.Z), 3)
    b = b - Pos(0, 0, -SPLIT) * teardrop_hole(2 * R, CL + 2, along="X")
    for y in (-BOLT_Y, BOLT_Y):
        b = b - Pos(0, y, UP_H + 1) * Cylinder(M4_D / 2, UP_H + 2, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return b


def lower() -> Part:
    """Printed split face down; in use it is flipped under the bar."""
    b = Box(CL, CLAMP_W, LO_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    b = fillet(b.edges().filter_by(Axis.Z), 3)
    b = b - Pos(0, 0, -SPLIT) * teardrop_hole(2 * R, CL + 2, along="X")
    for y in (-BOLT_Y, BOLT_Y):
        b = b - Pos(0, y, LO_H + 1) * Cylinder(M4_D / 2, LO_H + 2, align=(Align.CENTER, Align.CENTER, Align.MAX))
        b = b - Pos(0, y, LO_H) * nut_trap("M4", NUT_POCKET)
    return b


def build():
    x = PLATE_W / 2 + LAYOUT
    return [plate(), Pos(x, 0, 0) * upper(), Pos(x + CL + LAYOUT, 0, 0) * lower()]
