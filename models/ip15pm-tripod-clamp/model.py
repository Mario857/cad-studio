"""ip15pm-tripod-clamp: spring-free, screw-locked tripod clamp for iPhone 15 Pro Max (landscape).

Spec: two printed parts.
- Base: 30 x 35 x 18 mm block with a 1/4"-20 hex nut captured in a side slot (tripod screw goes
  up from below, the nut is pulled onto a 3 mm floor), the lower jaw (phone ledge + 5 mm front
  lip) and a 16 x 10 mm column rising to 136 mm.
- Slider: sleeve on the column with the upper jaw (hook + lip) and a cold shoe on top. Press the
  slider down onto the phone, then tighten an M5 thumb screw (nut in a hex pocket on the side
  wall) against the column. No springs. Grips phone(+case) widths 74-92 mm.
The phone sits in landscape with its long edges in the jaws. The jaws are only 20-30 mm wide:
place them ~35-60 mm from the phone's bottom end (USB-C end) so the Action button, volume and
side button (30-80 mm from the top end) stay free; the ends (USB-C, speakers, camera) are clear.

Print: both parts upright as modelled (layers horizontal, the jaw/hook loads run in-layer; all
roofs are 45 deg gables, holes teardrops). Parts are laid out side by side, not assembled.

Assumptions:
- Phone + case thickness 8.25 + 2*CASE; width range covers bare to thick case.
- 1/4"-20 hex nut 7/16" (11.11 mm) AF x 5.6 mm; M5 nut 8 mm AF x 4 mm; M5 x 16 thumb screw.
- Cold shoe foot 18 x 18 x 2 mm (standard).
- Jaw edges touching the phone are 0.8 mm chamfered / 1 mm filleted; a strip of 1 mm silicone
  or felt on the ledge, hook underside and lips adds grip and prevents scratches.

MEASURE BEFORE PRINTING (unverified values):
- PHONE_T + CASE: phone thickness in its case (jaw depth = PT + JAW_GAP).
- PHONE_W range: width in the case must be within WIDTH_MIN..WIDTH_MAX.
- BUTTON_FREE_BOTTOM: free length from the bottom end to the first button (~80 mm).
- NUT14_AF / NUT14_T: your 1/4"-20 nut; M5_NUT_AF / M5_NUT_T.
- CS_FOOT_W / CS_FOOT_T: cold-shoe foot of your mic/light.
"""

from build123d import *

from cadlib import *

# Phone / accessory
PHONE_W = 76.7
PHONE_T = 8.25
CASE = 2.5
BUTTON_FREE_BOTTOM = 80.0      # info: jaws must sit below this
WIDTH_MIN, WIDTH_MAX = 74.0, 92.0
NUT14_AF, NUT14_T, SCREW14_D = 11.11, 5.6, 6.6
M5_NUT_AF, M5_NUT_T, M5_D = 8.0, 4.0, 5.4
CS_FOOT_W, CS_FOOT_T = 18.0, 2.0

# Clamp
JAW_GAP = 1.0
LIP_T, LIP_H = 3.0, 5.0
BLOCK_W, BLOCK_H = 30.0, 18.0
BLOCK_BACK = 17.0
COL_W, COL_D, COL_Y0 = 16.0, 10.0, 3.5
COL_FIT = 0.3
SLEEVE_H = 30.0
SLEEVE_FRONT = 3.2
SIDE_LOCK_T = 7.0
CS_W, CS_L, CS_H = 24.0, 20.0, 7.4
JAW_W = 20.0
LAYOUT_X = 60.0

PT = PHONE_T + 2 * CASE
JD = PT + JAW_GAP                         # jaw depth (front-back)
COL_TOP = BLOCK_H + WIDTH_MAX + SLEEVE_H
CAV_W = CS_FOOT_W + 0.6

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="auto",
    brim="on",                 # 140 mm tall column on a 30 x 35 mm block
)


def gable_x(length, width, wall) -> Part:
    """Cutter along X: `width` in Y, vertical `wall`, 45 deg roof; bottom at z = 0."""
    prof = Polygon((-width / 2, 0), (width / 2, 0), (width / 2, wall), (0, wall + width / 2), (-width / 2, wall), align=None)
    return extrude(Plane.YZ * prof, length / 2, both=True)


def base() -> Part:
    y0 = -(JD + LIP_T)
    block = Pos(0, (y0 + BLOCK_BACK) / 2, 0) * rounded_box(BLOCK_W, BLOCK_BACK - y0, BLOCK_H, radius=3)
    lip = Pos(0, y0 + LIP_T / 2, BLOCK_H - 1) * Box(BLOCK_W - 6, LIP_T, LIP_H + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    lip = fillet(lip.edges().group_by(Axis.Z)[-1], 1.0)
    col = Pos(0, COL_Y0 + COL_D / 2, BLOCK_H - 1) * Box(COL_W, COL_D, COL_TOP - BLOCK_H + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    col = chamfer(col.edges().filter_by(Axis.Z), 0.8)
    part = block + lip + col
    # 1/4"-20 nut: slot from the back, gable roof, 3 mm floor; screw hole from below
    yc = (y0 + BLOCK_BACK) / 2
    slot_w = NUT14_AF + 0.3
    slot = Pos(0, yc + 15, 3) * Rot(0, 0, 90) * gable_x(30, slot_w, NUT14_T + 0.4)
    part = part - slot - Pos(0, yc, -1) * Cylinder(SCREW14_D / 2, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return part


def slider() -> Part:
    iw, idp = COL_W + 2 * COL_FIT, COL_D + 2 * COL_FIT
    yi0 = COL_Y0 - COL_FIT
    yb = yi0 + idp + 3.0
    x0, x1 = -iw / 2 - 3.0, iw / 2 + SIDE_LOCK_T
    zb = -LIP_H
    sleeve = Pos((x0 + x1) / 2, yb / 2, zb) * Box(x1 - x0, yb, SLEEVE_H - zb, align=(Align.CENTER, Align.CENTER, Align.MIN))
    sleeve = fillet(sleeve.edges().filter_by(Axis.Z), 1.0)
    # cold-shoe block behind the sleeve
    shoe = Pos(0, yb + CS_L / 2 - 1, zb) * Box(CS_W, CS_L + 2, SLEEVE_H + CS_H - zb, align=(Align.CENTER, Align.CENTER, Align.MIN))
    shoe = fillet(shoe.edges().filter_by(Axis.Z), 2.0)
    # upper jaw: plate over the phone's top edge + lip down in front
    jaw = Pos(0, -(JD + LIP_T) / 2, zb) * Box(JAW_W, JD + LIP_T + 1, LIP_H + JD / 2 + 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
    jaw = fillet(jaw.edges().filter_by(Axis.Z), 1.0)
    part = sleeve + shoe + jaw
    # column bore
    part = part - Pos(0, yi0 + idp / 2, zb - 1) * Box(iw, idp, 200, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # phone pocket under the jaw plate (45 deg gable roof, contact on its two edges)
    part = part - Pos(0, -JD / 2, zb - 1) * gable_x(JAW_W + 2, JD, LIP_H + 1)
    # cold-shoe cavity: foot slides in from +Y, stop at the front
    h = CS_FOOT_T + 0.4
    prof = Polygon((-CAV_W / 2, 0), (CAV_W / 2, 0), (CAV_W / 2, h), (CAV_W / 2 - 3, h + 3), (CAV_W / 2 - 3, 10),
                   (-CAV_W / 2 + 3, 10), (-CAV_W / 2 + 3, h + 3), (-CAV_W / 2, h), align=None)
    cav = extrude(Plane.XZ * prof, CS_L + 5)       # Plane.XZ extrudes towards -Y
    part = part - Pos(0, yb + CS_L + 4, SLEEVE_H) * cav
    # M5 lock screw through the thick side wall, nut in a hex pocket on the outside
    zc = SLEEVE_H / 2
    yc = yi0 + idp / 2
    part = part - Pos(x1, yc, zc) * teardrop_hole(M5_D, 2 * (SIDE_LOCK_T + 1), along="X")
    hexr = (M5_NUT_AF + 0.3) / 3 ** 0.5
    nut = extrude(Plane.YZ * RegularPolygon(hexr, 6, major_radius=True), M5_NUT_T + 0.3)
    part = part - Pos(x1 - M5_NUT_T - 0.3, yc, zc) * Rot(30, 0, 0) * nut
    return Pos(LAYOUT_X, 0, -zb) * part


def build():
    return [base(), slider()]
