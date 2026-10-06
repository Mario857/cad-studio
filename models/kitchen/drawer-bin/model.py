"""drawer-bin: modular drawer organizer bin on a 42 mm grid.

Spec: open-top bin whose footprint is UNITS_X * 42 x UNITS_Y * 42 mm minus a 0.5 mm gap
(default 2 x 1 -> 83.5 x 41.5 mm) so neighbouring bins sit side by side. Height 50 mm, 1.6 mm walls,
rounded vertical inside corners plus a cove-filleted floor edge for easy scooping, and a small
45 deg label ledge on the inside of the -X end wall (flat top for a label strip / small items).
Not stackable. Prints open side up with no supports.
Assumptions: 1.6 mm floor, grid pitch 42 mm, ledge on the short end (-X), PLA standard quality.
"""

from build123d import *

from cadlib import *

META = dict(
    material="PLA",
    quality="standard",
    standing=True,
    loads=[],
    print_orientation="auto",
    supports="auto",
    brim="auto",
)

# Parameters
UNITS_X = 2
UNITS_Y = 1
GRID = 42.0
GAP = 0.5
HEIGHT = 50.0
WALL = 1.6
FLOOR = 1.6
OUTER_R = 3.0          # outer vertical corner radius
INNER_R = 6.0           # inner vertical corner radius (scoop-friendly)
COVE_R = 4.0           # inner floor-edge fillet
LEDGE_W = 4.0          # how far the label ledge sticks in
LEDGE_Z = 40.0         # height of the ledge's flat top

LENGTH = UNITS_X * GRID - GAP
WIDTH = UNITS_Y * GRID - GAP


def build() -> Part:
    outer = rounded_box(LENGTH, WIDTH, HEIGHT, radius=OUTER_R, bottom_chamfer=0.4)

    in_l, in_w = LENGTH - 2 * WALL, WIDTH - 2 * WALL
    inner = extrude(RectangleRounded(in_l, in_w, INNER_R), HEIGHT - FLOOR + 1)
    inner = Pos(0, 0, FLOOR) * inner
    inner = fillet(inner.edges().group_by(Axis.Z)[0], COVE_R)
    part = outer - inner

    # label ledge on the inside of the -X end wall: flat top, 45 deg underside
    x0 = -LENGTH / 2 + WALL
    tri = Polygon(
        (x0 - 0.5, LEDGE_Z - LEDGE_W - 0.5),
        (x0 - 0.5, LEDGE_Z),
        (x0 + LEDGE_W, LEDGE_Z),
        align=None,
    )
    ledge_w = in_w - 2 * INNER_R - 2.0
    ledge = extrude(Plane.XZ * tri, ledge_w / 2, both=True)
    return part + ledge
