"""bed-slat-holder: replacement cup clip that holds a bed slat end on a bed frame side rail.

Spec: screwed to the vertical inside face of the side rail (y=0 face against the rail) with
2 countersunk wood screws through side wings. The slat end drops in from above into a U-cup
(floor + two side walls, open top and open toward the bed centre). Slat 65 x 8 mm.
Rated for 40 kg per clip (people on the bed), load on the cup floor.

Strength: printed in use orientation (flat bottom on the bed). The floor cantilever and the
side walls (which act as deep beams) carry the bending stress along Y, i.e. along the layers;
the wings transfer the screw pull to the cup in X, also along the layers.

Assumptions:
- Rail inside face is flat and vertical; clip top is flush with the slat side-wall top, so
  nothing protrudes above the slat (mattress side).
- Slat width/thickness vary in wood: pocket has SLAT_W_GAP / SLAT_T_GAP extra clearance.
- Screws: 4 x 25-30 mm countersunk wood screws (e.g. DIN 7997 / chipboard), 90 deg head,
  head dia ~8 mm. 2 per clip, 8 per set of 4.
- Material ABS (AzureFilm ABS PLUS), quality "strong".
"""

from build123d import *

from cadlib import *

# Parameters - slat
SLAT_W = 65.0          # slat width (X)
SLAT_T = 8.0           # slat thickness (Z)
SLAT_W_GAP = 1.0       # total extra pocket width (wood tolerance)
SLAT_T_GAP = 1.0       # side walls rise this much above the slat top
SEAT_D = 35.0          # how far the slat end sits in the cup (Y)

# Parameters - body
FLOOR_T = 5.0          # cup floor thickness (load bearing)
SIDE_T = 4.0           # cup side wall thickness
BACK_T = 6.0           # back plate / wing thickness (holds countersink)
WING_W = 15.0          # screw wing width beyond each side wall
CORNER_R = 2.0         # vertical edge rounding

# Parameters - screws (countersunk wood screw)
SCREW_D = 4.0
SCREW_CLEAR_D = SCREW_D + 2 * FIT["loose"] + 0.1   # 4.9 shank clearance (teardrop)
CSK_D = 8.6            # countersink diameter at the wing front face (8 mm head + clearance)

POCKET_W = SLAT_W + SLAT_W_GAP
POCKET_H = SLAT_T + SLAT_T_GAP
TOTAL_H = FLOOR_T + POCKET_H
CUP_W = POCKET_W + 2 * SIDE_T
TOTAL_W = CUP_W + 2 * WING_W
SCREW_X = CUP_W / 2 + WING_W / 2
SCREW_Z = TOTAL_H / 2

# Coordinates = in-use orientation, Z up, mm. y=0 is the face against the rail.
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,            # screwed to the rail
    loads=[dict(at=(0, BACK_T + SEAT_D / 2, FLOOR_T), grams=40000)],
    print_orientation=(0, 0, 0),  # flat as used: bending stress runs along the layers
    supports="off",
    brim="auto",
    copies=4,
)


def build() -> Part:
    back = Pos(0, BACK_T / 2, 0) * rounded_box(TOTAL_W, BACK_T, TOTAL_H, radius=CORNER_R)
    cup = Pos(0, BACK_T / 2 + (SEAT_D + BACK_T) / 2 - BACK_T / 2, 0) * rounded_box(
        CUP_W, SEAT_D + BACK_T, TOTAL_H, radius=CORNER_R
    )
    part = back + cup

    # slat pocket: open on top and toward the bed centre (+Y)
    pocket = Pos(0, BACK_T + SEAT_D, FLOOR_T) * Box(
        POCKET_W, 2 * SEAT_D, POCKET_H + 1, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    part = part - pocket

    # countersunk screw holes through the wings, axis Y, head on the +Y face
    csk_h = (CSK_D - SCREW_CLEAR_D) / 2
    for sx in (-SCREW_X, SCREW_X):
        shank = Pos(sx, BACK_T / 2, SCREW_Z) * teardrop_hole(SCREW_CLEAR_D, BACK_T * 3, along="Y")
        cone = Pos(sx, BACK_T, SCREW_Z) * Rot(90, 0, 0) * Cone(
            CSK_D / 2, SCREW_CLEAR_D / 2, csk_h, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
        relief = Pos(sx, BACK_T, SCREW_Z) * Rot(-90, 0, 0) * Cylinder(
            CSK_D / 2, 2, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
        part = part - shank - cone - relief
    return part
