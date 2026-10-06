"""seed-tray-dibber: press plate with a handle that punches 24 sowing holes in a seed tray.

Spec: 6 x 4 pegs at 40 mm pitch (a 24-cell tray, 240 x 160 mm), each Ø8 mm and 10 mm deep with
a 45° point. The pegs sit on a light, stiff grid of 10 x 8 mm bars (rows, columns, a centre
spine and a perimeter frame); the flat underside of the grid is the depth stop. A D-handle
(grip 190 mm long) bolts onto the spine with 2 x M4 so one press makes all 24 holes.
2 parts printed together in print poses: plate upside down (bars' top on the bed, pegs up), and
the handle lying on its side so its layers run along the grip (strong). Model coordinates are
therefore print poses. Fits the 300 x 320 plate.
Material: AzureFilm ABS PLUS. ABS+ yellows/embrittles after a season or two in full sun; the
user's "AzureFilm ASA @BBL H2C 0.4 nozzle" preset is the long-life swap (same geometry).

Assumptions:
- Tray: 24 cells, 4 x 6 at 40 mm pitch (COLS, ROWS, PITCH params); cell centres line up with
  the pegs when the plate edge is aligned with the tray edge.
- Peg depth 10 mm measured from the grid underside; Ø8 mm.
- Handle feet: M4 x 20 socket screws from the soil side (counterbored flush) into M4 nuts slid
  into side slots in the feet.
"""

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

COLS = 6
ROWS = 4
PITCH = 40.0
PEG_D = 8.0
PEG_DEPTH = 10.0
PEG_TIP = 3.0          # 45° cone length at the tip
BAR_W = 10.0
BAR_H = 8.0
FRAME_W = 6.0
# handle
GRIP_LEN = 190.0
GRIP_T = 20.0          # grip bar height
HANDLE_W = 22.0        # handle thickness (along tray Y)
HANDLE_H = 62.0        # plate top to grip top
FOOT_X = 80.0          # foot centres ±
FOOT_W = 26.0
OPENING_H = HANDLE_H - GRIP_T
EDGE_CHAMFER = 2.0
BOLT = "M4"
BOLT_LEN = 20.0
CBORE_D = 8.0
CBORE_DEPTH = 4.0
NUT_Z = 12.0           # nut slot height above the foot bottom

W = COLS * PITCH
D = ROWS * PITCH


def plate_in_use() -> Part:
    """Grid + pegs, in-use pose: grid underside at z = 0, pegs pointing down."""
    xs = [(i - (COLS - 1) / 2) * PITCH for i in range(COLS)]
    ys = [(j - (ROWS - 1) / 2) * PITCH for j in range(ROWS)]
    outer = Box(W, D, BAR_H, align=ON_BED)
    grid = outer - Box(W - 2 * FRAME_W, D - 2 * FRAME_W, 3 * BAR_H)
    for x in xs:
        grid += Pos(x, 0, 0) * Box(BAR_W, D, BAR_H, align=ON_BED)
    for y in ys + [0.0]:
        grid += Pos(0, y, 0) * Box(W, BAR_W, BAR_H, align=ON_BED)
    peg = Cylinder(PEG_D / 2, PEG_DEPTH - PEG_TIP + 0.01, align=(Align.CENTER, Align.CENTER, Align.MAX))
    peg += Pos(0, 0, -(PEG_DEPTH - PEG_TIP)) * Cone(0.5, PEG_D / 2, PEG_TIP, align=(Align.CENTER, Align.CENTER, Align.MAX))
    for x in xs:
        for y in ys:
            grid += Pos(x, y, 0) * peg
    # bolt holes for the handle feet, counterbored from the soil side
    for sx in (-1, 1):
        grid -= Pos(sx * FOOT_X, 0, BAR_H) * pin_hole(clearance(4.0, "loose"), BAR_H + 1)
        grid -= Pos(sx * FOOT_X, 0, CBORE_DEPTH) * pin_hole(CBORE_D, CBORE_DEPTH + 1)
    return grid


def handle_in_use() -> Part:
    """D-handle, in-use pose: feet on z = 0 (plate top), grip along X, thickness along Y."""
    half = GRIP_LEN / 2
    prof = Polygon((-half, OPENING_H), (-FOOT_X - FOOT_W / 2, OPENING_H - 6), (-FOOT_X - FOOT_W / 2, 0),
                   (-FOOT_X + FOOT_W / 2, 0), (-FOOT_X + FOOT_W / 2, OPENING_H - 10),
                   (-FOOT_X + FOOT_W / 2 + 10, OPENING_H), (FOOT_X - FOOT_W / 2 - 10, OPENING_H),
                   (FOOT_X - FOOT_W / 2, OPENING_H - 10), (FOOT_X - FOOT_W / 2, 0), (FOOT_X + FOOT_W / 2, 0),
                   (FOOT_X + FOOT_W / 2, OPENING_H - 6), (half, OPENING_H), (half, HANDLE_H), (-half, HANDLE_H),
                   align=None)
    part = extrude(Plane.XZ * prof, HANDLE_W / 2, both=True)
    part = chamfer(part.edges().filter_by(Axis.Y, reverse=True).group_by(Axis.Y)[-1], EDGE_CHAMFER)
    part = chamfer(part.edges().filter_by(Axis.Y, reverse=True).group_by(Axis.Y)[0], 0.4)
    nut = METRIC[BOLT]
    for sx in (-1, 1):
        # vertical bolt hole; teardrop with its tip toward +Y (up when printed on its side)
        tear = Rot(0, 0, -90) * Rot(0, -90, 0) * teardrop_hole(clearance(4.0, "loose"), 2 * NUT_Z + 12, along="X")
        part -= Pos(sx * FOOT_X, 0, 0) * tear
        # side slot (open to +Y) for the nut
        part -= Pos(sx * FOOT_X, 0, NUT_Z) * Box(nut["nut_af"] + 0.4, HANDLE_W, nut["nut_h"] + 0.4,
                                                 align=(Align.CENTER, Align.MIN, Align.CENTER))
    return part


def build():
    plate = Rot(180, 0, 0) * plate_in_use()
    plate = Pos(0, 0, -plate.bounding_box().min.Z) * plate
    handle = Rot(90, 0, 0) * handle_in_use()         # +Y face (nut slots) up, other face on the bed
    bb = handle.bounding_box()
    handle = Pos(0, D / 2 + 10 - bb.min.Y, -bb.min.Z) * handle
    return [plate, handle]
