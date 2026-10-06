"""gift-box-hex: hexagonal Christmas gift box with lift-off lid and raised star.

Spec: hexagonal box, 100 mm across flats, 60 mm tall closed (box + lid plate; the star
sits on top of that). The lid has a hex plug that drops into the box opening with a
slide fit (LID_FIT -> clearance()). The lid plate's underside rim is a 45 deg chamfer
that seats on the box's inner top edge (self-centring) and reads as a decorative seam.
Box and lid print together on one plate; the lid prints in use orientation (plug on the
bed, star up): the only overhang is the 45 deg rim chamfer, so no supports.

Assumptions:
- "100 mm across" = across flats (115.5 mm across corners).
- 60 mm height = closed box to lid top surface; the 3 mm star is extra on top.
- The lid plug is solid (a hollow plug would need an ~90 mm unsupported bridge).
- Decorative use only; no loads.
- "2 separate bodies" mesh WARN is intended: build() returns [box, lid] printed together.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[],
    print_orientation=(0, 0, 0),  # box open side up, lid star up: both support-free
    supports="off",
    brim="auto",
)

# Parameters
ACROSS_FLATS = 100.0     # outer hex, across flats
TOTAL_H = 60.0           # closed height to lid top surface (star excluded)
WALL = 2.4               # box side wall
FLOOR = 2.0              # box floor
LID_T = 4.0              # lid plate thickness
PLUG_H = 5.0             # lid plug depth into box
LID_FIT = "slide"        # fit of plug in box opening (clearance() fit name)
STAR_R_OUT = 30.0        # star outer radius
STAR_R_IN = 12.5         # star inner radius
STAR_H = 3.0             # star height above lid
BED_CHAMFER = 0.4        # elephant-foot chamfer on bed edges
GAP = 12.0               # gap between box and lid on the plate

COS30 = math.cos(math.radians(30))
INNER_FLATS = ACROSS_FLATS - 2 * WALL
FIT_GAP = (clearance(INNER_FLATS, LID_FIT) - INNER_FLATS) / 2   # per side
PLUG_FLATS = INNER_FLATS - 2 * FIT_GAP
RIM_CHAMFER = (ACROSS_FLATS - PLUG_FLATS) / 2                    # 45 deg underside chamfer
BOX_H = TOTAL_H - LID_T + FIT_GAP  # lid chamfer seats FIT_GAP below plate bottom level


def hexagon(flats: float) -> Sketch:
    return RegularPolygon(flats / 2 / COS30, 6)


def hex_prism(flats: float, h: float) -> Part:
    return extrude(hexagon(flats), h)


def star() -> Part:
    pts = []
    for i in range(10):
        r = STAR_R_OUT if i % 2 == 0 else STAR_R_IN
        a = math.radians(90 + i * 36)
        pts.append((r * math.cos(a), r * math.sin(a)))
    return extrude(Polygon(*pts, align=None), STAR_H)


def build_box() -> Part:
    outer = hex_prism(ACROSS_FLATS, BOX_H)
    outer = chamfer(outer.edges().group_by(Axis.Z)[0], BED_CHAMFER)
    cavity = Pos(0, 0, FLOOR) * hex_prism(INNER_FLATS, BOX_H)
    return outer - cavity


def build_lid() -> Part:
    # in-use orientation, plug bottom at z=0
    plug = hex_prism(PLUG_FLATS, PLUG_H)
    plug = chamfer(plug.edges().group_by(Axis.Z)[0], BED_CHAMFER)
    rim = loft([
        Plane.XY.offset(PLUG_H) * hexagon(PLUG_FLATS),
        Plane.XY.offset(PLUG_H + RIM_CHAMFER) * hexagon(ACROSS_FLATS),
    ])
    plate = Pos(0, 0, PLUG_H + RIM_CHAMFER) * hex_prism(ACROSS_FLATS, LID_T - RIM_CHAMFER)
    lid = plug + rim + plate
    lid += Pos(0, 0, PLUG_H + LID_T) * star()
    return lid


def build():
    box = build_box()
    lid = Pos(ACROSS_FLATS / COS30 + GAP, 0, 0) * build_lid()
    return [box, lid]
