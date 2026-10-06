"""ip15pm-shower-wall-holder: shower wall pocket for an iPhone 15 Pro Max in a waterproof pouch/case.

IMPORTANT: the phone must stay in a waterproof pouch (or a fully sealed waterproof case) in the
shower. IP68 does not cover hot water, steam, soap or shampoo; this holder only keeps the pouch
in place and sheds water — it does not protect the phone.

Spec: back plate (screws or adhesive) with a pocket the pouched phone drops into, portrait.
- The two floor pads slope 10 deg down towards the wall, so the phone leans back against the
  plate (stable) and water runs back into 3 mm drain slots along the wall side of each pad.
- The floor centre (60 mm) is fully open: water and soap run straight through, and the USB-C
  port/speakers area of the phone is never pressed.
- Front is two 28 mm corner ears only; side walls 35 mm (buttons at > 80 mm stay free).
- All upward faces are 45 deg chamfered (plate top, wall and ear tops) so splashes run off;
  no flat ledges collect water.
Mounting: 2 Ø4 pan-head stainless screws (heads in counterbores, plugs in the tile) or 2-3 strips of
3M VHB on the flat back (clean tile with alcohol first; 72 h cure before loading).

Assumptions:
- Pouch outside ~ 98 x 190 x 18 mm with the phone (in a thin case) inside; 221 g + ~60 g.
- ABS is fine in hot water spray; keep it out of direct >80 C water.
- A silicone/felt strip is not needed (pouch is soft); edges touching the pouch are 0.8 mm
  chamfered / 1 mm filleted anyway.

MEASURE BEFORE PRINTING (unverified values):
- POUCH_W / POUCH_T: width and thickness of your pouch with the phone inside (lay it flat,
  press lightly, measure with calipers). Pocket = POUCH + POCKET_GAP.
- POUCH_BUTTON_Z: how high the phone's lowest button sits above the pouch bottom (> WALL_H).
- SCREW_D / SCREW_HEAD_D: stainless screws you use (pan head).
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
POUCH_G = 60
POUCH_W = 98.0
POUCH_T = 18.0
POUCH_BUTTON_Z = 80.0      # info: must be > WALL_H
SCREW_D, SCREW_HEAD_D, SCREW_HEAD_H = 4.5, 9.5, 3.5

# Holder (wall at y = 0, pocket in front at +Y)
POCKET_GAP = 2.0
BACK_T = 6.0
PLATE_H = 66.0
WALL = 3.0
WALL_H = 35.0
EAR_W, EAR_H = 15.0, 28.0
FLOOR_T = 3.0              # pad thickness at the front
FLOOR_SLOPE = 10.0         # deg, down towards the wall
CENTER_GAP = 60.0
DRAIN_W = 3.0
SCREW_Z = (44.0, 58.0)

IW, ID = POUCH_W + POCKET_GAP, POUCH_T + POCKET_GAP
OW = IW + 2 * WALL
RISE = ID * math.tan(math.radians(FLOOR_SLOPE))

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[dict(at=(0, BACK_T + ID / 2, FLOOR_T + 95), grams=PHONE_G + POUCH_G)],
    print_orientation=(0, 0, 0),  # upright: the pads carry the phone along the layers
    supports="auto",
    brim="on",                 # tall narrow footprint
)


def build() -> Part:
    plate = Pos(0, BACK_T / 2, 0) * Box(OW, BACK_T, PLATE_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    plate = fillet(plate.edges().filter_by(Axis.Y), 6)
    plate = chamfer(plate.edges().filter_by(Axis.X).group_by(Axis.Y)[-1].group_by(Axis.Z)[-1], BACK_T - 1.5)
    part = plate
    pad_w = (IW - CENTER_GAP) / 2 + WALL
    y0, y1 = BACK_T - 2.0, BACK_T + ID + WALL
    # pad profile in YZ: top slopes down towards the wall
    prof = Polygon((y0, 0), (y1, 0), (y1, FLOOR_T + RISE), (BACK_T + ID, FLOOR_T + RISE), (BACK_T, FLOOR_T), (y0, FLOOR_T), align=None)
    for s in (-1, 1):
        xo = s * (OW / 2 - pad_w / 2)
        pad = Pos(xo, 0, 0) * extrude(Plane.YZ * prof, pad_w / 2, both=True)
        side = Pos(s * (OW / 2 - WALL / 2), (y0 + y1) / 2, 0) * Box(WALL, y1 - y0, WALL_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
        side = chamfer(side.edges().group_by(Axis.Z)[-1].filter_by(Axis.Y), 1.4)
        ear = Pos(s * (OW / 2 - EAR_W / 2), y1 - WALL / 2, 0) * Box(EAR_W, WALL, EAR_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
        ear = chamfer(ear.edges().filter_by(Axis.Z).group_by(Axis.X)[0 if s > 0 else -1], 0.8)
        ear = chamfer(ear.edges().group_by(Axis.Z)[-1].filter_by(Axis.X), 1.4)
        part = part + pad + side + ear
        # drain slot along the wall side of the pad
        part = part - Pos(xo - s * 1.0, BACK_T + 0.5 + DRAIN_W / 2, -1) * Box(pad_w - WALL - 4, DRAIN_W, 20, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for z in SCREW_Z:
        part = part - Pos(0, BACK_T / 2, z) * teardrop_hole(SCREW_D, BACK_T + 2, along="Y")
        part = part - Pos(0, BACK_T, z) * teardrop_hole(SCREW_HEAD_D, 2 * SCREW_HEAD_H, along="Y")
    return part
