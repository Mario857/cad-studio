"""trolley-token: €1-size shopping-trolley token with keyring tab, set of 4.

Spec: 23.25 mm disc, 2.3 mm thick, with a keyring tab. The face is recessed 0.6 mm inside
a rim and the TEXT stands 0.6 mm proud of the recess, flush with the rim — so the token is
never thicker than TOKEN_T and still slides into the trolley lock. Printed flat, text up;
META copies = 4.

MEASURE BEFORE PRINTING (calipers): €1 coin Ø 23.25, thickness 2.33 — the token should
match your trolleys' coin slot (TOKEN_D / TOKEN_T are one-line edits, e.g. 25.75/2.2 for
€2 locks).

Assumptions: TEXT = "€1" at 9 mm; tab length 10 mm with Ø4 hole for a split ring.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="auto",
    copies=4,
)

TOKEN_D = 23.25
TOKEN_T = 2.3
TEXT = "€1"
TEXT_SIZE = 9.0
RELIEF = 0.6           # recess depth = text height
RIM = 1.4
TAB_L = 10.0           # beyond the disc edge
TAB_W = 9.0
RING_HOLE = 4.0


def build() -> Part:
    r = TOKEN_D / 2
    part = Cylinder(r, TOKEN_T, align=ON_BED) + Pos(r + TAB_L - TAB_W / 2, 0, 0) * Cylinder(TAB_W / 2, TOKEN_T, align=ON_BED)
    part += Pos(r, 0, 0) * Box(TAB_L - TAB_W / 2, TAB_W, TOKEN_T, align=(Align.MIN, Align.CENTER, Align.MIN))
    part += Pos(r - 3, 0, 0) * Box(3, TAB_W, TOKEN_T, align=(Align.MIN, Align.CENTER, Align.MIN))
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    part = chamfer(part.edges().group_by(Axis.Z)[-1], 0.3)
    part -= Pos(r + TAB_L - TAB_W / 2, 0, -1) * Cylinder(RING_HOLE / 2, TOKEN_T + 2, align=ON_BED)
    part -= Pos(0, 0, TOKEN_T - RELIEF) * Cylinder(r - RIM, 2, align=ON_BED)
    txt = Text(TEXT, font_size=TEXT_SIZE, font_style=FontStyle.BOLD)
    part += Pos(0, 0, TOKEN_T - RELIEF - 0.01) * extrude(txt, RELIEF + 0.01)
    return part
