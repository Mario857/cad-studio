"""herb-stripper: flat herb/kale stripper with 5 graduated holes.

Spec: 150 x 50 x 4 mm rounded plate with holes of 3, 5, 7, 10 and 14 mm (thyme/rosemary
to kale/chard stems). Pull the stem through from the chamfered side and the leaves are
stripped off. 8 mm hang hole at the end; hole sizes engraved 0.6 mm deep, 5 mm tall.
Assumptions: thickness 4 mm gives a stiff plate and a sharp-enough stripping edge.
ABS is not food-safe: leaves only touch it briefly - rinse herbs after stripping, or print
in a food-safe material (e.g. PETG) for regular use.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation="auto",
    supports="auto",
    brim="auto",
)

# Parameters
LENGTH = 150.0
WIDTH = 50.0
THICK = 4.0
CORNER_R = 12.0
HOLES = (3.0, 5.0, 7.0, 10.0, 14.0)
HOLE_PITCH = 24.0
HOLE_Y = 6.0           # holes above the centreline, labels below
ENTRY_CHAMFER = 1.0
HANG_D = 8.0
LABEL_SIZE = 5.5
LABEL_DEPTH = 0.6


def build() -> Part:
    part = rounded_box(LENGTH, WIDTH, THICK, radius=CORNER_R)
    part = fillet(part.edges().group_by(Axis.Z)[-1], 1.0)
    x0 = -LENGTH / 2 + 22
    for i, d in enumerate(HOLES):
        x = x0 + i * HOLE_PITCH
        hole = Pos(x, HOLE_Y, THICK) * (Cylinder(d / 2, THICK + 2, align=(Align.CENTER, Align.CENTER, Align.MAX))
                                         + Cone(d / 2, d / 2 + ENTRY_CHAMFER, ENTRY_CHAMFER + 0.01,
                                                align=(Align.CENTER, Align.CENTER, Align.MAX)))
        part -= hole
        txt = label(f"{d:g}", size=LABEL_SIZE, depth=LABEL_DEPTH)
        part -= Pos(x, HOLE_Y - 16, THICK - LABEL_DEPTH) * txt
    part -= Pos(LENGTH / 2 - 14, 0, THICK) * Cylinder(HANG_D / 2, THICK + 2,
                                                       align=(Align.CENTER, Align.CENTER, Align.MAX))
    return part
