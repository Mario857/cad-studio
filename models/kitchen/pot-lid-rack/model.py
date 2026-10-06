"""pot-lid-rack: cabinet-door rack holding 3 pot lids on edge.

Spec: back plate screwed to the inside of a kitchen cabinet door with 3 horizontal
ledges (U-channels) stacked 100 mm apart. Each lid stands on edge with its rim in a
channel and leans back; lids shingle (lower lid in front of the upper channel), so put
the largest lid on the bottom tier. 45 deg gussets under the upper ledges.
The whole part is one extruded YZ profile, printed lying on its side
(print_orientation rotates X to vertical) so every ledge's bending load runs along
the layers and there are no overhangs.
Assumptions: lids 18-28 cm, <= 600 g each, rim/edge <= 24 mm thick (glass lids with
silicone rim fit); 4 x 4 mm pan-head wood screws (holes 4.5 mm); door has >= 45 mm
clearance to the shelves when closed (rack depth 30 mm + lid).
"""

from build123d import *

from cadlib import *

# Parameters
WIDTH = 120.0          # along the door (X)
PLATE_T = 4.0
TIERS = 3
TIER_PITCH = 100.0
LEDGE_D = 30.0         # projection from the door
LEDGE_T = 4.0          # channel floor
LIP_T = 4.0
LIP_H = 18.0
GUSSET = 20.0          # 45 deg brace under ledges 2..n
TOP_MARGIN = 40.0
SCREW_D = 4.5
SCREW_X = 40.0
LID_G = 600

HEIGHT = (TIERS - 1) * TIER_PITCH + TOP_MARGIN + LIP_H

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[dict(at=(0, LEDGE_D / 2, i * TIER_PITCH + LEDGE_T), grams=LID_G) for i in range(TIERS)],
    print_orientation=(0, 90, 0),   # lie on the side: profile in the layer plane
    supports="auto",
    brim="on",  # 258 mm long contact strip + brim holds it; the 8 deg "wobbly on bed" warn is
                # accepted: on its side is the only orientation where ledges bend along layers
)


def profile() -> Sketch:
    pts = [(0, 0)]
    for i in range(TIERS):
        z = i * TIER_PITCH
        if i > 0:
            pts += [(PLATE_T, z - GUSSET), (GUSSET + PLATE_T, z)]
        pts += [(LEDGE_D, z), (LEDGE_D, z + LIP_H), (LEDGE_D - LIP_T, z + LIP_H),
                (LEDGE_D - LIP_T, z + LEDGE_T), (PLATE_T, z + LEDGE_T)]
    pts += [(PLATE_T, HEIGHT), (0, HEIGHT)]
    # bottom tier starts at z=0 with no gusset; first point (PLATE_T,0) is implied by ledge
    return Polygon(*pts, align=None)


def build() -> Part:
    part = extrude(Plane.YZ * profile(), WIDTH / 2, both=True)
    for z in [(i + 0.5) * TIER_PITCH for i in range(TIERS - 1)] + [HEIGHT - TOP_MARGIN / 2]:
        for x in (-SCREW_X, SCREW_X):
            # tip toward -X = up in the print orientation
            part -= Pos(x, 0, z) * Rot(0, -90, 0) * teardrop_hole(SCREW_D, 3 * PLATE_T, along="Y")
    return part
