"""fridge-door-bin: clip-on bin that hangs inside an existing fridge door shelf.

Spec: 150 x 45 x 62 mm open-top bin (2 mm walls) whose back wall rests against the inner
face of a door shelf's front wall; a full-length hook (2.5 mm bridge + 12 mm outer lip)
clips over the top of that wall (4.5 mm slot). Gives an extra compartment for sauce
sachets, tubes, small jars. One end is cut at 45 deg in plan (front edge 105 mm) so it prints standing on its
square end with zero supports (the slanted end is the "roof").
Assumptions: door-shelf front wall <= 4.5 mm thick and >= 65 mm tall; contents <= 400 g.
ABS is not food-safe: keep food in its own packaging.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[dict(at=(70, -22, -30), grams=400)],
    print_orientation=(0, -90, 0),
    supports="auto",
    brim="auto",
)

# Parameters
LENGTH = 150.0         # X along the back
DEPTH = 45.0           # Y into the shelf
HEIGHT = 62.0          # Z below the rim
WALL = 2.0
SLOT = 4.5             # door-shelf wall thickness + clearance
BRIDGE_T = 2.5
LIP_T = 2.5
LIP_L = 12.0


def _cut45(offset: float = 0.0) -> Part:
    """Half-space removing x > LENGTH - offset*sqrt2 + y (45 deg end in plan view)."""
    big = Box(400, 400, 400, align=(Align.MIN, Align.CENTER, Align.CENTER))
    return Pos(LENGTH - offset * 1.4142, 0, 0) * Rot(0, 0, -45) * big


def build() -> Part:
    top = BRIDGE_T
    outer = Pos(0, -DEPTH, -HEIGHT) * Box(LENGTH, DEPTH, HEIGHT + top, align=(Align.MIN,) * 3)
    inner = Pos(WALL, -DEPTH + WALL, -HEIGHT + WALL) * Box(LENGTH, DEPTH - 2 * WALL, HEIGHT + top,
                                                         align=(Align.MIN,) * 3)
    hook = Pos(0, 0, 0) * Box(LENGTH, SLOT + LIP_T, BRIDGE_T, align=(Align.MIN,) * 3)
    hook += Pos(0, SLOT, top - LIP_L) * Box(LENGTH, LIP_T, LIP_L, align=(Align.MIN,) * 3)
    part = (outer + hook) - _cut45()
    part -= inner - _cut45(WALL)
    part = chamfer(part.edges().group_by(Axis.X)[0], 0.4)  # bed face when printed
    return part
