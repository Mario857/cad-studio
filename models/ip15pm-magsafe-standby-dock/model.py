"""ip15pm-magsafe-standby-dock: landscape nightstand dock (iOS StandBy) with an Apple MagSafe puck.

Spec: the phone (in a MagSafe case) lies in landscape against a 70 deg back plate that holds an
Apple MagSafe puck (Ø56 x 5.5 mm) flush in an open-top U pocket centred behind the phone. The phone's long
edge stands on two end pads (only the outer 24 mm at each end) with retaining lips, so the
Action button, volume buttons and side button (all 30-80 mm from the phone's top end) hang free
whichever long edge is down. The plate is only 65 mm wide, so the camera plateau (either end)
and the USB-C port/speakers (phone's short ends) are clear. The puck cable passes through a slot
in the plate, drops behind it and leaves the base through a rear channel. Wide 200 x 92 x 12 mm
base with a soft rounded top edge for a solid, "weighted" look.

Assumptions:
- Phone + case: 76.7 + 2*CASE by 159.9 + 2*CASE by 8.25 + 2*CASE; 221 g + ~30 g case.
- MagSafe centre is centred across the phone width and ~MAGSAFE_FROM_BOTTOM above the bottom
  end, i.e. ~at the middle of the length (MAGSAFE_OFFSET shifts it).
- Buttons are > BUTTON_FREE_END from either phone end; camera plateau is within CAM_FROM_TOP of
  the top end.
- Contact edges are 0.8 mm chamfered / 1 mm filleted. Stick felt or silicone pads on the end-pad
  tops and lip backs, and 4 rubber feet under the base for grip on a nightstand.

MEASURE BEFORE PRINTING (unverified values):
- PHONE_W/H/T and CASE: phone in its case, calipers.
- MAGSAFE_FROM_BOTTOM: snap the puck onto the phone, measure bottom end -> puck centre.
- PUCK_D / PUCK_T: Apple puck Ø56 x 5.5; third-party pucks differ.
- CABLE_SLOT_W: puck cable strain-relief width.
- BUTTON_FREE_END: distance from each phone end to the nearest button (Action button on the
  left, side button on the right); the end pads must be shorter than this.
- CAM_FROM_TOP: top end -> inner edge of the camera plateau (protrudes ~4 mm).
"""

import math

from build123d import *

from cadlib import *

# Phone / accessory
PHONE_W = 76.7
PHONE_H = 159.9
PHONE_T = 8.25
CASE = 2.5
PHONE_G = 221
CASE_G = 30 if CASE > 0 else 0
MAGSAFE_FROM_BOTTOM = 80.0
CAM_FROM_TOP = 50.0
BUTTON_FREE_END = 24.0
PUCK_D = 56.0
PUCK_T = 5.5
PUCK_FIT = 0.4
CABLE_SLOT_W = 6.0

# Dock
ANGLE = 70.0                # plate angle from horizontal
LEDGE_Z = 20.0              # phone's resting edge (back corner) above the table
PLATE_T = PUCK_T + 2.5
PLATE_TOP_ABOVE_PUCK = 18.0 # < puck radius: open-top U pocket, no ceiling to support
PAD_OUT = 2.0               # pads reach past the phone ends
LIP_H = 6.0
LIP_T = 3.0
PHONE_GAP = 1.2
BASE_X0, BASE_X1 = -32.0, 60.0
BASE_W = 200.0
BASE_T = 12.0
BASE_TOP_R = 4.0
GROOVE_W, GROOVE_D = 7.0, 3.0

PW = PHONE_W + 2 * CASE     # across the slope (landscape)
PL = PHONE_H + 2 * CASE     # along Y
PT = PHONE_T + 2 * CASE
PUCK_X = PW / 2             # puck centre up the slope
MAGSAFE_OFFSET = MAGSAFE_FROM_BOTTOM - PHONE_H / 2
PLATE_W = 2 * (PL / 2 - CASE - CAM_FROM_TOP)

LOCAL = Pos(0, 0, LEDGE_Z) * Rot(0, -ANGLE, 0)
_c, _s = math.cos(math.radians(ANGLE)), math.sin(math.radians(ANGLE))
_pc = (_c * PW / 2 - _s * PT / 2, LEDGE_Z + _s * PW / 2 + _c * PT / 2)

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(_pc[0], 0, _pc[1]), grams=PHONE_G + CASE_G)],
    print_orientation="auto",
    supports="auto",
    brim="on",                 # ABS, 200 x 92 mm flat base
)


def build() -> Part:
    top = PUCK_X + PLATE_TOP_ABOVE_PUCK
    plate = Pos(top, 0, 0) * Box(top + 60, PLATE_W, PLATE_T, align=(Align.MAX, Align.CENTER, Align.MAX))
    plate = chamfer(plate.edges().group_by(Axis.Z)[-1], 0.8)

    pad_w = BUTTON_FREE_END + CASE + PAD_OUT
    local = plate
    for s in (-1, 1):
        y = s * (PL / 2 + PAD_OUT - pad_w / 2)
        leg = Box(60, pad_w, PT + PHONE_GAP + LIP_T, align=(Align.MAX, Align.CENTER, Align.MIN))
        leg = chamfer(leg.edges().group_by(Axis.X)[-1].group_by(Axis.Z)[0], 0.8)
        lip = Pos(0, 0, PT + PHONE_GAP) * Box(LIP_H, pad_w, LIP_T, align=(Align.MIN, Align.CENTER, Align.MIN))
        lip = fillet(lip.edges().group_by(Axis.X)[-1], 1.0)
        local = local + Pos(0, y, 0) * (leg + lip)

    pocket = Pos(PUCK_X, MAGSAFE_OFFSET, 0) * Cylinder((PUCK_D + PUCK_FIT) / 2, PUCK_T, align=(Align.CENTER, Align.CENTER, Align.MAX))
    slot_len = top + 4             # runs out through the plate top: no ceiling to bridge
    cslot = Pos(top + 2 - slot_len / 2, MAGSAFE_OFFSET, 0) * Box(slot_len, CABLE_SLOT_W, 3 * PLATE_T)
    local = local - pocket - cslot

    base = Pos((BASE_X0 + BASE_X1) / 2, 0, 0) * rounded_box(BASE_X1 - BASE_X0, BASE_W, BASE_T, radius=12, top_radius=BASE_TOP_R)
    part = LOCAL * local + base
    part = part & Box(1000, 1000, 500, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # rear channel starts behind the plate's back face (no tunnel ceiling)
    xb = (BASE_T - LEDGE_Z + PLATE_T * _c) / _s * _c + PLATE_T * _s + 1
    groove = Pos((xb + BASE_X1 + 5) / 2, MAGSAFE_OFFSET, BASE_T) * Box(BASE_X1 + 5 - xb, GROOVE_W, GROOVE_D * 2)
    return part - groove
