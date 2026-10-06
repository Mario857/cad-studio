"""trash-bag-holder: over-the-cabinet-door bag holder (pair of clips) for 16-20 mm doors.

Spec: two identical 12 mm thick clips (copies=2). Each hooks over the door top; a flexing
back lip (16 mm gap at the tip, opens to 20 mm) grips doors 16-20 mm thick. A stem runs
90 mm down the door face and ends in a 120 mm forward arm with an upturned tip and a gusset.
Hang the clips ~25 cm apart and stretch the bag rim (or tie handles) over both arms; the
bag opens between the arms and the door.
Printed lying on its side so hook, arm and lip all bend in-plane with the layers.
Assumptions: door top is exposed (>= 4 mm gap to the cabinet frame when closed, or used on
an inside door); full bag <= 2 kg (1 kg per clip at the arm).
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[dict(at=(0, 70, -84), grams=1000)],
    print_orientation=(0, 90, 0),
    supports="auto",
    brim="auto",
    copies=2,
)

# Parameters
CLIP_W = 12.0          # X thickness of the clip
DOOR_MAX = 20.5        # gap at the lip root
DOOR_MIN = 16.0        # gap at the lip tip (flexes open)
BRIDGE_T = 3.5
STEM_T = 4.5
STEM_DROP = 90.0
LIP_T = 3.0
LIP_L = 30.0
ARM_L = 120.0
ARM_T = 12.0           # arm depth (Z)
TIP_H = 24.0           # upturned tip height above the arm
TIP_T = 8.0
GUSSET = 36.0


def build() -> Part:
    yb = -DOOR_MAX - LIP_T  # back of the lip root
    pts = [
        (yb, BRIDGE_T),                      # top-back
        (STEM_T, BRIDGE_T),                  # top-front
        (STEM_T, -STEM_DROP + ARM_T + GUSSET),
        (STEM_T + GUSSET, -STEM_DROP + ARM_T),
        (ARM_L - TIP_T, -STEM_DROP + ARM_T),
        (ARM_L - TIP_T, -STEM_DROP + ARM_T + TIP_H),
        (ARM_L, -STEM_DROP + ARM_T + TIP_H),
        (ARM_L, -STEM_DROP),
        (0, -STEM_DROP),                     # stem bottom-back (door side)
        (0, 0),                              # door front-top corner
        (-DOOR_MAX, 0),                      # under the bridge
        (-DOOR_MIN, -LIP_L),                 # lip tip (inner)
        (-DOOR_MIN - LIP_T, -LIP_L),         # lip tip (outer)
    ]
    prof = Polygon(*pts, align=None)
    part = extrude(Plane.YZ * prof, CLIP_W)
    part = Pos(-CLIP_W / 2, 0, 0) * part
    # round the outer corners of the bridge, tip and arm end
    part = fillet(part.edges().filter_by(Axis.X).filter_by_position(Axis.Y, ARM_L - 0.1, ARM_L + 0.1), 3.0)
    part = chamfer(part.edges().group_by(Axis.X)[-1], 0.4)  # bed side when printed
    return part
