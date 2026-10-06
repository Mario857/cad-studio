"""ornament-hooks: S-shaped Christmas ornament hooks, set of 20.

Spec: S hook 40 mm long overall, 2.0 x 2.0 mm square-ish wire section (>= 1.6 mm required).
Top hook (inner gap ~12 mm) hangs over a tree branch, bottom hook (inner gap ~9 mm) takes the
ornament's loop/cap wire. Both hook tips wrap 220 deg so they don't slip off. Rounded tips.
In-use model: S profile in the XZ plane, hanging (Z up), thickness along Y.
Printed flat (S profile on the bed, rotated 90 deg about X) so the bending load in the curves runs
along the layer lines, not across them. 20 copies via META.

Assumptions:
- Ornaments <= ~100 g; branch diameter <= ~11 mm.
- 2 mm wire is stiff enough in ABS; if hooks feel flimsy, raise WIRE / THICK to 2.4.
- standing=False: hooks hang, no tip-over audit.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(90, 0, 0),  # S profile flat on the bed: load runs along layers
    supports="off",
    brim="auto",
    copies=20,
)

# Parameters
LENGTH = 40.0        # overall hook length (Z, in use)
WIRE = 2.0           # wire width in the S plane
THICK = 2.0          # wire thickness (print height)
R_TOP = 7.0          # centerline radius of top (branch) hook
R_BOT = 5.5          # centerline radius of bottom (ornament) hook
WRAP = 220.0         # arc sweep of each hook, deg
BED_CHAMFER = 0.3    # elephant-foot chamfer on bed-side edges


def build() -> Part:
    shank = LENGTH - WIRE - R_TOP - R_BOT
    y_bot = WIRE / 2 + R_BOT
    y_top = y_bot + shank
    top = CenterArc((-R_TOP, y_top), R_TOP, 0, WRAP)
    line = Line((0, y_bot), (0, y_top))
    bot = CenterArc((R_BOT, y_bot), R_BOT, 180, WRAP)
    path = Wire([top, line, bot])
    outline = path.offset_2d(WIRE / 2, kind=Kind.ARC, side=Side.BOTH)
    face = Face(outline)
    part = extrude(Plane.XZ * face, THICK / 2, both=True)
    # light chamfer on both flat faces (bed side = elephant foot, top side = symmetry)
    flat = part.faces().filter_by(Axis.Y)
    part = chamfer(flat.edges(), BED_CHAMFER)
    return Part(part) if not isinstance(part, Part) else part
