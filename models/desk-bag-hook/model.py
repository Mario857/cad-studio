"""desk-bag-hook: folding 5 kg bag hook screwed under a desk top.

Spec: a mount plate (50 x 66 x 6) is screwed to the underside of the desk near the edge with
2 wood screws. Two clevis ears hang below it and carry an M4 pivot pin (horizontal, along Y).
The hook arm hangs vertically below the pin in use (80 mm stem) and ends in a J hook that curls
sideways (in the Y-Z plane, opening 22 mm wide) so that, folded up 90 deg under the desk, the hook
lies flat: folded thickness = 6 plate + 10 pin drop + 10 below pin = 26 mm (<= 40).
Lock: the stem is offset 3 mm in -X from the pin axis, so the bag load always rotates the arm
bottom toward +X; a square shoulder on the arm knuckle (+X/top quadrant) then bears against the
plate underside (0.6 mm gap) -> the load drives the arm against the stop at 90 deg (vertical).
The arm folds the other way (bottom toward -X) up under the desk; the knuckle is rounded there.
Strength: 5 kg -> ~2-3 MPa bending in the hook (14 x 12 section), far below PLA-Tough/PETG limits.

Printing: 2 separate bodies (intended), printed in place, both parts flat on their common -X face (print_orientation ry=-90),
so the hook curve and stem lie in the layers (bending runs along layers) and the clevis ears
are loaded in-plane too. Gaps: 0.5 mm per side between knuckle and ears, 0.6 mm at the stop.

Hardware: 1x M4 x 40 socket/hex bolt (pin) + M4 nylock nut (tighten until arm holds by
friction when folded); 2x #8 / 4 mm x 20 pan-head wood screws into the desk underside.
Assumptions: desk top >= 18 mm thick wood/MDF with clear 66 x 50 mm area under the edge;
pin holes 4.3 (ears, snug) / 4.6 (arm, free turning), teardrop-shaped for printing.
"""

from build123d import *

from cadlib import *

META = dict(
    material="PLA-TOUGH",
    quality="strong",
    standing=False,
    loads=[dict(at=(-3.0, 18.0, 14.0), grams=5000)],   # bottom of hook bowl
    print_orientation=(0, -90, 0),   # -X (in use) face on the bed: hook bends along layers
    supports="auto",
    brim="auto",
)

# Parameters
PLATE_L = 50.0          # X
PLATE_W = 66.0          # Y
PLATE_T = 6.0
PLATE_X0 = -9.0         # plate -X face = common print bed plane
SCREW_D = 4.6
SCREW_X = 18.0
SCREW_Y = 25.0
PIN_DROP = 10.0         # plate underside -> pin axis
EAR_T = 8.0
EAR_X1 = 11.0
EAR_BELOW = 10.0        # ear extends below pin axis
SIDE_GAP = 0.5
STOP_GAP = 0.6
KNUCKLE_R = 9.0
ARM_W = 14.0            # Y width of stem / knuckle
ARM_T = 12.0            # X thickness of stem and hook
ARM_X0 = -9.0           # stem spans ARM_X0 .. ARM_X0+ARM_T (center -3 -> 3 mm lock offset)
STEM_L = 80.0           # pin axis -> top of hook bowl
HOOK_RI = 11.0
HOOK_RO = 25.0
LIP_H = 15.0
PIN_EAR_D = 4.3
PIN_ARM_D = 4.6

ZB = HOOK_RO                     # hook bowl centre height (part bottom at z=0)
ZP = ZB + STEM_L                 # pin axis
Z_PLATE = ZP + PIN_DROP          # plate underside
HOOK_YC = -ARM_W / 2 + HOOK_RO


def arm() -> Part:
    bar = HOOK_RO - HOOK_RI
    prof = Pos(0, (ZB + ZP) / 2) * Rectangle(ARM_W, ZP - ZB)
    prof += (Pos(HOOK_YC, ZB) * (Circle(HOOK_RO) - Circle(HOOK_RI))) & (
        Pos(HOOK_YC, ZB - HOOK_RO / 2) * Rectangle(2 * HOOK_RO, HOOK_RO))
    lip_y = HOOK_YC + (HOOK_RI + HOOK_RO) / 2
    prof += Pos(lip_y, ZB + LIP_H / 2) * Rectangle(bar, LIP_H)
    prof += Pos(lip_y, ZB + LIP_H) * Circle(bar / 2)
    body = extrude(Plane.YZ.offset(ARM_X0) * prof, ARM_T)

    # knuckle: square stop shoulder on +X/top, 45 deg chamfer on -X/top (fold side, support-free)
    stop_h = PIN_DROP - STOP_GAP
    r = KNUCKLE_R
    k = Polygon((-r, ZP - r), (r, ZP - r), (r, ZP + stop_h), (0, ZP + stop_h),
                (-r, ZP + stop_h - r), align=None)
    knuckle = extrude(Plane.XZ * k, ARM_W / 2, both=True)
    a = body + knuckle
    try:
        a = fillet(a.edges().filter_by(Axis.X), 1.5)
    except Exception:
        pass
    a -= Pos(0, 0, ZP) * Rot(0, 90, 0) * teardrop_hole(PIN_ARM_D, ARM_W + 2, along="Y")
    return a


def mount() -> Part:
    plate = Pos(PLATE_X0 + PLATE_L / 2, 0, Z_PLATE) * Box(
        PLATE_L, PLATE_W, PLATE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    y_in = ARM_W / 2 + SIDE_GAP
    ear_h = PIN_DROP + EAR_BELOW
    for s in (1, -1):
        plate += Pos((PLATE_X0 + EAR_X1) / 2, s * (y_in + EAR_T / 2), Z_PLATE - ear_h / 2) * Box(
            EAR_X1 - PLATE_X0, EAR_T, ear_h)
    plate -= Pos(0, 0, ZP) * Rot(0, 90, 0) * teardrop_hole(PIN_EAR_D, PLATE_W, along="Y")
    for s in (1, -1):
        plate -= Pos(SCREW_X, s * SCREW_Y, Z_PLATE + PLATE_T / 2) * Cylinder(SCREW_D / 2, PLATE_T + 2)
    return plate


def build():
    return [mount(), arm()]
