"""phone-stand: desk stand holding a phone in portrait or landscape at 65 degrees.

Spec: fits phones up to 12 mm thick (with case); cable slot for charging from below.
Assumptions: phone ~200 g, centered 45 mm above the lip.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="PLA",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, -8, 55), grams=200)],
    print_orientation="auto",
    supports="auto",
    brim="auto",
)

WIDTH = 70.0
BASE_DEPTH = 90.0
THICKNESS = 5.0
BACK_ANGLE = 65.0          # from horizontal
BACK_LENGTH = 95.0
SLOT = clearance(12.0, "loose")
LIP_HEIGHT = 10.0
CABLE_SLOT = 14.0


def build() -> Part:
    t, a = THICKNESS, math.radians(BACK_ANGLE)
    front_y = -BASE_DEPTH / 2
    back_foot_y = front_y + t + SLOT
    top = (back_foot_y + BACK_LENGTH * math.cos(a), BACK_LENGTH * math.sin(a))

    # Side profile in the YZ plane (y = depth, z = up), extruded across the width (X).
    profile = Polygon(
        (front_y, 0), (BASE_DEPTH / 2, 0), (BASE_DEPTH / 2, t),
        (back_foot_y + t / math.sin(a) + 20, t),
        (top[0] + t / math.sin(a), top[1]), top,
        (back_foot_y, t), (front_y + t, t), (front_y + t, LIP_HEIGHT), (front_y, LIP_HEIGHT),
        align=None,
    )
    stand = extrude(Plane.YZ * profile, WIDTH / 2, both=True)
    stand = fillet(stand.edges().filter_by(Axis.X).group_by(Axis.Z)[-1], 2)

    cable = Box(CABLE_SLOT, t + SLOT + 1, LIP_HEIGHT + 2, align=(Align.CENTER, Align.MIN, Align.MIN))
    stand -= Pos(0, front_y - 1, -1) * cable
    return stand
