"""door-wedge: door stop wedge with V-groove grip underside and a hang hole.

Spec: 120 mm long, 40 mm wide, rises from a 1.5 mm tip to 25 mm at the tall end. The underside has
shallow V-grooves running across the width (grip on floors). A 8 mm hole through the tall end
(along the width) hangs it on a hook.
Print: lying on its SIDE (triangle profile on the bed, Y axis = print Z). The grooves and the hang
hole are then pure extrusions of the 2D profile: no overhangs, no supports, no ridges on the bed.
Material: TPU would give the best grip, but the only TPU preset (Bambu TPU 95A HF @BBL H2C) is for the
0.6 mm nozzle and the slice FAILs on the 0.4 mm H2C, so META uses PETG (the V-grooves still add grip).
Switch META material to TPU once a 0.4 mm TPU preset exists.
Assumptions: floor contact is the grooved underside; wedge compressed along its sloped top, so
the layers (stacked across the width) run parallel to the load direction.
"""

from build123d import *

from cadlib import *

META = dict(
    material="PETG",           # TPU preferred for grip, but its H2C preset is 0.6-nozzle-only -> slice FAIL; PETG used
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(90, 0, 0),  # on its side: Y axis becomes print Z
    supports="off",
    brim="auto",
)

# Parameters
LENGTH = 120.0       # X, tip to tall end
WIDTH = 40.0         # Y
HEIGHT = 25.0        # tall end height
TIP = 1.5            # tip thickness
GROOVE_PITCH = 4.0
GROOVE_DEPTH = 1.0
GROOVE_START = 8.0   # grooves span x = start .. LENGTH - end margin
GROOVE_END = 28.0    # leave the hole zone flat
HOLE_D = 8.0
HOLE_X = LENGTH - 10.0
HOLE_Z = HEIGHT / 2
EDGE_CH = 0.4


def build() -> Part:
    pts = [(0, 0)]
    n = int((LENGTH - GROOVE_END - GROOVE_START) // GROOVE_PITCH)
    for i in range(n):
        x = GROOVE_START + i * GROOVE_PITCH
        pts += [(x, 0), (x + GROOVE_PITCH / 2, GROOVE_DEPTH), (x + GROOVE_PITCH, 0)]
    pts += [(LENGTH, 0), (LENGTH, HEIGHT), (0, TIP)]
    prof = Polygon(*pts, align=None)
    part = extrude(Plane.XZ * prof, WIDTH / 2, both=True)
    # hang hole along Y
    hole = Pos(HOLE_X, 0, HOLE_Z) * Rot(90, 0, 0) * Cylinder(HOLE_D / 2, WIDTH + 2)
    part = part - hole
    # bed-edge chamfer on both side faces (either can be the bed face)
    side_edges = part.edges().filter_by(lambda e: abs(e.center().Y) > WIDTH / 2 - 0.01)
    part = chamfer(side_edges, EDGE_CH)
    return part
