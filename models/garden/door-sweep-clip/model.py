"""door-sweep-clip: 200 mm screw-free bug-barrier door sweep holder.

Spec: U-channel slides over the bottom edge of a 35-45 mm door (inner slot 40 mm, 2 mm
tolerance crush ribs on both inner walls) and carries a 12 mm wide brush/felt strip in a
lower slot opening downward (1 mm retention lips). Slot roof is a 45 deg chamfer, no flat ceilings.
Printed lying along its length (X on bed), profile upright, zero supports.
Assumptions: door slot 20 mm deep, walls 3 mm; 2 mm ribs are triangular crush ribs that
deform on thick doors (>40 mm) and grip thin ones; strip thickness ~12 mm, height <= 9 mm.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation="auto",
    supports="off",
    brim="auto",
)

LENGTH = 200.0
DOOR_SLOT = 40.0
WALL = 3.0
SLOT_DEPTH = 20.0
RIB_H = 2.0          # tolerance bump height
RIB_Z = 28.0
BRUSH_W = 12.0
BRUSH_H = 9.0        # vertical part of brush slot
LIP = 1.0            # retention lip each side
FLOOR_Z = 18.0       # door slot floor height


def build() -> Part:
    ow = DOOR_SLOT + 2 * WALL
    top = FLOOR_Z + SLOT_DEPTH
    h = ow / 2
    d = DOOR_SLOT / 2
    b = BRUSH_W / 2
    outer = Polygon((-h + .4, 0), (h - .4, 0), (h, .4), (h, top), (-h, top), (-h, .4), align=None)
    door = Polygon((-d, FLOOR_Z), (d, FLOOR_Z), (d, RIB_Z - RIB_H - 1), (d - RIB_H, RIB_Z - 1 + 0),
                   (d, RIB_Z + RIB_H), (d, top + 1), (-d, top + 1), (-d, RIB_Z + RIB_H),
                   (-d + RIB_H, RIB_Z - 1 + 0), (-d, RIB_Z - RIB_H - 1), align=None)
    brush = Polygon((-b + LIP, -1), (b - LIP, -1), (b - LIP, 1), (b, 1 + LIP), (b, BRUSH_H),
                    (0, BRUSH_H + b), (-b, BRUSH_H), (-b, 1 + LIP), (-b + LIP, 1), align=None)
    pl = Plane.YZ
    return extrude(pl * outer, LENGTH) - extrude(pl * door, LENGTH) - extrude(pl * brush, LENGTH)
