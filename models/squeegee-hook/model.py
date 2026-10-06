"""squeegee-hook: wall hook / U-cradle for a shower squeegee.

Spec: the squeegee hangs handle-down - the handle drops into an open-front,
open-bottom U-cradle (slot = HANDLE_W + CLEARANCE) and the blade rests across the two arms.
Wall plate with two M4 countersunk screw holes (reachable straight through the open U) and a
completely flat back so a double-sided adhesive pad can be used instead of screws.

Drainage: nothing can hold water.
- The cradle has no floor (open bottom) and an open front - drips fall straight through.
- Arm tops slope ARM_TOP_SLOPE deg inward, shedding water into the open slot.
- Arm undersides: flat foot on the bed then a 45 deg gusset (no flat ceilings, no supports).
- The plate top is a 45 deg roof sloping away from the wall.

Print orientation: printed in the in-use orientation (flat back vertical, plate standing on its
bottom edge). The arms are cantilevers loaded in -Z; their bending stress runs along Y, which then
lies inside the layers, so layer lines are not peeled apart (printing back-down would put the
arms vertical and load them across layer bonds). The 45 deg gusset undersides make this
orientation support-free; the ARM_FOOT pads widen the bed contact so the part cannot tip. Screw holes become horizontal (small, 45 deg csk cone - prints fine).

Assumptions: squeegee ~400 g; handle <= 25 mm wide (any thickness, front is open);
blade wider than ~60 mm so it rests on the arms. Hardware: 2x M4 (or #8) countersunk wood
screws ~30 mm + wall plugs, or a 50x60 mm double-sided waterproof adhesive pad.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[dict(at=(0, 6 + 17.5, 38), grams=400)],
    print_orientation=(0, 0, 0),  # in-use: arm bending stress runs along layers
    supports="off",
    brim="auto",
)

# Parameters
HANDLE_W = 25.0          # squeegee handle width
CLEARANCE = 4.0          # total clearance across the slot
SLOT_W = HANDLE_W + CLEARANCE
ARM_W = 10.0             # width of each cradle arm (X)
ARM_L = 35.0             # arm projection from plate front (Y)
ARM_FOOT = 15.0          # flat arm underside on the bed (Y) - keeps the print stable
ARM_TOP_Z = 38.0         # outer top edge height of arms
ARM_TOP_SLOPE = 15.0     # deg, arm top falls toward the slot
TIP_R = 3.0
PLATE_W = SLOT_W + 2 * ARM_W
PLATE_H = 75.0
PLATE_T = 6.0
SCREW = "M4"
SCREW_Z = (12.0, 62.0)   # screw hole heights at x=0 (lower one reached through the open U)
EDGE_R = 2.0


def _extrude_x(profile, width):
    """Extrude a YZ profile along +X from x=0 to x=width."""
    s = extrude(Plane.YZ * profile, width)
    return Pos(-s.bounding_box().min.X, 0, 0) * s


def build() -> Part:
    # wall plate: YZ profile with 45 deg roof falling away from the wall
    plate_prof = Polygon((0, 0), (PLATE_T, 0), (PLATE_T, PLATE_H - PLATE_T), (0, PLATE_H), align=None)
    plate = Pos(-PLATE_W / 2, 0, 0) * _extrude_x(plate_prof, PLATE_W)
    plate = fillet(plate.edges().filter_by(Axis.Z), EDGE_R)

    # cradle arms: flat foot on the bed, then 45 deg gusset underside up to the tip
    tip_z = ARM_L - ARM_FOOT
    arm_prof = Polygon(
        (PLATE_T - 1, 0),
        (PLATE_T - 1, ARM_TOP_Z),
        (PLATE_T + ARM_L, ARM_TOP_Z),
        (PLATE_T + ARM_L, tip_z),
        (PLATE_T + ARM_FOOT, 0),
        align=None,
    )
    arm = _extrude_x(arm_prof, ARM_W)
    arm = fillet(arm.edges().filter_by(Axis.Z).group_by(Axis.Y)[-1], TIP_R)
    right = Pos(SLOT_W / 2, 0, 0) * arm
    left = Pos(-SLOT_W / 2 - ARM_W, 0, 0) * arm
    part = plate + right + left

    # slope arm tops toward the slot (drain)
    for s in (1, -1):
        cutter = Box(ARM_W * 3, ARM_L + 10, 40, align=(Align.CENTER, Align.MIN, Align.MIN))
        cutter = Rot(0, -s * ARM_TOP_SLOPE, 0) * cutter
        cutter = Pos(s * (SLOT_W / 2 + ARM_W), PLATE_T, ARM_TOP_Z) * cutter
        part = part - cutter

    # countersunk screw holes from the front face (x=0, in the slot)
    for z in SCREW_Z:
        part = part - Pos(0, PLATE_T, z) * Rot(-90, 0, 0) * bolt_hole(SCREW, PLATE_T + 1, head="csk")

    # elephant-foot chamfer on the bed edges
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    return part
