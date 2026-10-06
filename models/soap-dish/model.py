"""soap-dish: self-draining soap dish, ~122 x 85 mm, PETG, prints with no supports.

Spec: the soap rests on 8 raised parallel ribs so its underside can dry. The floor between the
ribs slopes 3 deg toward the +X end, where the end wall is open (40 mm wide) and the floor
continues out as a tapered spout lip, so water runs off into the sink instead of pooling.
The ribs run along the fall line so water is guided to the spout. Body is a solid wedge with a
flat underside (prints flat on the bed, no overhangs).
Assumptions: bar soap up to ~90 x 60 mm; spout end hangs over the sink edge or is placed
facing the drain; PETG for wet use; 3 deg fall is enough for water to run (not so steep that
the soap slides, ribs are 4 mm tall).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="PETG",
    quality="standard",
    standing=False,
    loads=[dict(at=(0, 0, 10), grams=120)],   # a wet bar of soap
    print_orientation="auto",
    supports="off",
    brim="auto",
)

# Parameters
BODY_L = 110.0        # main tray length (X)
BODY_W = 85.0         # tray width (Y)
CORNER_R = 8.0        # plan corner radius
WALL = 2.4            # side wall
RIM_H = 16.0          # rim height above bed (flat top)
SLOPE_DEG = 3.0       # floor fall toward +X
TIP_FLOOR = 2.5       # floor thickness at spout tip
SPOUT_LEN = 12.0      # lip beyond the main body
SPOUT_W_ROOT = 50.0   # lip width at body
SPOUT_W_TIP = 26.0    # lip width at tip
OPENING_W = 40.0      # width of the open wall at the spout end
RIB_N = 8
RIB_PITCH = 10.0
RIB_T = 2.4
RIB_H = 4.0
BOTTOM_CHAMFER = 0.4

X_END = BODY_L / 2 + SPOUT_LEN
TAN_A = math.tan(math.radians(SLOPE_DEG))


def floor_z(x: float) -> float:
    return TIP_FLOOR + (X_END - x) * TAN_A


def build() -> Part:
    xb = BODY_L / 2
    # outer plan: rounded body + tapered spout tab
    plan = extrude(Plane.XY * RectangleRounded(BODY_L, BODY_W, CORNER_R), RIM_H)
    tab = extrude(
        Plane.XY * Polygon((xb - 6, -SPOUT_W_ROOT / 2), (X_END, -SPOUT_W_TIP / 2),
                           (X_END, SPOUT_W_TIP / 2), (xb - 6, SPOUT_W_ROOT / 2), align=None),
        RIM_H)
    body = plan + tab
    body = chamfer(body.edges().group_by(Axis.Z)[0], BOTTOM_CHAMFER)

    # cutter = everything above the sloped floor inside the walls + the open spout end
    inner = extrude(Plane.XY.offset(0.01) * RectangleRounded(BODY_L - 2 * WALL, BODY_W - 2 * WALL,
                                                             CORNER_R - WALL), 3 * RIM_H)
    opening = Pos(xb - WALL - 1, 0, 0) * Box(30, OPENING_W, 3 * RIM_H, align=(Align.MIN, Align.CENTER, Align.MIN))
    tabcut = Pos(xb, 0, 0) * Box(30, SPOUT_W_ROOT + 10, 3 * RIM_H, align=(Align.MIN, Align.CENTER, Align.MIN))
    x0, x1 = -X_END - 5, X_END + 5
    wedge = extrude(Plane.XZ * Polygon((x0, -1), (x1, -1), (x1, floor_z(x1)), (x0, floor_z(x0)),
                                       align=None), BODY_W, both=True)
    body = body - ((inner + opening + tabcut) - wedge)

    # ribs along the fall line, standing on the sloped floor
    rx0 = -xb + WALL - 0.5
    for i in range(RIB_N):
        y = (i - (RIB_N - 1) / 2) * RIB_PITCH
        # outer ribs stop in the end wall; inner ribs run out onto the spout lip (stay inside its width)
        rx1 = X_END - 7 if abs(y) <= 15 else xb - 1
        prof = Polygon((rx0, floor_z(rx0) - 1), (rx1, floor_z(rx1) - 1),
                       (rx1, floor_z(rx1) + RIB_H), (rx0, floor_z(rx0) + RIB_H), align=None)
        body = body + Pos(0, y, 0) * extrude(Plane.XZ * prof, RIB_T / 2, both=True)
    return body
