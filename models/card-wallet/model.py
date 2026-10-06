"""card-wallet: slim sleeve wallet for 6 bank cards, thumb push-out slot, elastic-band channel for notes.

Spec: one-piece sleeve, cards slide in from the open +X end. A stadium window in the top face near
the closed end lets the thumb push the stack out. Two low ridges ring the sleeve mid-length and form
a channel for a flat 6 mm elastic band that clamps folded banknotes against the bottom face.
Walls 1.2 mm; long edges rounded R2 (concentric with the pocket), closed-end edges chamfered.
Printed standing on its closed end: pocket is a vertical cavity, no bridges, no supports.

MEASURE BEFORE PRINTING: bank card 85.6 x 54 x 0.76 mm (ISO 7810 ID-1); embossed cards are thicker
(~1.2 mm on the numbers) -> reduce CARDS or raise CARD_T.
Assumptions: 6 flat cards; the stack is held by slight friction (POCKET_CLEAR_T total), not a latch;
elastic band 5-6 mm wide bought separately (or a hair tie).
Walls are exactly 1.2 mm by request (slim wallet); the audit WARN on 1.2 mm walls is accepted.
Printed on end (87 mm tall, 9 mm thick) the audit flags it as wobbly; brim is forced on to anchor it.
Hardware: 1x flat elastic band, ~6 mm wide, ~150 mm loop.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,
    loads=[],
    print_orientation=(0, -90, 0),  # closed end on the bed, pocket opening up
    supports="off",
    brim="on",                 # tall narrow print on ABS: brim for adhesion/stability
)

# Parameters
CARD_L = 85.6
CARD_W = 54.0
CARD_T = 0.76
CARDS = 6
POCKET_CLEAR_L = 0.6      # length clearance (cards stop against closed end)
POCKET_CLEAR_W = 0.8      # width clearance, total
POCKET_CLEAR_T = 0.5      # stack-thickness clearance, total (light friction)
POCKET_R = 0.8            # pocket long-edge radius
END_CHAMFER = 0.4         # closed-end edges (bed side when printing)
WALL = 1.2
THUMB_SLOT_L = 38.0       # thumb push-out window, along X
THUMB_SLOT_W = 18.0
THUMB_SLOT_FROM_END = 6.0 # gap between closed-end inner wall and window
OPEN_NOTCH_R = 10.0       # finger notch at the opening, top face
BAND_W = 7.0              # elastic channel width (6 mm band + 1 mm)
RIDGE_W = 1.6
RIDGE_H = 0.8
BAND_X = 8.0              # channel centre offset from wallet centre towards the open end

POCKET_L = CARD_L + POCKET_CLEAR_L
POCKET_W = CARD_W + POCKET_CLEAR_W
POCKET_T = CARDS * CARD_T + POCKET_CLEAR_T
OUT_T = POCKET_T + 2 * WALL


def _tube(grow: float, x_from: float, x_to: float) -> Part:
    """Rounded-rectangle prism along X: pocket section grown by `grow`, radius grown with it."""
    sec = RectangleRounded(POCKET_W + 2 * grow, POCKET_T + 2 * grow, POCKET_R + grow)
    return extrude(Plane.YZ.offset(x_from) * sec, x_to - x_from)


def build() -> Part:
    x0 = -POCKET_L / 2                       # inner face of closed end
    x1 = POCKET_L / 2                        # open end
    body = _tube(WALL, x0 - WALL, x1)
    body = chamfer(body.faces().sort_by(Axis.X)[0].edges(), END_CHAMFER)
    for dx in (-(BAND_W + RIDGE_W) / 2, (BAND_W + RIDGE_W) / 2):
        cx = BAND_X + dx
        ridge = _tube(WALL + RIDGE_H, cx - RIDGE_W / 2, cx + RIDGE_W / 2)
        # 45 deg underside (faces the bed when printed on end) -> no support
        ridge = chamfer(ridge.faces().sort_by(Axis.X)[0].edges(), RIDGE_H - 0.05)
        body += ridge
    body -= _tube(0, x0, x1 + 1)
    # thumb push-out window through the top skin
    sx = x0 + THUMB_SLOT_FROM_END + THUMB_SLOT_L / 2
    body -= Pos(sx, 0, OUT_T / 2 + RIDGE_H + 1) * slot(THUMB_SLOT_L, THUMB_SLOT_W, WALL + RIDGE_H + 2)
    # finger notch at the opening (top skin only)
    body -= Pos(x1, 0, POCKET_T / 2 - 0.01) * Cylinder(OPEN_NOTCH_R, WALL + RIDGE_H + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Pos(0, 0, OUT_T / 2 + RIDGE_H) * body
