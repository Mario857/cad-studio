"""wall-hook: screw-mounted wall hook for coats/bags, two M4 countersunk wood screws.

Spec: 24 mm wide, 70 mm back plate, 45 mm reach, 18 mm tall lip. Holds ~5 kg.
Assumptions: wall is the y=0 plane, hook points -Y; printed on its side so the bending load runs
along the layers (not across them).
"""

from build123d import *

from cadlib import *

META = dict(
    material="PETG",
    quality="strong",
    standing=False,
    loads=[],
    print_orientation=(0, 90, 0),  # +X face on the bed; model -X is up while printing
    supports="auto",
    brim="auto",
)

WIDTH = 24.0
PLATE_HEIGHT = 70.0
PLATE_THICKNESS = 5.0
REACH = 45.0
ARM_THICKNESS = 7.0
LIP_HEIGHT = 18.0
LIP_THICKNESS = 5.0
INNER_RADIUS = 5.0
EDGE_RADIUS = 1.5
SCREW = "M4"
SCREW_Z = (32.0, 60.0)


def build() -> Part:
    plate = Box(WIDTH, PLATE_THICKNESS, PLATE_HEIGHT, align=(Align.CENTER, Align.MAX, Align.MIN))
    arm = Box(WIDTH, REACH, ARM_THICKNESS, align=(Align.CENTER, Align.MAX, Align.MIN))
    lip = Pos(0, -REACH, 0) * Box(WIDTH, LIP_THICKNESS, LIP_HEIGHT, align=(Align.CENTER, Align.MIN, Align.MIN))
    hook = plate + arm + lip

    along_x = hook.edges().filter_by(Axis.X)
    inner = [e for e in along_x if abs(e.center().Z - ARM_THICKNESS) < 0.01 and -REACH < e.center().Y < -PLATE_THICKNESS + 0.01]
    hook = fillet(inner, INNER_RADIUS)
    hook = fillet(hook.edges().filter_by(Axis.X).group_by(Axis.Z)[-1], EDGE_RADIUS)

    for z in SCREW_Z:
        hook -= Pos(0, -PLATE_THICKNESS, z) * Rot(90, 0, 0) * bolt_hole(SCREW, PLATE_THICKNESS + 1, head="csk")
        hook -= Pos(0, -PLATE_THICKNESS / 2, z) * teardrop_hole(METRIC[SCREW]["clear"], PLATE_THICKNESS + 2, along="Y", tip="-X")
    return hook
