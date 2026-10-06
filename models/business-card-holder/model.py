"""business-card-holder: desk holder for 50 business cards (90 x 55 mm), angled front, thumb notch.

Spec: side profile (Y-Z) extruded along X and closed by two end walls. The card pocket is tilted back
TILT deg with its floor perpendicular to the cards, so the stack settles against the back rest.
Low front lip with a 60 deg sloped (angled) face and a U thumb notch in the middle to slide the front
card up. Long base foot behind the back rest keeps it from tipping back.
Prints in use orientation, no supports (all faces <= 45 deg from vertical, notch opens upward).

MEASURE BEFORE PRINTING: business card 90 x 55 mm (EU), ~0.35 mm thick -> 50 cards ~17.5 mm.
Assumptions: standard 300-350 gsm cards; ~2 g per card for the load audit.
Hardware: none (optional 4 rubber feet 8 mm).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 22, 30), grams=100)],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="auto",
)

# Parameters
CARD_W, CARD_H, CARD_T = 90.0, 55.0, 0.35
CARDS_N = 50
CLEAR_X = 2.0              # card width clearance, total
STACK_EXTRA = 2.5          # free play in the stack depth
TILT = 15.0                # deg back from vertical
FLOOR = 3.0                # minimum floor
END_WALL = 3.0
BACK_T = 3.0
BACK_H_OVER_FLOOR = 38.0   # back rest height above the pocket floor
LIP_H_OVER_FLOOR = 12.0    # front lip height above the pocket floor
FRONT_SLOPE = 60.0         # deg from horizontal, angled front face
LIP_TOP_W = 2.4            # flat on top of the lip
FOOT_EXTRA = 6.0           # base reach behind the back-rest top
THUMB_R = 13.0             # thumb notch radius

POCKET_T = CARDS_N * CARD_T + STACK_EXTRA
IN_X = CARD_W + CLEAR_X
OUT_X = IN_X + 2 * END_WALL


def _profile_pts():
    a = math.radians(TILT)
    up = (math.sin(a), math.cos(a))          # along the cards
    nrm = (math.cos(a), -math.sin(a))        # through the stack, towards the back
    z0 = FLOOR + POCKET_T * math.sin(a)      # pocket front-bottom height
    z_lip = z0 + LIP_H_OVER_FLOOR
    # front face from (0,0) up to the lip top
    y_lip_front = z_lip / math.tan(math.radians(FRONT_SLOPE))
    y_front_line_at_lip = y_lip_front + LIP_TOP_W
    y0 = y_front_line_at_lip - (z_lip - z0) * math.tan(a)  # pocket front line through (y0, z0)
    F0 = (y0, z0)
    B0 = (y0 + POCKET_T * nrm[0], z0 + POCKET_T * nrm[1])

    def line_y(p, z):                        # y on a tilted line through p at height z
        return p[0] + (z - p[1]) * math.tan(a)

    z_back = z0 + BACK_H_OVER_FLOOR
    back_out = (B0[0] + BACK_T / math.cos(a), B0[1])
    D = line_y(back_out, z_back) + FOOT_EXTRA
    solid = [(0, 0), (D, 0), (D, FLOOR), (line_y(back_out, FLOOR), FLOOR),
             (line_y(back_out, z_back), z_back), (line_y(B0, z_back), z_back),
             (line_y(F0, z_lip), z_lip), (y_lip_front, z_lip)]
    far = 100
    pocket = [F0, B0, (B0[0] + far * up[0], B0[1] + far * up[1]), (F0[0] + far * up[0], F0[1] + far * up[1])]
    return solid, pocket, z_lip, D


def build() -> Part:
    solid, pocket, z_lip, depth = _profile_pts()
    body = extrude(Plane.YZ.offset(-OUT_X / 2) * Polygon(*solid, align=None), OUT_X)
    cut = extrude(Plane.YZ.offset(-IN_X / 2) * Polygon(*pocket, align=None), IN_X)
    body -= cut
    body = chamfer(body.edges().group_by(Axis.Z)[0], 0.4)
    # thumb notch through the front lip (horizontal axis along Y, opens upward)
    body -= Pos(0, 0, z_lip + THUMB_R * 0.35) * Pos(0, -1, 0) * Rot(90, 0, 0) * Cylinder(THUMB_R, solid[6][0] + 2, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return Pos(0, -depth / 2, 0) * body
