"""ip15pm-wall-charging-dock: screw-mounted wall cradle for iPhone 15 Pro Max, charged from below.

Spec: a back plate (2 screws, counterbored so the heads sit below the phone) carries a 30 mm deep
cradle the phone (in its case) drops into, portrait, USB-C down. The cradle floor is only two
corner pads; the 56 mm centre is open from back to front, so a USB-C cable coming up from below
plugs straight into the phone and its plug/overmold hangs through the open bottom. The front has
two 28 mm corner ears only, so the speakers, USB-C and most of the screen stay clear. Side walls
are 30 mm tall -> the Action button, volume and side button (all > 80 mm above the bottom edge)
stay free; the back plate ends 58 mm up, well below the camera plateau.

Assumptions:
- Phone + case: 76.7 + 2*CASE by 159.9 + 2*CASE by 8.25 + 2*CASE; 221 g + ~30 g case.
- Wall screws: 2x Ø4 mm pan-head wood screws (or M4) with plugs; head Ø <= 9 mm.
- Printed as used (upright): the pads carry the phone along the layers; holes are teardrops.
- Contact edges are 0.8 mm chamfered; a felt strip on the back plate and pad tops avoids
  scuffing the case.

MEASURE BEFORE PRINTING (unverified values):
- PHONE_W/T and CASE: phone in its case, calipers (cradle clearance is POCKET_GAP).
- SPEAKER_GAP: span of the bottom speaker grilles + USB-C port (must be < 56 mm).
- PLUG_OVERMOLD_W: widest part of your USB-C plug (must pass the centre gap; it does up to 56).
- BUTTON_MIN_Z: lowest button above the phone's bottom edge (must be > WALL_H).
- SCREW_D / SCREW_HEAD_D: your wall screws.
"""

from build123d import *

from cadlib import *

# Phone / accessory
PHONE_W = 76.7
PHONE_H = 159.9
PHONE_T = 8.25
CASE = 2.5
PHONE_G = 221
CASE_G = 30 if CASE > 0 else 0
SPEAKER_GAP = 56.0
PLUG_OVERMOLD_W = 14.0       # info only: must be < SPEAKER_GAP
BUTTON_MIN_Z = 80.0          # info only: must be > WALL_H
SCREW_D = 4.5                # clearance for a 4 mm screw
SCREW_HEAD_D = 9.5
SCREW_HEAD_H = 3.5

# Cradle (wall at y = 0, phone in front at +Y)
POCKET_GAP = 1.5
BACK_T = 6.0
PLATE_H = 58.0
WALL = 3.0
WALL_H = 30.0
FLOOR_T = 3.0
EAR_W = 15.0
EAR_H = 28.0
SCREW_Z = (38.0, 50.0)

PW, PT = PHONE_W + 2 * CASE, PHONE_T + 2 * CASE
IW, ID = PW + POCKET_GAP, PT + POCKET_GAP
OW = IW + 2 * WALL

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[dict(at=(0, BACK_T + ID / 2, FLOOR_T + (PHONE_H + 2 * CASE) / 2), grams=PHONE_G + CASE_G)],
    print_orientation=(0, 0, 0),  # upright: phone load runs along the layers of pads/walls
    supports="auto",
    brim="on",                 # tall narrow footprint: brim holds it on the bed
)


def build() -> Part:
    plate = Pos(0, BACK_T / 2, 0) * Box(OW, BACK_T, PLATE_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    plate = fillet(plate.edges().filter_by(Axis.Y), 6)
    plate = chamfer(plate.edges().filter_by(Axis.X).group_by(Axis.Y)[-1].group_by(Axis.Z)[-1], 0.8)
    part = plate
    pad_w = (IW - SPEAKER_GAP) / 2 + WALL
    yd = BACK_T + ID + WALL
    for s in (-1, 1):
        xo = s * (OW / 2 - pad_w / 2)
        pad = Pos(xo, BACK_T + (ID + WALL) / 2, 0) * Box(pad_w, ID + WALL, FLOOR_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
        pad = chamfer(pad.edges().filter_by(Axis.Y).group_by(Axis.Z)[-1], 0.8)
        side = Pos(s * (OW / 2 - WALL / 2), BACK_T + (ID + WALL) / 2, 0) * Box(WALL, ID + WALL, WALL_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
        side = fillet(side.edges().group_by(Axis.Z)[-1], 1.0)
        ear = Pos(s * (OW / 2 - EAR_W / 2), yd - WALL / 2, 0) * Box(EAR_W, WALL, EAR_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
        ear = chamfer(ear.edges().filter_by(Axis.Z).group_by(Axis.X)[0 if s > 0 else -1], 0.8)
        ear = chamfer(ear.edges().group_by(Axis.Z)[-1], 0.8)
        part = part + pad + side + ear
    for z in SCREW_Z:
        part = part - Pos(0, BACK_T / 2, z) * teardrop_hole(SCREW_D, BACK_T + 2, along="Y")
        part = part - Pos(0, BACK_T, z) * teardrop_hole(SCREW_HEAD_D, 2 * SCREW_HEAD_H, along="Y")
    return part
