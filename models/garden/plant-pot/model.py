"""plant-pot: modern faceted herb pot (~110 mm top dia, 100 mm tall) with drainage holes and a matching drip saucer.

Spec: two separate bodies printed side by side on one plate. The pot is a 20-sided tapered
prism (subtle vertical facets) with a conical cavity, 3 mm floor and 6 drainage holes.
The saucer has the same faceted look, a shallow flared wall and 4 small feet on its floor so the
pot stands ~3 mm above any collected water.
Assumptions: PETG, standard quality, no supports. Pot top outer circumradius 55 mm (flat-to-flat
~108.6 mm), bottom 45 mm. Both bodies rest on z=0 (print layout, not assembled); in use the pot
drops into the saucer onto the feet. The "2 separate bodies" WARN is intended (pot + saucer).
Wall 2.4 mm at the facet centres (>= 1.2 mm, 6 perimeters).
"""

from math import atan2, cos, degrees, pi, sin, tan

from build123d import *

from cadlib import *

META = dict(
    material="PETG",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation="auto",
    supports="off",
    brim="auto",
)

# Pot
SIDES = 20                 # facets around the circumference
POT_H = 100.0
POT_R_BOT = 45.0           # outer circumradius at the bed
POT_R_TOP = 55.0           # outer circumradius at the rim
POT_WALL = 2.6             # at facet centres
POT_FLOOR = 3.0
HOLE_D = 6.0
HOLE_RING_R = 20.0
N_HOLES = 5
BOT_CHAMFER = 0.6

# Saucer
SAU_H = 15.0
SAU_R_BOT = 52.0
SAU_R_TOP = 60.0
SAU_WALL = 2.4
SAU_FLOOR = 2.4
FOOT_D = 9.0
FOOT_H = 3.0
FOOT_RING_R = 34.0
GAP = 12.0                 # plate spacing between the two bodies

APO = cos(pi / SIDES)      # apothem / circumradius for the facet polygon


def faceted(r_bot, r_top, h):
    taper = degrees(atan2(r_top - r_bot, h))
    return extrude(Plane.XY * RegularPolygon(r_bot, SIDES), h, taper=-taper)


def cavity(r_out_bot, r_out_top, h, wall, floor):
    """Conical cavity whose wall is `wall` thick at the facet centres."""
    slope = (r_out_top - r_out_bot) / h
    r_bot = r_out_bot * APO - wall + slope * floor
    r_top = r_out_top * APO - wall
    cav = Pos(0, 0, floor) * Cone(r_bot, r_top, h - floor + 0.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return cav


def pot() -> Part:
    body = faceted(POT_R_BOT, POT_R_TOP, POT_H)
    body = chamfer(body.edges().group_by(Axis.Z)[0], BOT_CHAMFER)
    body = body - cavity(POT_R_BOT, POT_R_TOP, POT_H, POT_WALL, POT_FLOOR)
    pts = [(0, 0)] + [
        (HOLE_RING_R * cos(2 * pi * i / N_HOLES), HOLE_RING_R * sin(2 * pi * i / N_HOLES))
        for i in range(N_HOLES)
    ]
    for x, y in pts:
        body = body - Pos(x, y, 0) * Cylinder(HOLE_D / 2, POT_FLOOR * 3, align=ON_BED)
    return body


def saucer() -> Part:
    body = faceted(SAU_R_BOT, SAU_R_TOP, SAU_H)
    body = chamfer(body.edges().group_by(Axis.Z)[0], BOT_CHAMFER)
    body = body - cavity(SAU_R_BOT, SAU_R_TOP, SAU_H, SAU_WALL, SAU_FLOOR)
    for i in range(4):
        a = pi / 4 + i * pi / 2
        body = body + Pos(FOOT_RING_R * cos(a), FOOT_RING_R * sin(a), SAU_FLOOR - 0.1) * Cylinder(
            FOOT_D / 2, FOOT_H + 0.1, align=ON_BED
        )
    return body


def build():
    offset = SAU_R_TOP + POT_R_TOP + GAP
    return [Pos(-offset / 2 + 0, 0, 0) * pot(), Pos(offset / 2, 0, 0) * saucer()]
