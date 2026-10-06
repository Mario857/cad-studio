"""bill-presenter-tray: 200x120 mm restaurant bill tray with push-on receipt clip and coin well.

Spec: tray 200x120x18 mm, 10 mm corner radius, 3 mm rim walls, 10 mm deep pocket for notes,
card and receipt. Right end: Ø60 coin well sunk 6 mm below the pocket floor with a 5 mm scooped
edge so coins slide out. Receipt clip: separate U-clip (printed beside the tray, lying on its side
so the legs flex along the layers) that pushes over the left end rim; the receipt is pinched
between the clip's inner leg (with a pressure bump) and the rim.

MEASURE BEFORE PRINTING: none critical (receipts 57/80 mm wide fit under the 30 mm clip).
Assumptions: clip grip = RIM_T - CLIP_PRELOAD so it holds a receipt or two without falling off;
tray is presented on a table (not free-standing load-bearing).
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="auto",
)

# Parameters
TRAY_L = 200.0
TRAY_W = 120.0
TRAY_H = 18.0
CORNER_R = 10.0
RIM_T = 3.0              # side walls; the clip pushes over the left-end wall
POCKET_DEPTH = 10.0
TOP_ROUND = 1.0          # rounded top lip
COIN_D = 60.0
COIN_DEPTH = 6.0         # below the pocket floor
COIN_SCOOP_R = 5.0
COIN_X = 55.0            # coin well centre from tray centre
CLIP_W = 30.0            # clip width along the rim (print height)
CLIP_T = 2.5             # leg thickness
CLIP_PRELOAD = 0.3       # gap = RIM_T - preload (paper adds ~0.1 mm per receipt)
CLIP_IN_LEG = 22.0       # inner leg length (down into the pocket)
CLIP_OUT_LEG = 14.0      # outer leg length
BUMP_R = 1.2             # pressure bump on the inner leg tip


def _tray() -> Part:
    tray = rounded_box(TRAY_L, TRAY_W, TRAY_H, radius=CORNER_R)
    pocket = rounded_box(TRAY_L - 2 * RIM_T, TRAY_W - 2 * RIM_T, POCKET_DEPTH + 1, radius=CORNER_R - RIM_T, bottom_chamfer=0)
    pocket = fillet(pocket.edges().group_by(Axis.Z)[0], 2.0)
    tray -= Pos(0, 0, TRAY_H - POCKET_DEPTH) * pocket
    tray = fillet(tray.edges().group_by(Axis.Z)[-1], TOP_ROUND)
    well = Cylinder(COIN_D / 2, COIN_DEPTH + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    well = fillet(well.edges().group_by(Axis.Z)[0], COIN_SCOOP_R)
    tray -= Pos(COIN_X, 0, TRAY_H - POCKET_DEPTH - COIN_DEPTH) * well
    return tray


def _clip() -> Part:
    gap = RIM_T - CLIP_PRELOAD
    # U profile in XY (print lying on its side), opening toward -Y; bending in-plane = along layers
    outer_w = gap + 2 * CLIP_T
    bridge = Pos(0, CLIP_T / 2, 0) * Box(outer_w, CLIP_T, CLIP_W, align=(Align.CENTER, Align.CENTER, Align.MIN))
    leg_in = Pos(-(gap + CLIP_T) / 2, -CLIP_IN_LEG / 2, 0) * Box(CLIP_T, CLIP_IN_LEG, CLIP_W, align=(Align.CENTER, Align.CENTER, Align.MIN))
    leg_out = Pos((gap + CLIP_T) / 2, -CLIP_OUT_LEG / 2, 0) * Box(CLIP_T, CLIP_OUT_LEG, CLIP_W, align=(Align.CENTER, Align.CENTER, Align.MIN))
    bump = Pos(-gap / 2 - BUMP_R * 0.4, -CLIP_IN_LEG + 3, 0) * Cylinder(BUMP_R, CLIP_W, align=(Align.CENTER, Align.CENTER, Align.MIN))
    clip = bridge + leg_in + leg_out + bump
    clip = chamfer(clip.edges().group_by(Axis.Z)[0], 0.4)
    return Pos(-TRAY_L / 2 + 40, -TRAY_W / 2 - 30, 0) * clip


def build():  # 2 bodies intended: tray + separate receipt clip
    return [_tray(), _clip()]
