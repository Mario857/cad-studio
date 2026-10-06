"""soundbar-bracket: pair of wall-mounted L brackets that carry a soundbar under a TV.

Spec: vertical wall plate with 2 countersunk screw holes, horizontal arm on top whose length
fits the soundbar depth (SOUNDBAR_DEPTH, 60-110 mm, default 90), a front retaining lip so the
bar cannot slide off, a shallow recess on the arm top for a self-adhesive rubber pad, and a
full-width gusset under the arm (screws sit below it, driver reaches them straight on). Load 2 kg per bracket. Two identical brackets (copies=2).

Coordinates: wall at y=0, arm points +Y, bracket width along X, Z up.
Printed lying on its side (rot Y 90deg) so the L profile lies in the layer plane: the bending
load at the arm/plate corner runs along the layers, and the gusset/arm need no supports.

ASSUMPTIONS:
- Screws: M4 countersunk wood/plug screws (hole + 90deg countersink), 2 per bracket.
- Rubber pad: 20 x 60 mm, ~1 mm thick self-adhesive strip (recess 1.0 mm deep).
- "Shelf lip" = 10 mm high front lip on the arm that retains the soundbar.
- Brackets are 30 mm wide; mount them ~1/4 of the bar length in from each end.
"""

from build123d import *

from cadlib import *

# Parameters
SOUNDBAR_DEPTH = 90.0   # 60..110, soundbar front-to-back depth
WIDTH = 30.0            # bracket width (X)
PLATE_T = 6.0           # wall plate thickness (Y)
PLATE_H = 100.0         # wall plate height (Z)
ARM_T = 8.0             # arm thickness (Z)
ARM_CLEAR = 3.0         # extra arm length beyond soundbar depth
LIP_T = 4.0             # front lip thickness (Y)
LIP_H = 10.0            # lip height above arm top
GUSSET_T = WIDTH         # full-width gusset (support-free when printed on side)
GUSSET_DROP = 45.0      # gusset height below arm
GUSSET_REACH = 60.0     # gusset length along arm from plate face
SCREW = "M4"
SCREW_Z = (15.0, 40.0)  # screw hole heights (below gusset)
PAD_W = WIDTH + 2.0     # pad recess runs through full width (no ceiling when printed on side)
PAD_L = 62.0            # pad recess length (Y)
PAD_DEPTH = 1.0
LOAD_G = 2000

ARM_L = PLATE_T + SOUNDBAR_DEPTH + ARM_CLEAR + LIP_T  # total arm length from wall

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[dict(at=(0, PLATE_T + SOUNDBAR_DEPTH / 2, PLATE_H), grams=LOAD_G)],
    print_orientation=(0, 90, 0),  # lie on side: L profile in layer plane (strength)
    supports="auto",
    brim="auto",
    copies=2,
)


def _profile(gusset: bool):
    top = PLATE_H
    arm_bot = PLATE_H - ARM_T
    pts = [(0, 0), (PLATE_T, 0)]
    if gusset:
        pts += [(PLATE_T, arm_bot - GUSSET_DROP), (PLATE_T + GUSSET_REACH, arm_bot)]
    else:
        pts += [(PLATE_T, arm_bot)]
    pts += [
        (ARM_L, arm_bot),
        (ARM_L, top + LIP_H),
        (ARM_L - LIP_T, top + LIP_H),
        (ARM_L - LIP_T, top),
        (0, top),
    ]
    return Polygon(*pts, align=None)


def build() -> Part:
    # Plane.YZ: local x = +Y, local y = +Z, extrudes along +X
    body = extrude(Plane.YZ.offset(-WIDTH / 2) * _profile(False), WIDTH)
    gusset = extrude(Plane.YZ.offset(-GUSSET_T / 2) * _profile(True), GUSSET_T)
    part = body + gusset

    # Countersunk screw holes through the plate, heads on the +Y (front) face
    for z in SCREW_Z:
        part -= Pos(0, PLATE_T, z) * Rot(-90, 0, 0) * bolt_hole(SCREW, PLATE_T + 1, head="csk")

    # Rubber pad recess on arm top, centred on the soundbar seat
    seat_c = PLATE_T + (SOUNDBAR_DEPTH + ARM_CLEAR) / 2
    part -= Pos(0, seat_c, PLATE_H - PAD_DEPTH) * Box(PAD_W, PAD_L, PAD_DEPTH + 0.01, align=ON_BED)

    # Elephant-foot chamfer on the +X face, which sits on the bed after rot Y 90deg
    part = chamfer(part.faces().sort_by(Axis.X)[-1].edges(), 0.4)
    return part
