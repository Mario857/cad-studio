"""ip15pm-magsafe-desk-stand: portrait desk stand for iPhone 15 Pro Max with an Apple MagSafe puck.

Spec: the phone (in a MagSafe case) leans back against a 65 deg (from horizontal) back plate
that carries the Apple MagSafe charger puck (Ø56 x 5.5 mm) flush in a U-pocket. The phone's
bottom edge rests on two corner pads with retaining lips; the 56 mm wide centre between the pads
is open so the USB-C port and both bottom speakers stay clear (a straight USB-C plug fits:
~35 mm of free space below the port). The puck cable goes through a slot in the plate, drops
behind the plate and leaves through a rear channel in the base. Nothing touches the phone's long
edges (Action button, volume, side button) and the plate ends below the camera plateau.
Base 115 x 90 mm, wide enough to stay tip-safe with the phone on it.

Assumptions:
- Phone + case: 76.7 + 2*CASE wide, 159.9 + 2*CASE tall, 8.25 + 2*CASE thick; 221 g + ~30 g case.
- MagSafe ring centre sits ~80 mm above the phone's bottom edge (bare phone), centred in width.
- Puck cable/strain relief fits a 6 mm slot; the slot runs from the puck centre downward, so
  both centre-exit and edge-exit cables work (rotate the puck so its cable points down).
- Camera plateau starts ~50 mm below the phone's top edge; the plate top stays below it.
- Contact edges (plate face, pads, lips) are 0.8 mm chamfered / 1 mm filleted. A self-adhesive
  felt or silicone strip on the pad tops and the lip backs prevents scuffs on the case.

MEASURE BEFORE PRINTING (unverified values):
- PHONE_W/H/T and CASE: measure phone in its case with calipers (width, height, thickness).
- MAGSAFE_FROM_BOTTOM: put the puck on the back of the phone, let it snap, measure from the
  phone's bottom edge (bare) to the puck centre.
- PUCK_D / PUCK_T: Apple puck is Ø56 x 5.5 mm; third-party pucks differ — measure.
- CABLE_SLOT_W: width of the puck cable's strain relief.
- CAM_FROM_TOP: phone top edge to the lower edge of the camera plateau (~4 mm protrusion).
- SPEAKER_GAP: span of the bottom speaker grilles + USB-C (must be < this).
"""

from build123d import *

from cadlib import *

# Phone / accessory
PHONE_W = 76.7
PHONE_H = 159.9
PHONE_T = 8.25
CASE = 2.5                  # mm added per side by the case (0 = bare phone)
PHONE_G = 221
CASE_G = 30 if CASE > 0 else 0
MAGSAFE_FROM_BOTTOM = 80.0  # bare phone bottom edge -> MagSafe centre
CAM_FROM_TOP = 50.0         # phone top edge -> lower edge of camera plateau
PUCK_D = 56.0
PUCK_T = 5.5
PUCK_FIT = 0.4              # diametral clearance
CABLE_SLOT_W = 6.0
SPEAKER_GAP = 56.0          # open centre of the ledge (USB-C + speakers)

# Stand
ANGLE = 65.0                # plate angle from horizontal (viewing angle)
LEDGE_Z = 35.0              # height of the phone's bottom/back corner above the desk
PLATE_T = PUCK_T + 2.5
PLATE_TOP_ABOVE_PUCK = 22.0 # plate top above puck centre (< radius -> open-top U pocket)
PAD_EXTRA = 2.0             # pads reach this far past the phone edge
LIP_H = 6.0
LIP_T = 3.0
PHONE_GAP = 1.2             # clearance phone thickness -> lip
BASE_X0, BASE_X1 = -40.0, 75.0
BASE_W = 90.0
BASE_T = 6.0
GROOVE_W, GROOVE_D = 7.0, 3.0

PW = PHONE_W + 2 * CASE
PT = PHONE_T + 2 * CASE
PH = PHONE_H + 2 * CASE
PUCK_CX = CASE + MAGSAFE_FROM_BOTTOM          # along the plate from the ledge
PLATE_W = PW + 2 * PAD_EXTRA

# Local plate frame: x up the slope, y across, z out of the plate face (towards the phone).
LOCAL = Pos(0, 0, LEDGE_Z) * Rot(0, -ANGLE, 0)

import math
_u = (math.cos(math.radians(ANGLE)), math.sin(math.radians(ANGLE)))
_n = (-math.sin(math.radians(ANGLE)), math.cos(math.radians(ANGLE)))
_pc = (_u[0] * (CASE + PH / 2) + _n[0] * PT / 2, LEDGE_Z + _u[1] * (CASE + PH / 2) + _n[1] * PT / 2)

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(_pc[0], 0, _pc[1]), grams=PHONE_G + CASE_G)],
    print_orientation="auto",
    supports="auto",
    brim="on",                 # ABS, 115 x 90 mm flat base
)


def build() -> Part:
    top = PUCK_CX + PLATE_TOP_ABOVE_PUCK
    plate = Box(top + 60, PLATE_W, PLATE_T, align=(Align.MAX, Align.CENTER, Align.MAX))
    plate = Pos(top, 0, 0) * plate
    plate = chamfer(plate.edges().group_by(Axis.Z)[-1], 0.8)

    # pads: leg below the ledge + lip in front of the phone, one per side
    pad_w = (PLATE_W - SPEAKER_GAP) / 2
    pads = []
    for s in (-1, 1):
        y = s * (SPEAKER_GAP / 2 + pad_w / 2)
        leg = Box(80, pad_w, PT + PHONE_GAP + LIP_T, align=(Align.MAX, Align.CENTER, Align.MIN))
        lip = Pos(0, 0, PT + PHONE_GAP) * Box(LIP_H, pad_w, LIP_T, align=(Align.MIN, Align.CENTER, Align.MIN))
        lip = fillet(lip.edges().group_by(Axis.X)[-1], 1.0)
        leg = chamfer(leg.edges().group_by(Axis.X)[-1], 0.8)
        pads.append(Pos(0, y, 0) * (leg + lip))

    local = plate + pads[0] + pads[1]
    # puck pocket (open at the top) + cable slot through the plate
    pocket = Pos(PUCK_CX, 0, 0) * Cylinder((PUCK_D + PUCK_FIT) / 2, PUCK_T, align=(Align.CENTER, Align.CENTER, Align.MAX))
    slot_len = (PUCK_D / 2 + 4)
    cslot = Pos(PUCK_CX - slot_len / 2, 0, 0) * Box(slot_len, CABLE_SLOT_W, 3 * PLATE_T)
    local = local - pocket - cslot

    stand = LOCAL * local
    base = Pos((BASE_X0 + BASE_X1) / 2, 0, 0) * rounded_box(BASE_X1 - BASE_X0, BASE_W, BASE_T, radius=8)
    part = stand + base
    part = part & Box(1000, 1000, 500, align=(Align.CENTER, Align.CENTER, Align.MIN))
    groove = Pos((BASE_X1 + 0) / 2 + 2, 0, BASE_T) * Box(BASE_X1, GROOVE_W, GROOVE_D * 2)
    part = part - groove
    return part
