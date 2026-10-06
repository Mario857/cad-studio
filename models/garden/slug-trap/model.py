"""slug-trap: beer slug trap - sunk cup plus a removable rain roof on 4 posts.

Spec: Ø100 mm cup, 100 mm tall, sunk so its rim stands RIM_ABOVE_SOIL = 10 mm above the
ground (a 45° soil-line collar marks the burying depth). Slugs climb the short rim and fall
into the beer. A conical rain roof (Ø124, 50° pitch) stands on 4 posts whose pins drop into
lugs on the rim; its eave sits ENTRY_GAP = 15 mm above the rim all round, so slugs get in but
rain and pets/birds' beaks mostly don't. The roof + posts IS the removable lid: lift it off,
empty and refill the cup in place.
2 parts printed together in their print poses: cup upright, roof upside down (plateau on the
bed, posts/pins up), so model coordinates are print poses. No supports.
Material: AzureFilm ABS PLUS. ABS+ yellows/embrittles after a season or two in full sun; the
user's "AzureFilm ASA @BBL H2C 0.4 nozzle" preset is the long-life swap (same geometry).

Assumptions:
- Pins Ø4 in Ø4 + 2 x PIN_FIT (slide) holes, 7 mm deep: drop-in, no tools.
- Beer capacity ≈ 400 ml up to ~25 mm below the rim.
- Cup wall 2.4 mm is enough for soil pressure on a buried Ø100 cup.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),   # parts already in print poses
    supports="off",
    brim="auto",
    copies=1,
)

CUP_D = 100.0
CUP_H = 100.0
WALL = 2.4
FLOOR_T = 2.4
RIM_ABOVE_SOIL = 10.0
COLLAR_W = 3.0
ENTRY_GAP = 15.0       # eave height above the rim
ROOF_EAVE_R = 62.0
ROOF_T = 2.4
ROOF_PITCH = 50.0     # degrees from horizontal (> 45° for margin when printed upside down)
ROOF_PLATEAU_R = 15.0
POST_R_POS = 54.0      # post circle radius (on the rim lugs)
POST_D = 7.0
PIN_D = 4.0
PIN_FIT = "slide"
PIN_LEN = 7.0
LUG_W = 11.0
LUG_H = 8.0
GAP = 12.0             # spacing between the two parts on the plate

R = CUP_D / 2


def cup() -> Part:
    part = Cylinder(R, CUP_H, align=ON_BED)
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    part -= Pos(0, 0, FLOOR_T) * Cylinder(R - WALL, CUP_H, align=ON_BED)
    # soil-line collar: 45° underside, flat top at the soil line
    zs = CUP_H - RIM_ABOVE_SOIL
    collar = Polygon((R - 0.5, zs - COLLAR_W - 0.5), (R + COLLAR_W, zs), (R - 0.5, zs), align=None)
    part += revolve(Plane.XZ * collar, Axis.Z)
    # 4 rim lugs with 45° undersides and pin holes
    lug_out = POST_R_POS + POST_D / 2 + 1
    prof = Polygon((R - 1, CUP_H), (lug_out, CUP_H), (lug_out, CUP_H - LUG_H),
                   (R - 1, CUP_H - LUG_H - (lug_out - R + 1)), align=None)
    lug = extrude(Plane.XZ * prof, LUG_W / 2, both=True)
    for i in range(4):
        part += Rot(0, 0, 90 * i) * lug
        part -= Rot(0, 0, 90 * i) * Pos(POST_R_POS, 0, CUP_H) * pin_hole(clearance(PIN_D, PIN_FIT), PIN_LEN + 0.5)
    return part


def roof_in_use() -> Part:
    """Roof in its in-use pose, z = 0 at the cup rim."""
    k = math.tan(math.radians(ROOF_PITCH))
    tv = ROOF_T / math.cos(math.radians(ROOF_PITCH))   # vertical thickness of the sloped shell
    z_e = ENTRY_GAP
    rise = (ROOF_EAVE_R - ROOF_PLATEAU_R) * k
    solid = revolve(Plane.XZ * Polygon((0, z_e + rise), (ROOF_PLATEAU_R, z_e + rise), (ROOF_EAVE_R, z_e),
                                       (ROOF_EAVE_R, z_e + tv), (ROOF_PLATEAU_R, z_e + tv + rise),
                                       (0, z_e + tv + rise), align=None), Axis.Z)
    part = solid
    # posts are trimmed to the roof's top surface so they never poke through it
    under_top = revolve(Plane.XZ * Polygon((0, -20), (ROOF_EAVE_R + 10, -20), (ROOF_EAVE_R + 10, z_e + tv),
                                           (ROOF_EAVE_R, z_e + tv), (ROOF_PLATEAU_R, z_e + tv + rise),
                                           (0, z_e + tv + rise), align=None), Axis.Z)
    for i in range(4):
        h = z_e + (ROOF_EAVE_R - POST_R_POS + POST_D / 2) * k + 1      # reaches the underside everywhere
        post = Pos(POST_R_POS, 0, 0) * Cylinder(POST_D / 2, h, align=ON_BED)
        pin = Pos(POST_R_POS, 0, 0) * Cylinder(PIN_D / 2, PIN_LEN, align=(Align.CENTER, Align.CENTER, Align.MAX))
        pin = chamfer(pin.edges().group_by(Axis.Z)[0], 0.5)
        part += Rot(0, 0, 90 * i) * ((post & under_top) + pin)
    return part


def build():
    roof = Rot(180, 0, 0) * roof_in_use()
    zmin = roof.bounding_box().min.Z
    roof = Pos(R + ROOF_EAVE_R + GAP, 0, -zmin) * roof
    return [cup(), roof]
