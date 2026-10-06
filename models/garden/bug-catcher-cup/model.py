"""bug-catcher-cup: hand-held stink-bug catcher cup with a slide-in card lid.

Spec: cup 75 mm OD x 90 mm tall, 2.4 mm walls, closed top, mouth at z=0 (cup mouth-down in use).
The mouth has a 45 deg dovetail slot (along Y); a separate 1.6 mm card lid slides in the slot, so
you can cup a bug on a wall, slide the card under it and carry it away. Both parts print together,
cup flipped (closed top on the bed, mouth up): flare, dovetail and lid all self-support at 45 deg.
Assumptions: lid is pushed in from either Y end by thumb (no stop); slot clearance 0.25 mm per side;
lid card 84 x 84 mm at its narrow face, wide face 87.2 mm; flange R52 mm gives dovetail walls
for ~55 mm of lid edge. Lid is placed beside the cup, same orientation as in the slot.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(180, 0, 0),  # closed top on the bed, mouth up
    supports="off",
    brim="auto",
)

# Parameters
CUP_OD = 75.0
CUP_H = 90.0
WALL = 2.4
LID_T = 1.6
CLR = 0.25
SLOT_H = LID_T + CLR          # dovetail slot depth (z 0..SLOT_H)
FLANGE_R = 52.0
LID_HALF = 42.0               # lid half width at its narrow (wall-side) face
LID_LEN = 84.0
LID_GAP = 20.0                # gap between parts on the bed

R_O = CUP_OD / 2
R_I = R_O - WALL
FLARE_H = FLANGE_R - R_O      # 45 deg flare keeps the flange print-supported


def trap(half, h, length):
    """Dovetail prism: half-width `half` at z=0, widening 45 deg to z=h; along Y."""
    p = Polygon((-half, 0), (half, 0), (half + h, h), (-half - h, h), align=None)
    return extrude(Plane.XZ * p, amount=length / 2, both=True)


def build():
    prof = Polygon(
        (0, 0), (FLANGE_R, 0), (FLANGE_R, SLOT_H), (R_O, SLOT_H + FLARE_H),
        (R_O, CUP_H), (0, CUP_H), align=None,
    )
    cup = revolve(Plane.XZ * prof, Axis.Z, 360)
    cup = chamfer(cup.edges().group_by(Axis.Z)[-1], 0.4)
    cup -= Pos(0, 0, SLOT_H) * Cylinder(R_I, CUP_H - WALL - SLOT_H, align=ON_BED)
    cup -= trap(LID_HALF + CLR, SLOT_H, 2 * FLANGE_R + 10)

    lid = trap(LID_HALF, LID_T, LID_LEN)
    lid = Pos(FLANGE_R + LID_HALF + LID_T + LID_GAP, 0, CUP_H - LID_T) * lid  # lands on bed after flip
    return [cup, lid]
