"""cat-wall-shelf: wall-mounted cat climbing step with a recessed grip pad and big gussets.

Spec: 280 x 200 mm step top (12 mm plate) with a 2 mm deep recess for a carpet / cork pad,
an 8 mm back plate (140 mm tall) screwed to the wall with 4 countersunk wood screws, and
4 big triangular gussets (8 mm) under the top. Screw heads sit flush in the back plate below the
step, between the gussets, so they are hidden from above; drive them horizontally from the front
underneath the step. Design load 15 kg at the front edge (6 kg cat landing ~2.5x).

Print: wall face down on the bed (print_orientation (-90,0,0)). Strength reasoning: the highest
stress is bending of the back plate between the top screw row and the gusset roots (~7-8 MPa at
15 kg); printed wall-face-down that stress runs along the layers. The step plate / gusset tension
in the other direction is tiny (< 1 MPa) because the 140 mm deep gusset section carries it.
Support-free: gussets taper upward, the pad recess is a vertical face, countersinks open upward.

Pet safety: ABS must not hold food/water directly and is not a chew toy. All cat-touched edges
are rounded/chamfered (top perimeter 3 mm 45 deg chamfer = bed edge in print, other edges filleted).
Glue the pad into the recess (double-sided carpet tape); replace it when worn.

Hardware: 4x countersunk wood screws ~4.5-5 x 60 mm (head <= 10 mm) + matching wall anchors,
or screws straight into studs; 260 x 180 x ~2 mm carpet or cork pad.

Assumptions: wall at y = +DEPTH/2 (model back face), front edge at y = -DEPTH/2; screw holes
sized for M5-class countersunk heads (works for 4.5/5 mm wood screws); mount into studs or rated
anchors (each screw sees ~150 N pull-out at 15 kg front load).
"""

from build123d import *

from cadlib import *

# Parameters (mm)
WIDTH = 280.0          # along wall (X)
DEPTH = 200.0          # out from wall (Y)
TOP_T = 12.0           # step plate thickness
BACK_H = 140.0         # back plate total height (top of step = BACK_H)
BACK_T = 8.0           # back plate thickness
GUSSET_T = 8.0         # gusset thickness
GUSSET_DEPTH = 175.0   # how far gussets reach under the step (from wall)
GUSSET_X = (-131.0, -45.0, 45.0, 131.0)  # gusset centre lines
PAD_INSET = 10.0       # rim around the pad recess floor (8 mm at the top, 45 deg walls)
PAD_DEPTH = 2.0        # pad recess depth
PAD_R = 8.0            # pad recess corner radius
CORNER_R = 12.0        # plan-view corner radius of the top plate
EDGE_CHAMFER = 3.0     # top perimeter chamfer (bed edge in print)
BED_CHAMFER = 0.4      # elephant-foot chamfer on the wall face (bed in print)
FILLET_R = 2.0         # other cat-touched edges
SCREW = "M5"           # countersunk hole size class for ~4.5-5 mm wood screws
SCREW_X = (-88.0, 88.0)
SCREW_Z = (22.0, 100.0)

BACK_Y = DEPTH / 2                  # wall plane
FRONT_Y = -DEPTH / 2
TOP_Z0 = BACK_H - TOP_T

# Coordinates = in-use orientation, Z up, mm.
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,            # screwed to the wall
    loads=[dict(at=(0.0, FRONT_Y, BACK_H), grams=15000)],
    print_orientation=(-90, 0, 0),  # wall face on bed: back-plate bending runs along layers
    supports="off",
    brim="auto",
)


def build() -> Part:
    # top step plate
    # front corners rounded, wall-side corners square (they print on the bed)
    plan = RectangleRounded(WIDTH, DEPTH, CORNER_R) + Pos(0, DEPTH / 2 - CORNER_R) * Rectangle(
        WIDTH, 2 * CORNER_R
    )
    top = extrude(Plane.XY.offset(TOP_Z0) * plan, TOP_T)
    not_wall = lambda es: es.filter_by(lambda e: e.center().Y < BACK_Y - 0.1)
    top = chamfer(not_wall(top.edges().group_by(Axis.Z)[-1]), EDGE_CHAMFER)
    top = fillet(not_wall(top.edges().group_by(Axis.Z)[0]), FILLET_R)

    # back plate (against the wall)
    back = Pos(0, BACK_Y - BACK_T / 2, 0) * Box(
        WIDTH, BACK_T, TOP_Z0 + 1, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    back = fillet(back.edges().filter_by(Axis.Z), 2.0)
    back = chamfer(back.faces().sort_by(Axis.Y)[-1].edges(), BED_CHAMFER)

    part = top + back

    # gussets: right triangle, legs on the back plate and under the step
    y0 = BACK_Y - BACK_T + 0.5
    y1 = BACK_Y - GUSSET_DEPTH
    z1 = TOP_Z0 + 0.5
    tri = Polygon((y0, 0.0), (y0, z1), (y1, z1), align=None)
    for gx in GUSSET_X:
        part = part + extrude(Plane.YZ.offset(gx - GUSSET_T / 2) * tri, GUSSET_T)

    # countersunk screw holes: head at back-plate front face, shank toward the wall (+Y)
    face_y = BACK_Y - BACK_T
    for sx in SCREW_X:
        for sz in SCREW_Z:
            part = part - Pos(sx, face_y, sz) * Rot(90, 0, 0) * bolt_hole(SCREW, BACK_T + 2, head="csk")

    # grip pad recess, 45 deg walls (the front wall is a ceiling when printed wall-face-down)
    rw, rd, grow = WIDTH - 2 * PAD_INSET, DEPTH - 2 * PAD_INSET, PAD_DEPTH + 1
    recess = loft(
        [
            Plane.XY.offset(BACK_H - PAD_DEPTH) * RectangleRounded(rw, rd, PAD_R),
            Plane.XY.offset(BACK_H + 1) * RectangleRounded(rw + 2 * grow, rd + 2 * grow, PAD_R + grow),
        ]
    )
    return part - recess
