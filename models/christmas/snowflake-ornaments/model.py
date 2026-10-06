"""snowflake-ornaments: set of 3 different flat 6-fold snowflake Christmas ornaments.

Spec: three distinct snowflakes, 80 mm tip-to-tip across the arms, 3 mm thick, every
strut/feature >= 1.2 mm (struts are 2.0-2.4 mm). Each has a hanging loop at the top arm tip
(5 mm hole for ribbon/thread/ornament hook). build() returns the 3 snowflakes as separate parts
laid out side by side on the plate, printed together in one job
(the check's "3 separate bodies" WARN is therefore intended).

Assumptions:
- "80 mm across" = arm tip to arm tip; the hanging loop sticks out beyond that (~7.5 mm).
- Modelled lying flat (Z = thickness) since that is the print orientation and the flat shape is
  the same in use (hangs vertically from the loop); print_orientation fixed to flat (0, 0, 0).
- 5 mm loop hole fits standard ornament hooks and ribbon up to ~4 mm wide.
- Bottom edges get a 0.4 mm elephant-foot chamfer.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # flat: thickness along Z, no supports
    supports="off",  # flat plate, nothing overhangs except the 0.4 mm bottom chamfer,
    brim="auto",
)

# Parameters
DIAMETER = 80.0          # arm tip to arm tip
THICKNESS = 3.0
ARM_W = 2.4              # main arm width
BRANCH_W = 2.0           # side branch width (>= 1.2 min feature)
LOOP_OD = 9.0            # hanging loop outer diameter
LOOP_HOLE_D = 5.0        # hanging loop hole diameter
LOOP_OVERLAP = 1.5       # loop overlaps the arm tip (< ring wall, keeps hole clear of arm)
BOTTOM_CHAMFER = 0.4
SPACING = 92.0           # centre-to-centre spacing of the 3 snowflakes on the plate

R = DIAMETER / 2


def _bar(x0, y0, x1, y1, w):
    """Rounded 2D bar from (x0,y0) to (x1,y1) of width w."""
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    ang = math.degrees(math.atan2(dy, dx))
    return Pos((x0 + x1) / 2, (y0 + y1) / 2) * Rot(0, 0, ang) * SlotOverall(length + w, w)


def _branch(r, length, w, ang=60):
    """Pair of side branches leaving the +Y arm at radius r, angled `ang` deg off the arm."""
    a = math.radians(ang)
    bx, by = length * math.sin(a), r + length * math.cos(a)
    return _bar(0, r, bx, by, w) + _bar(0, r, -bx, by, w)


def _six(sketch):
    s = sketch
    for i in range(1, 6):
        s = s + Rot(0, 0, 60 * i) * sketch
    return s


def _ring(r_out, r_in):
    return Circle(r_out) - Circle(r_in)


def _hex_ring(r_out, w):
    return RegularPolygon(r_out, 6) - RegularPolygon(r_out - w / math.cos(math.radians(30)), 6)


def flake_a():
    """Classic fern: arm with three pairs of branches, solid hex centre."""
    arm = _bar(0, 0, 0, R - ARM_W / 2, ARM_W)
    arm = arm + _branch(12, 9, BRANCH_W) + _branch(21, 10, BRANCH_W) + _branch(30, 6, BRANCH_W)
    return _six(arm) + RegularPolygon(7, 6, major_radius=True)


def flake_b():
    """Hex rings: open centre hexagon ring, arms with a diamond near the tip."""
    arm = _bar(0, 0, 0, R - ARM_W / 2, ARM_W)
    diamond = Pos(0, 29) * Rot(0, 0, 0) * (
        Polygon((0, -7), (5, 0), (0, 7), (-5, 0), align=None)
        - Polygon((0, -4), (2.2, 0), (0, 4), (-2.2, 0), align=None)
    )
    arm = arm + diamond + _branch(15, 7, BRANCH_W, ang=45)
    return _six(arm) + _hex_ring(11, 2.2) + Circle(3.5)


def flake_c():
    """Plate + dendrite: round ring at mid radius, forked tips, star centre."""
    arm = _bar(0, 0, 0, R - ARM_W / 2, ARM_W)
    fork = _branch(29, 7, BRANCH_W, ang=30)
    inner = _branch(8, 7, BRANCH_W, ang=60)
    arm = arm + fork + inner
    return _six(arm) + _ring(19, 16.8) + Circle(4.5)


def _finish(sketch):
    # Loop is a ring unioned on (no cut through the arm); the arm tip stays below the hole.
    s = sketch + Pos(0, R + LOOP_OD / 2 - LOOP_OVERLAP) * _ring(LOOP_OD / 2, LOOP_HOLE_D / 2)
    part = extrude(s, THICKNESS)
    bottom = part.edges().group_by(Axis.Z)[0]
    return chamfer(bottom, BOTTOM_CHAMFER)


def build():
    flakes = [flake_a(), flake_b(), flake_c()]
    return [Pos((i - 1) * SPACING, 0, 0) * _finish(f) for i, f in enumerate(flakes)]
