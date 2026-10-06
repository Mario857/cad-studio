"""controller-stand: desk / TV-unit stand for 2 game controllers + a headset hook on top.

Spec: wide base plate; a central spine with reclined backrest faces carries one controller
on each side (left and right), each stood upright on its grips in a trough, face pointing
outward, leaning back against the spine and kept from sliding by an outer lip. A mast rises
from the spine to a saddle-shaped headset hook; the headband lies across the saddle so the
earcups hang in front of and behind the mast, clear of both controllers.
Loads for the tip-over audit: headset 350 g on the hook, 2 x 280 g controllers.

Assumptions:
- Controllers: PS5 DualSense (160 x 66 x 106 mm) or Xbox (153 x 61 x 102 mm). The trough is
  sized for the grip bottoms (CRADLE_SLOT 62 mm between backrest and lip at the floor, CRADLE_LEN
  140 mm along the controller width); controllers may overhang the trough ends.
- Headset: band-to-earcup-bottom ~200 mm, band width <= 60 mm; hook top at 300 mm keeps the
  earcups (which hang front/back of the mast, |x| < 45 mm) above the desk and away from controllers.
- Material ABS+; mast 24 x 30 mm solid section is ample for a 350 g headset.
"""

import math

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm. The audit picks the print orientation.
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[
        dict(at=(0, 0, 300), grams=350),     # headset on hook
        dict(at=(-62, 0, 60), grams=280),    # left controller
        dict(at=(62, 0, 60), grams=280),     # right controller
    ],
    print_orientation="auto",
    supports="auto",
    brim="auto",
)

# Parameters
BASE_W = 250.0          # X
BASE_D = 180.0          # Y
BASE_H = 5.0
BASE_R = 12.0           # corner radius

SPINE_T_TOP = 24.0      # spine/backrest thickness at top (X)
SPINE_H = 90.0          # backrest height above base
RECLINE_DEG = 12.0      # controller lean-back angle
CRADLE_LEN = 140.0      # spine / lip length along Y (controller width direction)
CRADLE_SLOT = 62.0      # floor gap between backrest foot and lip (controller thickness at grips)
LIP_T = 6.0
LIP_H = 18.0

MAST_X = 24.0
MAST_Y = 30.0
HOOK_TOP = 300.0        # top of headset saddle
SADDLE_LEN_X = 80.0     # along X (headband width direction)
SADDLE_W_Y = 60.0       # across Y (headband curvature)
SADDLE_H = 40.0         # saddle height incl. 45 deg flare
SADDLE_TOP_R = 12.0     # rounding of the saddle's top edges


def _xz_extrude(pts, length):
    """Polygon in XZ (x, z) extruded symmetrically along Y."""
    return extrude(Plane.XZ * Polygon(*pts, align=None), length / 2, both=True)


def _yz_extrude(pts, length):
    """Polygon in YZ (y, z) extruded symmetrically along X."""
    return extrude(Plane.YZ * Polygon(*pts, align=None), length / 2, both=True)


def build() -> Part:
    base = rounded_box(BASE_W, BASE_D, BASE_H, radius=BASE_R, bottom_chamfer=0.4)

    # spine: trapezoid in XZ -> reclined backrest faces on both sides
    z0, z1 = BASE_H, BASE_H + SPINE_H
    half_top = SPINE_T_TOP / 2
    half_bot = half_top + SPINE_H * math.tan(math.radians(RECLINE_DEG))
    spine = _xz_extrude([(-half_bot, z0 - 0.5), (half_bot, z0 - 0.5), (half_top, z1), (-half_top, z1)],
                        CRADLE_LEN)

    # outer lips, 45 deg chamfer on the outer top edge
    lip_x = half_bot + CRADLE_SLOT
    lips = []
    for s in (-1, 1):
        pts = [(lip_x, z0 - 0.5), (lip_x + LIP_T, z0 - 0.5), (lip_x + LIP_T, z0 + LIP_H - 3),
               (lip_x + LIP_T - 3, z0 + LIP_H), (lip_x, z0 + LIP_H)]
        lips.append(_xz_extrude([(s * x, z) for x, z in pts], CRADLE_LEN))

    # mast
    mast_bot = z1 - 1
    saddle_bot = HOOK_TOP - SADDLE_H
    mast = Pos(0, 0, mast_bot) * Box(MAST_X, MAST_Y, saddle_bot - mast_bot + 1,
                                     align=(Align.CENTER, Align.CENTER, Align.MIN))

    # saddle: YZ profile (45 deg flare) intersected with XZ profile (45 deg flare)
    flare_y = (SADDLE_W_Y - MAST_Y) / 2
    zf = saddle_bot + flare_y
    yz = _yz_extrude([(-MAST_Y / 2, saddle_bot), (MAST_Y / 2, saddle_bot), (SADDLE_W_Y / 2, zf),
                      (SADDLE_W_Y / 2, HOOK_TOP), (-SADDLE_W_Y / 2, HOOK_TOP), (-SADDLE_W_Y / 2, zf)],
                     SADDLE_LEN_X)
    flare_x = (SADDLE_LEN_X - MAST_X) / 2
    xz = _xz_extrude([(-MAST_X / 2, saddle_bot), (MAST_X / 2, saddle_bot),
                      (SADDLE_LEN_X / 2, saddle_bot + flare_x), (SADDLE_LEN_X / 2, HOOK_TOP),
                      (-SADDLE_LEN_X / 2, HOOK_TOP), (-SADDLE_LEN_X / 2, saddle_bot + flare_x)],
                     SADDLE_W_Y)
    saddle = yz & xz
    # round the top long edges (along X) so the headband sits on a curve
    top_edges = saddle.edges().group_by(Axis.Z)[-1].filter_by(Axis.X)
    saddle = fillet(top_edges, SADDLE_TOP_R)

    return base + spine + lips[0] + lips[1] + mast + saddle
