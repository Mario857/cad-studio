"""closet-rod-support: mid-span J-hook support for a sagging 25 mm closet rod.

Spec: hangs from the underside of the closet shelf. A flat top plate takes 3 countersunk
wood screws driven upward into the shelf; a vertical arm drops down one side of the rod
and curls into a cradle under it. The cradle is open at the top (lip ends 15 deg above the
rod centre, inside the cradle circle), so the rod lifts straight up and out sideways.
Gussets brace the arm to the plate on both sides. Rod runs along Y.
Load 15 kg at the rod centre: rod -> cradle -> arm (tension) -> plate -> screws (pull-out).

Print orientation (90, 0, 0): the XZ profile lies flat on the bed, so every load path
(cradle hoop, arm tension, gusset/plate bending) runs inside layers - no layer-line peel.
Screw holes then run horizontally in print and are teardrop-shaped (tip = print-up).

Assumptions:
- Rod OD 25 mm; 1 mm radial clearance in the cradle.
- Rod top sits ROD_TOP_GAP = 40 mm under the shelf (room for hanger hooks / lifting out).
- Shelf is >= 15 mm wood/MDF/melamine; screws: 3x countersunk wood screw 4 mm (#8) x 25-30 mm,
  90 deg head <= 8 mm, driven from below. Screw positions keep driver access clear of the
  cradle and gussets.
- Mount is the shelf underside (the usual mid-span spot); for a back-wall mount use a
  separate wall-plate variant, since this plate is horizontal.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[],                       # filled below from params (rod centre)
    print_orientation=(90, 0, 0),   # profile flat on bed: loads run along layers
    supports="auto",
    brim="auto",
)

# Parameters
ROD_D = 25.0             # closet rod OD
CRADLE_CLEAR = 1.0       # radial clearance rod -> cradle
CRADLE_T = 6.0           # cradle hoop thickness
LIP_ANGLE = 15.0         # deg above horizontal where the lip ends (<= 22 keeps straight lift-out)
ARM_T = 6.0              # vertical arm thickness (X)
WIDTH = 24.0             # bracket width along the rod (Y)
ROD_TOP_GAP = 40.0       # rod top to shelf underside
PLATE_T = 6.0            # top plate thickness
PLATE_X_MIN = -76.0      # plate extent (X) relative to rod centre
PLATE_X_MAX = 36.0
GUSSET_OUT = 20.0        # outer gusset leg length
GUSSET_IN = 12.0         # inner gusset leg length (stays above the rod lift-out path)
SCREW_X = (-66.0, -48.0, 28.0)  # screw positions (X)
SCREW_CLEAR = 4.6        # shank clearance for 4 mm wood screw
SCREW_HEAD_D = 8.6       # countersink diameter (8 mm head + clearance)
EDGE_CHAMFER = 0.4       # elephant-foot chamfer on the bed face
LOAD_G = 15000           # 15 kg rod + clothes share

R_IN = ROD_D / 2 + CRADLE_CLEAR
R_OUT = R_IN + CRADLE_T
Z_C = R_OUT                              # rod centre height (cradle bottom on z=0)
Z_PLATE = Z_C + ROD_D / 2 + ROD_TOP_GAP  # plate underside
X_ARM_IN = -R_IN
X_ARM_OUT = -R_IN - ARM_T

META["loads"] = [dict(at=(0, 0, Z_C), grams=LOAD_G)]


def _profile() -> Sketch:
    # cradle hoop, open from LIP_ANGLE round to 180 deg (arm side)
    hoop = Pos(0, Z_C) * (Circle(R_OUT) - Circle(R_IN))
    big = 3 * R_OUT
    a = math.radians(LIP_ANGLE)
    wedge = Polygon(
        (0, Z_C),
        (big * math.cos(a), Z_C + big * math.sin(a)),
        (big, Z_C + big),
        (-big, Z_C + big),
        (-big, Z_C),
        align=None,
    )
    hoop = hoop - wedge
    arm = Polygon((X_ARM_OUT, Z_C - 1), (X_ARM_IN, Z_C - 1), (X_ARM_IN, Z_PLATE + 0.5),
                  (X_ARM_OUT, Z_PLATE + 0.5), align=None)
    plate = Polygon((PLATE_X_MIN, Z_PLATE), (PLATE_X_MAX, Z_PLATE),
                    (PLATE_X_MAX, Z_PLATE + PLATE_T), (PLATE_X_MIN, Z_PLATE + PLATE_T), align=None)
    g_out = Polygon((X_ARM_OUT + 0.5, Z_PLATE + 0.5), (X_ARM_OUT - GUSSET_OUT, Z_PLATE + 0.5),
                    (X_ARM_OUT + 0.5, Z_PLATE - GUSSET_OUT), align=None)
    g_in = Polygon((X_ARM_IN - 0.5, Z_PLATE + 0.5), (X_ARM_IN + GUSSET_IN, Z_PLATE + 0.5),
                   (X_ARM_IN - 0.5, Z_PLATE - GUSSET_IN), align=None)
    return hoop + arm + plate + g_out + g_in


def _screw_cutter(x: float) -> Part:
    length = PLATE_T + 2
    shank = Rot(-90, 0, 0) * teardrop_hole(SCREW_CLEAR, length, along="Y")
    shank = Pos(x, 0, Z_PLATE + PLATE_T / 2) * shank
    csk_h = (SCREW_HEAD_D - SCREW_CLEAR) / 2
    cone = Cone(SCREW_HEAD_D / 2, SCREW_CLEAR / 2, csk_h,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
    relief = Cylinder(SCREW_HEAD_D / 2, 1.0, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return shank + Pos(x, 0, Z_PLATE) * (cone + relief)


def build() -> Part:
    part = extrude(Plane.XZ * _profile(), amount=WIDTH / 2, both=True)
    for x in SCREW_X:
        part = part - _screw_cutter(x)
    # elephant-foot chamfer on the face that lands on the bed (-Y in use -> bottom in print)
    part = chamfer(part.edges().group_by(Axis.Y)[0], EDGE_CHAMFER)
    return part
