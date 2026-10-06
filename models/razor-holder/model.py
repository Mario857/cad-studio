"""razor-holder: wall-mounted holder for 2 cartridge razors (head up, handle hanging).

Spec: back plate with a shelf that has two open-front U-slots; a razor hangs by its
head with the handle neck in a slot. A 45 deg gusset under the shelf, a 3 mm 45 deg wedge lip at the front
keeps heads from sliding forward; drain gaps (the slots) keep it dry.
Mount: 2 countersunk 4 mm screws (or VHB tape on the flat back).
Printed back-down (print_orientation (90,0,0)): no overhangs, no supports. The shelf
then bends across layers; accepted because the load is ~2 x 60 g and the shelf root
is 5 mm + gusset.
Assumptions: handle neck <= 11 mm wide, razor head >= 20 mm wide; shelf 45 mm from wall.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[dict(at=(x, 25, 45), grams=60) for x in (-20, 20)],
    print_orientation=(90, 0, 0),
    supports="auto",
    brim="auto",
)

# Parameters
WIDTH = 80.0
PLATE_H = 60.0
PLATE_T = 4.0
SHELF_Z = 40.0           # shelf top
SHELF_T = 5.0
SHELF_D = 45.0           # from wall
SLOT_W = 12.0
SLOT_DEPTH = 28.0
SLOT_X = 20.0
LIP_H = 3.0
GUSSET = 20.0
SCREW = "M4"


def build() -> Part:
    plate = Pos(0, PLATE_T / 2, 0) * Box(WIDTH, PLATE_T, PLATE_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    shelf = Pos(0, SHELF_D / 2, SHELF_Z - SHELF_T) * Box(WIDTH, SHELF_D, SHELF_T,
                                                       align=(Align.CENTER, Align.CENTER, Align.MIN))
    # 45 deg wedge lip at the shelf tip (no overhang when printed back-down)
    lip = extrude(Plane.YZ * Polygon((SHELF_D - LIP_H, SHELF_Z), (SHELF_D, SHELF_Z),
                                     (SHELF_D, SHELF_Z + LIP_H), align=None), WIDTH / 2, both=True)
    gus = extrude(Plane.YZ * Polygon((PLATE_T, SHELF_Z - SHELF_T), (PLATE_T + GUSSET, SHELF_Z - SHELF_T),
                                     (PLATE_T, SHELF_Z - SHELF_T - GUSSET), align=None), WIDTH / 2, both=True)
    part = plate + shelf + lip + gus
    for x in (-SLOT_X, SLOT_X):
        u = (Cylinder(SLOT_W / 2, 30, align=(Align.CENTER, Align.CENTER, Align.MAX))
             + Pos(0, SLOT_DEPTH, 0) * Box(SLOT_W, 2 * SLOT_DEPTH, 30, align=(Align.CENTER, Align.CENTER, Align.MAX)))
        part -= Pos(x, SHELF_D - SLOT_DEPTH + SLOT_W / 2, SHELF_Z + LIP_H + 1) * u
    # countersunk screw holes in the plate, below and above the shelf
    for z in (12.0, PLATE_H - 9.0):
        part -= Pos(0, PLATE_T, z) * Rot(-90, 0, 0) * bolt_hole(SCREW, PLATE_T + 1, head="csk")
    return part
