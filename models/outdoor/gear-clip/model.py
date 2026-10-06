"""gear-clip: 60 mm accessory carabiner with an inward-opening flex gate. Set of 4.

NOT FOR CLIMBING, ROPE WORK, FALL PROTECTION OR ANY LIFE-SAFETY LOAD. Accessory use only: hang a mug,
gloves, keys or a small bag on a pack (rated working load 3 kg, static).

Spec: stadium body 60 x 32 mm, 7 mm thick, 6 mm wide spine/ends. A 1.4 mm flex gate grows from the
bottom of the open side; its tip sits in a pocket behind a 2.4 mm nose lip, so the gate only opens
inward (push it in to clip on) and an outward pull on the gate is stopped by the lip.
Strength: printed flat (profile in XY), so the in-plane hanging load runs along the layers, never
across them. Worst case 3 kg hanging 15 mm off the spine: M = 0.44 N.m on a 6 x 7 mm spine ->
~10.5 MPa bending, ~3.5x below ABS+ tensile strength. Gate strain at a 6 mm opening ~2.0 %.
Hardware: none.
Assumptions: load applied in the clip plane (normal hanging use); gate is not load-bearing.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # flat: load + gate flex in the layer plane
    supports="off",
    brim="auto",
    copies=4,
)

LENGTH = 60.0
WIDTH = 32.0
THICK = 7.0
WALL = 6.0               # spine + ends (structural)
GATE_W = 1.4             # flex gate width (in-plane)
GATE_X = 12.0            # inner face of the gate (x)
GAP_BOTTOM = -10.0       # opening spans y = GAP_BOTTOM .. GAP_TOP on the +X side
GAP_TOP = 12.0
GATE_TIP_CLEAR = 0.4     # gate tip to pocket roof
LIP_CLEAR = 0.3          # gate to nose lip
POCKET_DEPTH = 3.6       # gate tip engagement behind the lip
EDGE_R = 1.0


def build() -> Part:
    outer = Rot(0, 0, 90) * SlotOverall(LENGTH, WIDTH)
    inner = Rot(0, 0, 90) * SlotOverall(LENGTH - 2 * WALL, WIDTH - 2 * WALL)
    x_in, x_out = WIDTH / 2 - WALL, WIDTH / 2
    lip_x = GATE_X + GATE_W + LIP_CLEAR
    tip_y = GAP_TOP + POCKET_DEPTH
    sk = outer - inner
    sk -= Pos((x_in + x_out + 1) / 2, (GAP_BOTTOM + GAP_TOP) / 2) * Rectangle(WALL + 1, GAP_TOP - GAP_BOTTOM)
    # pocket behind the nose lip for the gate tip
    sk -= Pos((x_in - 0.5 + lip_x) / 2, (GAP_TOP - 0.1 + tip_y + GATE_TIP_CLEAR) / 2) * Rectangle(
        lip_x - x_in + 0.5, tip_y + GATE_TIP_CLEAR - GAP_TOP + 0.1)
    # gate: rooted in the bottom end, free tip in the pocket
    sk += Pos(GATE_X + GATE_W / 2, (GAP_BOTTOM - 1 + tip_y) / 2) * Rectangle(GATE_W, tip_y - GAP_BOTTOM + 1)
    part = extrude(sk, THICK)
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    return part
