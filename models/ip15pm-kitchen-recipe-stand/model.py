"""ip15pm-kitchen-recipe-stand: kitchen stand for iPhone 15 Pro Max, landscape or portrait, 2 angles.

Spec: 150 x 100 mm base with two grooves in front of one back support:
- rear groove -> phone leans at ~70 deg (reading while standing close),
- front groove -> ~55 deg (reading from further away / sitting).
A 12 mm splash lip at the very front shields the lower edge of the screen and the bottom edge
from spills; the lip between the grooves is 6 mm so a phone in the front groove leans over it.
Stepped groove floor keeps buttons, port and speakers free in both orientations:
- portrait: the bottom edge stands on pads at 28-41 mm from centre; the centre 56 mm is
  recessed 3 mm (USB-C + speakers free); the long edges (buttons) touch nothing.
- landscape: the phone stands on end pads (|x| >= 58, 1.5 mm higher) = the outer 24 mm of each
  end, so the Action/volume/side buttons (30-80 mm from the top end) float 1.5 mm above the
  floor whichever long edge is down; the camera end overhangs free.
The back support (62 mm above the floor) touches the phone's back only at its rounded top edge.

Assumptions:
- Phone + case 76.7 + 2*CASE by 159.9 + 2*CASE by 8.25 + 2*CASE; 221 g + ~30 g case.
- Angles are nominal (+-3 deg; depend on the case's corner radius).
- Contact edges are 1 mm filleted / 0.8 mm chamfered. A felt strip on the support top and
  silicone pads under the base are recommended; wipe out the groove recesses after spills.

MEASURE BEFORE PRINTING (unverified values):
- PHONE_T + CASE: phone thickness in its case (groove geometry uses PT).
- SPEAKER_GAP: span of bottom speakers + USB-C (portrait recess; must be < 56 mm).
- BUTTON_FREE_END: distance from each phone end to the nearest button (landscape end pads
  must be shorter; ~28 mm).
- PHONE_W + CASE: width in case must be < 2 * PORTRAIT_PAD_X1 (82 mm).
"""

import math

from build123d import *

from cadlib import *

# Phone
PHONE_W = 76.7
PHONE_H = 159.9
PHONE_T = 8.25
CASE = 2.5
PHONE_G = 221
CASE_G = 30 if CASE > 0 else 0
SPEAKER_GAP = 56.0
BUTTON_FREE_END = 28.0

# Stand
ANGLES = (70.0, 55.0)          # rear groove, front groove
SUPPORT_H = 62.0               # support top above the groove floor
WIDTH = 150.0
DEPTH = 100.0
BASE_T = 4.0
FLOOR_Z = 8.0
RECESS = 3.0
LAND_RAISE = 1.5
SPLASH_H, MID_H = 12.0, 6.0
LIP_T = 4.0
SUPPORT_T = 6.0
SUPPORT_W = 100.0
PORTRAIT_PAD_X1 = 41.0

PT = PHONE_T + 2 * CASE
PL = PHONE_H + 2 * CASE
LAND_PAD_X = PL / 2 - (BUTTON_FREE_END - 4)


def _setback(a):
    """support-front distance from a groove's lip: back-bottom corner + lean run."""
    r = math.radians(a)
    return PT * math.sin(r) + 0.5 + SUPPORT_H / math.tan(r)


Y_L2 = LIP_T                                   # front groove lip (rear face)
Y_S = Y_L2 + _setback(ANGLES[1])               # support front face
Y_L1 = Y_S - _setback(ANGLES[0])               # rear groove lip (rear face)

_r = math.radians(ANGLES[1])
_c = (Y_L2 + 0.5 + math.cos(_r) * (PHONE_W / 2 + CASE), FLOOR_Z + math.sin(_r) * (PHONE_W / 2 + CASE))

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, _c[0], _c[1]), grams=PHONE_G + CASE_G)],
    print_orientation=(0, 0, 0),
    supports="auto",
    brim="on",                 # ABS, 150 x 100 mm flat base
)


def build() -> Part:
    base = Pos(0, DEPTH / 2, 0) * rounded_box(WIDTH, DEPTH, BASE_T, radius=8)
    block = Pos(0, Y_S / 2, 0) * rounded_box(WIDTH, Y_S, FLOOR_Z, radius=8)
    part = base + block
    # pads/recesses: cut the floor down by RECESS except the portrait pads, then add landscape pads
    for s in (-1, 1):
        for x0, x1 in ((0, SPEAKER_GAP / 2), (PORTRAIT_PAD_X1, WIDTH / 2 + 1)):
            cut = Pos(s * (x0 + x1) / 2, (Y_L2 + Y_S) / 2, FLOOR_Z) * Box(x1 - x0, Y_S - Y_L2, 2 * RECESS)
            part = part - cut
        pad = Pos(s * (LAND_PAD_X + WIDTH / 2) / 2, (Y_L2 + Y_S) / 2, FLOOR_Z - RECESS - 0.5) * Box(WIDTH / 2 - LAND_PAD_X, Y_S - Y_L2, RECESS + LAND_RAISE + 0.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        pad = chamfer(pad.edges().group_by(Axis.Z)[-1].filter_by(Axis.Y), 0.8)
        part = part + pad
    splash = Pos(0, LIP_T / 2, FLOOR_Z - 1) * Box(WIDTH, LIP_T, SPLASH_H + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    mid = Pos(0, Y_L1 - LIP_T / 2, FLOOR_Z - RECESS - 1) * Box(WIDTH, LIP_T, MID_H + RECESS + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for lip in (splash, mid):
        lip = fillet(lip.edges().group_by(Axis.Z)[-1].filter_by(Axis.X), 1.0)
        part = part + lip
    support = Pos(0, Y_S + SUPPORT_T / 2, 0) * Box(SUPPORT_W, SUPPORT_T, FLOOR_Z + SUPPORT_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    support = fillet(support.edges().filter_by(Axis.Y), 4)
    support = fillet(support.edges().group_by(Axis.Z)[-1].filter_by(Axis.X), 2.5)
    gusset = Pos(0, Y_S + SUPPORT_T - 0.5, BASE_T - 0.5) * Rot(0, 0, 90) * rib(30, 40, 6)
    part = part + support + gusset
    # trim lips/pads to the rounded footprint (no box corners hanging past the rounded base)
    part = part & (Pos(0, DEPTH / 2, 0) * rounded_box(WIDTH, DEPTH, 200, radius=8))
    return part
