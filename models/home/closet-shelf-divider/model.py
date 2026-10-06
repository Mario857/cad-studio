"""closet-shelf-divider: slide-on vertical divider that keeps sweater stacks apart on a closet shelf.

Spec: a C-shaped clip grips the shelf's front edge (top flange on the shelf, web across the
front edge, short jaw underneath) and carries a 200 mm tall vertical plate that runs back
along the shelf depth. Slide it onto the shelf from the front; the snug fit keeps it in place.
Printed as a set of 2 (META copies=2), lying on the plate face (load in bending runs along
layers, zero supports).

Coordinates: Y = into the shelf (shelf front edge at y=0), Z up, X = across the shelf.
Plate occupies x = 0..PLATE_T; clip flanges extend to +X (JAW_W).

Assumptions:
- Shelf thickness 18 mm (typical melamine/MDF); gap = clearance(SHELF_T, "snug") = 18.3 mm.
- Shelf front edge is square and unobstructed (no lip/face frame deeper than WEB_T).
- Plate depth 130 mm (along the shelf) so two copies fit the bed together; 200 mm tall
  above the shelf top.
- Hardware: none.
"""

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm. The audit picks the print orientation.
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,            # clamped on the shelf edge, not free-standing
    loads=[],
    print_orientation=(0, -90, 0),  # plate face (x=0) on the bed: no supports, strong in bending
    supports="off",
    brim="auto",
    copies=2,
)

# Parameters
SHELF_T = 18.0          # shelf thickness
FIT = "snug"            # clip fit on the shelf
GAP = clearance(SHELF_T, FIT)
HEIGHT = 200.0          # plate height above the shelf top
DEPTH = 130.0           # plate length along the shelf depth
PLATE_T = 4.0           # divider plate thickness
JAW_W = 40.0            # clip width across the shelf (X)
TOP_T = 4.0             # top flange thickness (sits on the shelf)
BOT_T = 4.0             # bottom jaw thickness (under the shelf)
BOT_LEN = 60.0          # bottom jaw length under the shelf
WEB_T = 4.0             # web across the shelf front edge
CORNER_R = 25.0         # rounded top-back corner of the plate
RIB_H = 30.0            # gusset height on the plate
RIB_T = 3.0             # gusset thickness
RIB_Y = (15.0, 65.0, 115.0)
LEAD_IN = 1.5           # entry chamfer on the jaw tips
EF = 0.4                # elephant-foot chamfer on the bed face

SHELF_TOP = BOT_T + GAP


def build() -> Part:
    # Divider plate (x 0..PLATE_T), from the shelf top up HEIGHT
    plate = Pos(0, 0, SHELF_TOP) * Box(PLATE_T, DEPTH, HEIGHT, align=(Align.MIN, Align.MIN, Align.MIN))
    top_back = plate.edges().filter_by(Axis.X).group_by(Axis.Z)[-1].sort_by(Axis.Y)[-1]
    plate = fillet(top_back, CORNER_R)

    flange = Pos(0, 0, SHELF_TOP) * Box(JAW_W, DEPTH, TOP_T, align=(Align.MIN, Align.MIN, Align.MIN))
    jaw = Box(JAW_W, BOT_LEN, BOT_T, align=(Align.MIN, Align.MIN, Align.MIN))
    web = Pos(0, -WEB_T, 0) * Box(JAW_W, WEB_T, SHELF_TOP + TOP_T, align=(Align.MIN, Align.MIN, Align.MIN))

    part = plate + flange + jaw + web

    for y in RIB_Y:
        part += Pos(PLATE_T, y, SHELF_TOP + TOP_T) * rib(JAW_W - PLATE_T - 2, RIB_H, RIB_T)

    # Lead-in chamfer on the bottom jaw tip (inner top edge) to ease sliding on
    tip = part.edges().filter_by(Axis.X).filter_by_position(Axis.Y, BOT_LEN - 0.01, BOT_LEN + 0.01)
    tip = tip.filter_by_position(Axis.Z, BOT_T - 0.01, BOT_T + 0.01)
    part = chamfer(tip, LEAD_IN)

    # Elephant-foot chamfer around the bed face (x = 0 in model coords)
    bed_face = part.faces().sort_by(Axis.X)[0]
    part = chamfer(bed_face.edges(), EF)
    return part
