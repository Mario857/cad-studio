"""{{NAME}}: graded-size fit gauge for one feature (scaffold from `./cad coupon`).

Feature under test: {{FEATURE}}
Prints COUNT test blocks, size = NOMINAL + (i - (COUNT-1)/2) * STEP, numbered 1..COUNT. Print once, find the
number that fits, then put that size into the real model (via hole_d()/clearance() if it is a general rule).
Sizes are the modelled diameters (no extra compensation added): that is what the gauge measures.
TODO (agent): replace test_cutter() with the real mating feature (slot, nut trap, snap, ...), keep the
gauge small (<= ~10 g, <= 15 min) and list the number -> size table in this docstring.
Assumptions: none yet.
"""

from build123d import *

from cadlib import *

META = dict(
    material="PLA",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="off",
)

NOMINAL = 6.0     # centre size of the sweep (mm)
STEP = 0.1        # size increment between blocks (mm)
COUNT = 6         # number of test blocks
BLOCK_W = 16.0
BLOCK_H = 6.0
DEPTH = 4.5       # test cut depth from the top face
PITCH = 18.0
STRIP_T = 1.2
STRIP_W = 22.0
NUM_SIZE = 7.0
NUM_H = 0.6


def sizes():
    return [round(NOMINAL + (i - (COUNT - 1) / 2) * STEP, 3) for i in range(COUNT)]


def test_cutter(size):
    """Cutter for one block, pointing down from z=0. TODO: replace with the real feature."""
    return Pos(0, 0, -DEPTH) * Cylinder(size / 2, DEPTH, align=ON_BED)


def block(size):
    b = Box(BLOCK_W, BLOCK_W, BLOCK_H, align=ON_BED)
    b = chamfer(b.edges().group_by(Axis.Z)[0], 0.4)
    return b - Pos(0, 0, BLOCK_H) * test_cutter(size)


def build() -> Part:
    part = Pos((COUNT - 1) * PITCH / 2, -3.0, 0) * Box(COUNT * PITCH, STRIP_W, STRIP_T, align=ON_BED)
    for i, size in enumerate(sizes()):
        x = i * PITCH
        part += Pos(x, 0, 0) * block(size)
        t = label(str(i + 1), size=NUM_SIZE, depth=NUM_H)
        bb = t.bounding_box()
        part += Pos(x - (bb.min.X + bb.max.X) / 2, -BLOCK_W / 2 - 3.0 - (bb.min.Y + bb.max.Y) / 2, STRIP_T) * t
    return part
