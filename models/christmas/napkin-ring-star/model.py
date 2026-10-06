"""napkin-ring-star: Christmas napkin ring with star cut-outs, set of 6.

Spec: plain cylindrical ring, Ø45 mm inside, 25 mm wide (axis length), 3 mm wall.
Around the wall: 6 four-pointed "sparkle" stars (tall diamond + square diamond) cut radially
through the wall, alternating with 6 small diamonds. Printed standing on its ring edge (axis
vertical), so every cut-out is a horizontal radial hole; all hole ceilings slope at <= 45 deg from
vertical (diamond tops / 45 deg star shoulders), so no supports are needed.

Assumptions:
- Wall 3 mm (OD 51) for stiffness; rims of >= 4.5 mm above/below the stars.
- Star 16 mm tall x 10 mm wide; small diamond 6 mm square-diagonal; all pointed tips upward.
- Top/bottom edges get 0.4 mm chamfers (elephant foot / comfort).
- No fit to anything; napkins of normal cloth thickness pass through Ø45.
- Model coordinates: axis vertical (= print orientation); in use it lies on its side.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,            # decorative, lies on the table
    loads=[],
    print_orientation=(0, 0, 0),  # stand on ring edge: cut-outs become self-supporting radial holes
    supports="off",
    brim="auto",
    copies=6,
)

# Parameters
INNER_D = 45.0
WALL = 3.0
WIDTH = 25.0               # ring length along its axis (print height)
EDGE_CHAMFER = 0.4

N_STARS = 6
STAR_HALF_H = 8.0          # tall diamond half-height (vertical star points)
STAR_HALF_W = 2.5          # tall diamond half-width
STAR_SIDE = 5.0            # square diamond half-diagonal (side points, 45 deg shoulders)
SMALL_DIAMOND = 3.0        # small diamond half-diagonal, between stars

OUTER_D = INNER_D + 2 * WALL
CUT_LEN = OUTER_D          # radial cutter length (from axis outward)


def _diamond(half_w, half_h):
    return Polygon((half_w, 0), (0, half_h), (-half_w, 0), (0, -half_h), align=None)


def _radial_cut(sketch, angle_deg):
    # Plane.XZ: local x = X, local y = Z; extrudes toward -Y (outward through one side only).
    cutter = extrude(Plane.XZ * Pos(0, WIDTH / 2) * sketch, amount=CUT_LEN)
    return Rot(0, 0, angle_deg) * cutter


def build() -> Part:
    ring = Cylinder(OUTER_D / 2, WIDTH, align=ON_BED) - Cylinder(INNER_D / 2, WIDTH, align=ON_BED)
    ring = chamfer(ring.edges().filter_by(GeomType.CIRCLE), EDGE_CHAMFER)

    star = _diamond(STAR_HALF_W, STAR_HALF_H) + _diamond(STAR_SIDE, STAR_SIDE)
    small = _diamond(SMALL_DIAMOND, SMALL_DIAMOND)

    step = 360 / N_STARS
    cutters = None
    for i in range(N_STARS):
        for sk, a in ((star, i * step), (small, i * step + step / 2)):
            c = _radial_cut(sk, a)
            cutters = c if cutters is None else cutters + c
    return ring - cutters
