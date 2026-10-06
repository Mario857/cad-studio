"""hair-dryer-holder: wall-mounted ring holder for a hair dryer (ring ID 60 mm).

Spec: dryer is dropped nozzle-first through a 60 mm ring and hangs by its body/handle.
Ring (6 mm wall, 20 mm tall) is fused to the back plate by a full-width arm; two 45 deg
gussets on top tie the arm into the plate. Ring, arm and plate all start at z=0, so it
prints as modeled with no supports, and the ring/arm bending under the dryer weight
runs along the layers. 2 x 4.5 mm teardrop screw holes (pan-head 4 mm screws + plugs).
Assumptions: nozzle/concentrator < 58 mm OD, body > 64 mm; dryer <= 800 g;
ring centre 46 mm from the wall.
"""

from build123d import *

from cadlib import *

# Parameters
RING_ID = 60.0
RING_WALL = 6.0
RING_H = 20.0
WALL_GAP = 6.0           # wall to ring OD
PLATE_W = 90.0
PLATE_H = 110.0
PLATE_T = 5.0
GUSSET_H = 45.0
GUSSET_T = 6.0
GUSSET_X = 30.0
SCREW_D = 4.5
SCREW_Z = (60.0, 95.0)
DRYER_G = 800

RING_OD = RING_ID + 2 * RING_WALL
RING_Y = PLATE_T + WALL_GAP + RING_OD / 2

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[dict(at=(0, RING_Y, RING_H), grams=DRYER_G)],
    print_orientation="auto",
    supports="auto",
    brim="on",                # ABS: 110 mm tall thin plate on a small footprint
)


def build() -> Part:
    plate = Pos(0, PLATE_T / 2, 0) * Box(PLATE_W, PLATE_T, PLATE_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    arm = Pos(0, RING_Y / 2, 0) * Box(RING_OD, RING_Y, RING_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    ring = Pos(0, RING_Y, 0) * Cylinder(RING_OD / 2, RING_H, align=ON_BED)
    part = plate + arm + ring
    for x in (-GUSSET_X, GUSSET_X):
        g = Polygon((PLATE_T - 0.5, RING_H - 0.5), (RING_Y - RING_ID / 2, RING_H - 0.5),
                    (PLATE_T - 0.5, RING_H + GUSSET_H), align=None)
        part += Pos(x, 0, 0) * extrude(Plane.YZ * g, GUSSET_T / 2, both=True)
    part -= Pos(0, RING_Y, -1) * Cylinder(RING_ID / 2, RING_H + 2, align=ON_BED)
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    for z in SCREW_Z:
        part -= Pos(0, PLATE_T / 2, z) * teardrop_hole(SCREW_D, PLATE_T + 2, along="Y")
    return part
