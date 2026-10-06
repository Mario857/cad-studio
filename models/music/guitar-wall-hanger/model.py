"""guitar-wall-hanger: wall-mounted yoke that hangs a guitar by its headstock.

Spec: a vertical wall plate (3 countersunk wall screws) with a cantilever arm that ends in a
two-prong yoke. The neck passes between the prongs; the underside of the headstock (nut side)
rests on the prong tops. The arm is angled ARM_ANGLE (10 deg) up and the prongs end in a raised
lip, so the headstock cannot slide off the front. Two triangular gussets brace the arm.
Design load 5 kg (guitar ~4 kg + margin) at the yoke.

Guitar contact: every yoke edge is filleted (>= 1 mm, FILLET) and each prong top has a
FELT_DEPTH recess for a self-adhesive pad. Use FELT (or cork) pads, NOT rubber/vinyl/foam:
some rubbers and plasticisers react with nitrocellulose finishes and leave permanent marks.

Print: on its side (model X up), so the arm bending stress and the plate bending both run
along layers, not across them. The upper prong overhangs the yoke slot in that orientation,
so that prong underside needs (easy-to-remove) supports — accepted for strength.
The gusset is a full-width wedge under the solid stem (no overhang when printed on its side).

Assumptions:
- YOKE_GAP 46 mm clears Fender (42 mm) and Gibson (43 mm) nut widths; range 40-50 mm.
- Wall screws: 3x countersunk 4 mm wood screws (#8) >= 40 mm into stud/plug; modelled as M4 csk.
- Felt pads: 1.5 mm self-adhesive felt, cut to FELT_W x FELT_L.
- Arm length puts the neck ~90 mm off the wall so the body clears it.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="Guitar Core ABS+ 0.20mm @BBL H2C",
    standing=False,
    loads=[dict(at=(0.0, 68.0, 88.0), grams=5000)],
    print_orientation=(0, 90, 0),  # model X up: arm + plate bending stress along layers
    supports="auto",           # WARN accepted: upper prong underside (~11 cm2) needs tree supports on its side
    brim="auto",
)

# Parameters — wall plate (wall at y=0, plate front at y=PLATE_T)
PLATE_W = 80.0
PLATE_H = 130.0
PLATE_T = 8.0
PLATE_R = 6.0              # plate corner radius
SCREW = "M4"               # proxy for #8 / 4 mm countersunk wood screw
SCREW_TOP_Z = 112.0
SCREW_TOP_DX = 26.0        # +/- X of the two top screws
SCREW_BOT_Z = 18.0

# Arm / yoke
ARM_ANGLE = 10.0           # deg up from horizontal
ARM_Z = 62.0               # arm underside height at the plate
ARM_H = 18.0               # arm thickness (vertical)
STEM_L = 30.0              # solid arm before the slot
PRONG_L = 55.0             # prong length (headstock rest)
PRONG_W = 17.0             # width of each prong (YOKE_W = PLATE_W: flat on bed)
YOKE_GAP = 46.0            # neck slot width, 40-50 for Fender/Gibson
LIP_H = 9.0                # raised stop at the prong tips
LIP_L = 8.0
FILLET = 1.2               # guitar-contact fillets (>= 1 mm)
FILLET_V = 3.0             # vertical yoke edges

# Felt pad recesses on prong tops
FELT_DEPTH = 1.5
FELT_W = PRONG_W - 4.0
FELT_L = PRONG_L - LIP_L - 6.0

# Gussets
GUSSET_L = STEM_L - 8.0    # full-width wedge under the stem, stops short of the neck slot
GUSSET_H = 48.0            # down the plate

YOKE_W = YOKE_GAP + 2 * PRONG_W
ARM_L = STEM_L + PRONG_L


def _arm() -> Part:
    """Arm in local coords: root at y=0, underside z=0, pointing +Y, horizontal."""
    bury = PLATE_T / 2  # extends into the plate for a solid union
    prof = Polygon(
        (-bury, 0), (ARM_L, 0), (ARM_L, ARM_H + LIP_H), (ARM_L - LIP_L, ARM_H + LIP_H),
        (ARM_L - LIP_L, ARM_H), (-bury, ARM_H), align=None)
    arm = extrude(Plane.YZ * prof, YOKE_W / 2, both=True)
    arm = arm - Pos(0, STEM_L + PRONG_L / 2 + 1, -1) * Box(
        YOKE_GAP, PRONG_L + 2, ARM_H + LIP_H + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    px = YOKE_GAP / 2 + PRONG_W / 2
    # two passes with different radii (equal radii give a non-watertight mesh)
    arm = fillet(arm.edges().filter_by(Axis.Z), FILLET_V)
    arm = fillet(arm.edges().filter_by(
        lambda e: e.center().Y > 1 and abs(e.tangent_at(0.5).Z) < 0.99), FILLET)
    for sx in (-1, 1):
        pad = Pos(sx * px, ARM_L - LIP_L - 3 - FELT_L / 2, ARM_H) * extrude(
            RectangleRounded(FELT_W, FELT_L, 2), -FELT_DEPTH)
        arm = arm - pad
    return arm


def build() -> Part:
    plate = Pos(0, PLATE_T / 2, 0) * Box(PLATE_W, PLATE_T, PLATE_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    plate = fillet(plate.edges().filter_by(Axis.Y), PLATE_R)
    plate = chamfer(plate.edges().group_by(Axis.Y)[-1], 0.8)

    arm = Pos(0, PLATE_T, ARM_Z) * Rot(ARM_ANGLE, 0, 0) * _arm()

    tan = math.tan(math.radians(ARM_ANGLE))
    tri = Polygon(
        (PLATE_T - 1, ARM_Z + 1),
        (PLATE_T + GUSSET_L, ARM_Z + GUSSET_L * tan + 1),
        (PLATE_T - 1, ARM_Z - GUSSET_H),
        align=None,
    )
    part = plate + arm
    part = part + extrude(Plane.YZ * tri, YOKE_W / 2, both=True)

    for x, z in ((-SCREW_TOP_DX, SCREW_TOP_Z), (SCREW_TOP_DX, SCREW_TOP_Z), (0, SCREW_BOT_Z)):
        part = part - Pos(x, PLATE_T, z) * Rot(-90, 0, 0) * bolt_hole(SCREW, PLATE_T + 2, head="csk")
    return part
