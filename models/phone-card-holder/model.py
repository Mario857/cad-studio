"""phone-card-holder: stick-on card holder for the back of a phone case, 2 cards, <= 4 mm thick.

Spec: flat base (adhesive face at z=0) with a dovetail pocket: the pocket walls lean in at 45 deg,
so the top lip overlaps the card edges by ~1.5 mm on three sides while the part prints flat with no
supports. The face is an open window: push the cards out of the open +X end with the thumb (thumb
slot = window + scoop at the open end). Card long axis along the phone's long axis.

MEASURE BEFORE PRINTING: bank card 85.6 x 54 x 0.76 mm; phone back width must be >= OUT_W (58 mm).
Assumptions: phone case back is flat over the holder area; 2 flat cards; total thickness excludes the
tape. Base and lip are 1.0 mm (not 1.2) to keep the part <= 4 mm thick, and the 45 deg dovetail
lip edge tapers locally to ~0.8 mm - audit WARN accepted.
Hardware: 3M VHB double-sided tape (e.g. 4910/5952), ~50 x 80 mm, or 2 strips 15 mm wide.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # adhesive face on the bed (flattest face for the tape)
    supports="off",
    brim="on",                    # large thin flat ABS part
)

# Parameters
CARD_L, CARD_W, CARD_T = 85.6, 54.0, 0.76
CARDS = 2
CLEAR_L = 0.6           # length clearance
CLEAR_W = 0.8           # width clearance, total
CLEAR_T = 0.4           # stack clearance, total
BASE_T = 1.0            # adhesive base
LIP_T = 1.0             # top lip thickness
RAIL_W = 1.6            # solid rail beside the pocket (at pocket floor)
CORNER_R = 4.0          # outer corner radius
TOP_R = 0.6             # top edge round
THUMB_R = 12.0          # thumb scoop through the lip at the open end

POCKET_L = CARD_L + CLEAR_L
POCKET_W = CARD_W + CLEAR_W
POCKET_H = CARDS * CARD_T + CLEAR_T
OUT_L = POCKET_L + RAIL_W
OUT_W = POCKET_W + 2 * RAIL_W
OUT_H = BASE_T + POCKET_H + LIP_T
assert OUT_H <= 4.0


def build() -> Part:
    body = rounded_box(OUT_L, OUT_W, OUT_H, radius=CORNER_R, top_radius=TOP_R)
    x0 = -OUT_L / 2 + RAIL_W                 # closed end of the pocket floor
    ext = 30.0                               # pocket runs out through the open end
    z0, z1 = BASE_T, BASE_T + POCKET_H
    bot = Plane.XY.offset(z0) * Pos(x0 + (POCKET_L + ext) / 2, 0) * Rectangle(POCKET_L + ext, POCKET_W)
    top_l = POCKET_L + ext - POCKET_H
    top_w = POCKET_W - 2 * POCKET_H
    top = Plane.XY.offset(z1) * Pos(x0 + POCKET_H + top_l / 2, 0) * Rectangle(top_l, top_w)
    body -= loft([bot, top])                 # 45 deg dovetail pocket
    # window through the lip
    body -= Pos(x0 + POCKET_H + top_l / 2, 0, z1 - 0.01) * Box(top_l, top_w, LIP_T + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # thumb scoop at the open end, through the lip only
    body -= Pos(OUT_L / 2, 0, z1 - 0.01) * Cylinder(THUMB_R, LIP_T + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return body
