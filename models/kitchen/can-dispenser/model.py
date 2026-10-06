"""can-dispenser: gravity-roll fridge dispenser for 6 x 330 ml cans (2 lanes x 3).

Spec: cans lie sideways in two lanes and roll forward on 6 deg sloped rails against a front
stop; take the front can and the next one rolls in. Load from the open back. 251 x 225 mm
footprint fits a standard fridge shelf; base plate has large windows (less plastic, less
ABS warp, fridge air flows through).
Assumptions: 330 ml can = 66 mm dia x 115 mm long (std. 330 ml), ~350 g full; lane inner
width 122 mm leaves 7 mm side play; shelf is level. ABS is not food-safe, but cans are
sealed so there is no direct food contact.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(-62, 0, 45), grams=1050), dict(at=(62, 0, 45), grams=1050)],
    print_orientation="auto",
    supports="auto",
    brim="on",
)

# Parameters
CAN_D = 66.0
CAN_L = 115.0
CANS_PER_LANE = 3
LANES = 2
LANE_W = 122.0         # inner lane width (can length + play)
WALL = 2.4
BASE_T = 2.4
SLOPE_DEG = 6.0
RAIL_FRONT_H = 8.0     # rail top height at the front stop
RAIL_T = 3.0
RAIL_INSET = 30.0      # rails sit this far in from each lane wall
SIDE_ABOVE_RAIL = 42.0
STOP_ABOVE_RAIL = 24.0
STOP_T = 3.0
EXTRA_L = 25.0         # slack behind the last can
CORNER_R = 6.0


def build() -> Part:
    import math
    width = LANES * LANE_W + (LANES + 1) * WALL
    length = CANS_PER_LANE * CAN_D + EXTRA_L + STOP_T
    y0, y1 = -length / 2, length / 2  # front (-Y) .. back
    rise = math.tan(math.radians(SLOPE_DEG))

    base = rounded_box(width, length, BASE_T, radius=CORNER_R)
    # windows under each lane between the rails
    win_w = LANE_W - 2 * RAIL_INSET - 2 * RAIL_T - 4
    for i in range(LANES):
        cx = -width / 2 + WALL + LANE_W / 2 + i * (LANE_W + WALL)
        base -= Pos(cx, 0, -1) * rounded_box(win_w, length - 30, BASE_T + 2, radius=8,
                                             bottom_chamfer=0)

    def ramp(top_front, top_back, thick):
        prof = Polygon((y0, 0), (y1, 0), (y1, top_back), (y0, top_front), align=None)
        return extrude(Plane.YZ * prof, thick)

    rail_f, rail_b = RAIL_FRONT_H, RAIL_FRONT_H + length * rise
    part = base
    # lane walls (outer + dividers), sloped tops
    wall = ramp(rail_f + SIDE_ABOVE_RAIL, rail_b + SIDE_ABOVE_RAIL, WALL)
    for i in range(LANES + 1):
        x = -width / 2 + i * (LANE_W + WALL)
        part += Pos(x, 0, 0) * wall
    # rails
    rail = ramp(rail_f, rail_b, RAIL_T)
    for i in range(LANES):
        lx = -width / 2 + WALL + i * (LANE_W + WALL)
        part += Pos(lx + RAIL_INSET, 0, 0) * rail
        part += Pos(lx + LANE_W - RAIL_INSET - RAIL_T, 0, 0) * rail
    # front stop
    part += Pos(0, y0 + STOP_T / 2, 0) * Box(width, STOP_T, rail_f + STOP_ABOVE_RAIL,
                                             align=ON_BED)
    return part
