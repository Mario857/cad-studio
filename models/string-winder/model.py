"""string-winder: guitar string-winder crank with spinning knob and bridge-pin puller notch.

Spec:
- Cup with a stadium slot (nominal button SLOT_L x SLOT_W + SLOT_CLR per side) slips over the
  tuner button. Cup depth CUP_H clears neighbouring buttons so the arm runs above them.
- The cup mouth is the only face that can touch the headstock / tuner housing: its edges get
  MOUTH_FILLET (>= 1 mm) fillets and a FELT_DEPTH recess for a self-adhesive felt ring.
  Use FELT (or cork), NOT rubber: some rubbers/vinyls react with nitrocellulose finishes.
- Crank arm ARM_L from button axis to knob axis. Knob spins on a separate printed axle pin:
  pin collar (clearance fit in knob bore), head retains the knob, split snap end clicks through
  the arm hole and hooks under the arm. 3 parts, printed together.
- Bridge-pin puller notch in the tab behind the cup (keyhole, edges filleted).
- Print: flipped (arm top face on the bed, cup mouth up). The arm lies flat, so crank torque bends
  it in-plane, along the layers. Knob and pin are modelled in use orientation with their top at
  the arm top height, so the same flip puts all three on the bed.

Assumptions:
- Button roughly 22 x 8 mm (typical acoustic/electric tuner); SLOT_CLR 0.4 mm per side.
- Felt ring ~1.5 mm thick self-adhesive felt, cut to the recess (sits ~0.5 mm proud).
- Bridge pins: ~5 mm shaft under a ~7-8 mm head; notch 4.2 mm at the root, 6 mm at the entry.
- Material ABS+ (snap prongs need some flex); no hardware needed.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="Guitar Core ABS+ 0.20mm @BBL H2C",
    standing=False,
    loads=[],
    print_orientation=(180, 0, 0),  # arm top on bed: torque bends the arm along layers
    supports="auto",
    brim="auto",
)

# ---- Tuner cup ----
SLOT_L = 22.0          # nominal tuner button width
SLOT_W = 8.0           # nominal tuner button thickness
SLOT_CLR = 0.4         # clearance per side
SLOT_R = 2.0           # slot corner radius
CUP_R = 18.0           # cup outer radius
CUP_H = 16.0           # cup depth (button engagement + clear neighbouring buttons)
MOUTH_FILLET = 1.2     # fillet on guitar-touching mouth edges (>= 1 mm)
FELT_DEPTH = 1.0       # felt pad recess depth
FELT_RIM = 2.0         # plastic rim left inside/outside the felt recess

# ---- Arm ----
ARM_L = 75.0           # button axis -> knob axis
ARM_T = 6.0            # arm thickness
ARM_END_R = 10.0       # arm radius at knob end
ARM_EDGE_FILLET = 1.5  # underside edge fillet
BED_CHAMFER = 0.4      # elephant-foot chamfer on bed faces

# ---- Bridge pin puller tab ----
TAB_X = -27.0          # tab centre (behind the cup)
TAB_R = 8.0
NOTCH_ROOT = 4.2       # notch width at root (bridge pin shaft)
NOTCH_ENTRY = 6.0      # notch width at the tab edge
NOTCH_DEPTH = 9.0      # from tab tip inward
NOTCH_RELIEF = 5.0     # keyhole relief at the notch root
OUTLINE_FILLET = 2.0   # vertical corner rounds of the arm/tab/notch outline

# ---- Knob + axle pin ----
KNOB_D = 18.0
KNOB_L = 28.0
KNOB_CHAMFER = 1.0
COLLAR_D = 8.0                         # axle the knob spins on
KNOB_BORE = clearance(COLLAR_D, "loose")  # 8.8, free spin
AXIAL_PLAY = 0.6                       # knob end play between arm and pin head
HEAD_D = 14.0
HEAD_H = 2.5
PIN_D = 6.0                            # pin shank through the arm
PIN_HOLE = clearance(PIN_D, "snug")    # 6.3 arm hole
LIP_D = 7.1                            # snap lip, hooks under the arm
LIP_H = 1.2
LEAD_H = 1.6                           # lead-in cone height
LEAD_D = 5.0
SLIT_W = 1.6                           # split for snap prongs
SLIT_UP = 2.5                          # slit extends this far into the collar
SHANK_PLAY = 0.2                       # axial slack shank vs arm thickness

TOP_Z = CUP_H + ARM_T                  # arm top (bed after flip)


def _crank() -> Part:
    # cup
    cup = Cylinder(CUP_R, CUP_H, align=ON_BED)
    slot_l, slot_w = SLOT_L + 2 * SLOT_CLR, SLOT_W + 2 * SLOT_CLR
    slot_cut = extrude(Plane.XY * RectangleRounded(slot_l, slot_w, SLOT_R), CUP_H)
    cup = cup - slot_cut
    cup = fillet(cup.edges().group_by(Axis.Z)[0], MOUTH_FILLET)
    felt = (Circle(CUP_R - FELT_RIM)
            - RectangleRounded(slot_l + 2 * FELT_RIM, slot_w + 2 * FELT_RIM, SLOT_R + FELT_RIM))
    cup = cup - extrude(Plane.XY * felt, FELT_DEPTH)

    # arm outline: cup disc + bar + knob-end disc + puller tab
    outline = (Circle(CUP_R + 2)
               + Pos(ARM_L / 2, 0) * Rectangle(ARM_L, 2 * ARM_END_R)
               + Pos(ARM_L, 0) * Circle(ARM_END_R)
               + Pos((TAB_X - TAB_R) / 2, 0) * Rectangle(abs(TAB_X - TAB_R), 2 * TAB_R))
    tip = TAB_X - TAB_R
    xr = tip + NOTCH_DEPTH - NOTCH_ROOT / 2
    slope = (NOTCH_ENTRY - NOTCH_ROOT) / 2 / (xr - tip)
    xo = tip - 3
    notch = Polygon((xo, NOTCH_ENTRY / 2 + 3 * slope), (xr, NOTCH_ROOT / 2),
                    (xr, -NOTCH_ROOT / 2), (xo, -NOTCH_ENTRY / 2 - 3 * slope), align=None)
    notch += Pos(xr, 0) * Circle(NOTCH_RELIEF / 2)
    outline = fillet((outline - notch).vertices(), OUTLINE_FILLET)
    arm = extrude(Plane.XY.offset(CUP_H) * outline, ARM_T)
    arm = chamfer(arm.edges().group_by(Axis.Z)[-1], BED_CHAMFER)
    arm = fillet(arm.edges().group_by(Axis.Z)[0], ARM_EDGE_FILLET)

    crank = arm + cup - slot_cut  # keep slot clear
    crank = crank - Pos(ARM_L, 0, TOP_Z) * Cylinder(PIN_HOLE / 2, ARM_T + 1,
                                                    align=(Align.CENTER, Align.CENTER, Align.MAX))
    return crank


def _knob(x, y) -> Part:
    k = Cylinder(KNOB_D / 2, KNOB_L, align=ON_BED)
    k = chamfer(k.edges(), KNOB_CHAMFER)
    k = k - Cylinder(KNOB_BORE / 2, KNOB_L, align=ON_BED)
    # in use the knob top sits AXIAL_PLAY below the pin head; align its top with the arm top
    return Pos(x, y, TOP_Z - KNOB_L) * k


def _pin(x, y) -> Part:
    # built with z=0 at the arm top face (in use), head up
    head = Pos(0, 0, KNOB_L + AXIAL_PLAY) * Cylinder(HEAD_D / 2, HEAD_H, align=ON_BED)
    head = chamfer(head.edges(), 0.6)
    collar = Cylinder(COLLAR_D / 2, KNOB_L + AXIAL_PLAY, align=ON_BED)
    shank_l = ARM_T + SHANK_PLAY
    shank = Pos(0, 0, -shank_l) * Cylinder(PIN_D / 2, shank_l, align=ON_BED)
    lip = Pos(0, 0, -shank_l - LIP_H) * Cylinder(LIP_D / 2, LIP_H, align=ON_BED)
    lead = Pos(0, 0, -shank_l - LIP_H - LEAD_H) * Cone(LEAD_D / 2, LIP_D / 2, LEAD_H, align=ON_BED)
    pin = head + collar + shank + lip + lead
    bottom = -shank_l - LIP_H - LEAD_H
    slit_h = -bottom + SLIT_UP
    pin = pin - Pos(0, 0, bottom - 0.1) * Box(LIP_D + 2, SLIT_W, slit_h + 0.1, align=ON_BED)
    top = KNOB_L + AXIAL_PLAY + HEAD_H
    return Pos(x, y, TOP_Z - top) * pin


def build():
    return [_crank(), _knob(20, 34), _pin(48, 34)]
