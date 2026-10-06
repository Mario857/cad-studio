"""guyline-tensioner: line-lok style cam/wedge tensioner for 2-3 mm guyline, set of 8.

Spec: flat plate. Tent end: ATTACH slot for the tent's sewn loop / a cord loop (fixed).
Cord path: guyline from the stake runs under the plate, up through the WINDOW, over the
rounded CROSSBAR, and down into the WEDGE slot entered from the side edge. Under load the
loaded strand pins the tail into the tapering wedge (mouth CORD_D+0.6 -> CAM_GAP), so it
locks; lifting the TAB end (free end) tilts the plate and the cord slides to re-tension.
Tent end at x=0, stake/tab end at x=+46. Overall ~46 x 20 x 3.5 mm. Printed flat (in-use orientation) so line pull runs along layers.

Assumptions:
- Cord 2-3 mm (CORD_D = 3.0 nominal max); CAM_GAP 1.3 mm pinches 2 mm cord (compressible
  sheath) and 3 mm cord sits higher in the taper. Tune CAM_GAP for your cord.
- Tent loop/webbing <= 9 mm wide x 3 mm thick fits ATTACH slot; a cord loop also works.
- Loaded sections (rails around window/slot, around attach slot) >= 2.5 mm wide x 3.5 mm thick.
- Cord-contact edges filleted (EDGE_R) to protect the line; bottom 0.4 mm chamfer.
- Tab has a lightening/finger hole; non-load material removed there.
- Min loaded section: crossbar 4 mm, rail under wedge ~8 mm, around attach slot ~3 mm (x 3.5 thick).
- Wedge cam edges left unfilleted (cut after fillet/chamfer) for grip.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # flat: guyline pull along X runs along layers
    supports="off",
    brim="auto",
    copies=8,
)

# Parameters
CORD_D = 3.0          # max cord diameter
CAM_GAP = 1.3         # narrow end of wedge slot (grips 2 mm cord; 3 mm grips higher up)
WEDGE_MOUTH = CORD_D + 0.6
LENGTH = 46.0
WIDTH = 20.0
THICK = 3.5
CORNER_R = 4.0
EDGE_R = 0.8          # top-edge fillet (cord friendly)

ATTACH_X = 6.5        # centre of tent-end slot from tent end
ATTACH_L = 10.0       # slot length across plate (Y)
ATTACH_W = 3.6        # slot width (X)

WINDOW_X0 = 13.0      # cord window (through)
WINDOW_LEN = CORD_D + 3.0
WINDOW_W = 10.0
BAR = 4.0             # crossbar width (X) cord wraps around

WEDGE_ANGLE = -15.0   # slot leans toward stake/tab end (deg from Y axis) so pull drags cord into taper
WEDGE_DEPTH = 11.0    # from +Y edge inward
TAB_HOLE_D = 6.0      # finger/lightening hole in tab
TAB_HOLE_X = LENGTH - 7.0


def build() -> Part:
    plate = extrude(RectangleRounded(LENGTH, WIDTH, CORNER_R), THICK)
    plate = Pos(LENGTH / 2, 0, 0) * plate

    attach = Pos(ATTACH_X, 0, 0) * Rot(0, 0, 90) * extrude(SlotOverall(ATTACH_L, ATTACH_W), THICK)
    window = Pos(WINDOW_X0 + WINDOW_LEN / 2, 0, 0) * extrude(
        RectangleRounded(WINDOW_LEN, WINDOW_W, 1.2), THICK)

    # wedge slot: tapers from the +Y edge (mouth) inward to CAM_GAP, leaning toward stake end
    wx = WINDOW_X0 + WINDOW_LEN + BAR + WEDGE_MOUTH / 2  # mouth centre x at edge
    y0, y1 = WIDTH / 2 + 1.0, WIDTH / 2 - WEDGE_DEPTH
    import math
    dx = (y0 - y1) * math.tan(math.radians(WEDGE_ANGLE))
    wedge_sk = Polygon(
        (wx - WEDGE_MOUTH / 2, y0), (wx + WEDGE_MOUTH / 2, y0),
        (wx - dx + CAM_GAP / 2, y1), (wx - dx - CAM_GAP / 2, y1), align=None)
    wedge = extrude(wedge_sk, THICK)
    wedge_end = Pos(wx - dx, y1, 0) * Cylinder(CAM_GAP / 2, THICK, align=ON_BED)

    tab_hole = Pos(TAB_HOLE_X, 0, 0) * Cylinder(TAB_HOLE_D / 2, THICK, align=ON_BED)

    part = plate - attach - window - tab_hole
    part = fillet(part.edges().group_by(Axis.Z)[-1], EDGE_R)
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    # wedge cut last: its narrow cam edges stay sharp-ish for grip (no chamfer/fillet)
    return part - wedge - wedge_end
