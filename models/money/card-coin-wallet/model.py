"""card-coin-wallet: card sleeve for 4 cards stacked over a sliding coin drawer for up to 6 euro coins.

Spec: shell with two tunnels: upper card pocket opens at +X (thumb window in the top skin near the
closed end), lower drawer tunnel opens at -X. The drawer is an open tray (6 coins lie flat 2 x 3, max
EUR 2 = 25.75 mm); the tunnel ceiling closes it so coins cannot fall out. Small side bumps rub the
tunnel walls (DETENT_INTERF) so the drawer stays shut in a pocket. Finger notches in the skins at
both openings. Two parts printed together, both standing on end (all cavities vertical, the only
ceilings are 4 mm bridges at the closed tunnel ends) -> no supports.

MEASURE BEFORE PRINTING: bank card 85.6 x 54 x 0.76 mm; EUR 2 coin 25.75 mm dia, 50c 2.38 mm thick
(thickest coin) - drawer is sized for 6 coins of any denomination lying flat.
Assumptions: flat (non-embossed) cards; the drawer is pulled by pinching it through the bottom notch.
Walls are 1.2 mm (slim wallet); the audit WARN on 1.2 mm walls is accepted. Tall narrow prints on end ->
brim forced on. The 4 cm2 "needs support" are the 4.4 mm (tunnel end) and 2.7 mm (drawer back wall)
bridges over the closed ends - well under the 15 mm bridge limit, printed without supports.
Hardware: none.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,
    loads=[],
    print_orientation=(0, -90, 0),  # both parts on their -X end
    supports="off",
    brim="on",                      # tall narrow ABS parts
)

# Parameters
CARD_L, CARD_W, CARD_T = 85.6, 54.0, 0.76
CARDS = 4
CARD_CLEAR_L = 0.6
CARD_CLEAR_W = 0.8
CARD_CLEAR_T = 0.5          # total stack-thickness clearance
COIN_D_MAX = 25.75          # EUR 2
COIN_T_MAX = 2.38           # 50c
COIN_HEADROOM = 0.32        # coin pocket depth over the thickest coin
WALL = 1.2                  # shell skins and divider
CAV_R = 0.8                 # cavity long-edge radius
DRAWER_WALL = 1.2
DRAWER_FLOOR = 1.2
DRAWER_CLEAR = 0.25         # per side, drawer in tunnel (slide fit)
DETENT_R = 0.8              # side bump sphere radius
DETENT_INTERF = 0.15        # bump overlap with tunnel wall (friction hold)
THUMB_SLOT_L, THUMB_SLOT_W = 34.0, 18.0
NOTCH_R = 10.0              # finger notches at the openings
PRINT_GAP = 8.0             # drawer placed beside the shell on the plate

POCKET_L = CARD_L + CARD_CLEAR_L
POCKET_W = CARD_W + CARD_CLEAR_W
CARD_H = CARDS * CARD_T + CARD_CLEAR_T
DRAWER_H = DRAWER_FLOOR + COIN_T_MAX + COIN_HEADROOM
DRAWER_W = POCKET_W - 2 * DRAWER_CLEAR
TUNNEL_H = DRAWER_H + 2 * DRAWER_CLEAR
SHELL_L = POCKET_L + WALL
SHELL_H = WALL + TUNNEL_H + WALL + CARD_H + WALL
DRAWER_L = SHELL_L - WALL - DRAWER_CLEAR


def _prism(w, h, r, x_from, x_to, z_mid) -> Part:
    sec = RectangleRounded(w, h, r)
    return Pos(0, 0, z_mid) * extrude(Plane.YZ.offset(x_from) * sec, x_to - x_from)


def shell() -> Part:
    x0, x1 = -SHELL_L / 2, SHELL_L / 2
    body = _prism(POCKET_W + 2 * WALL, SHELL_H, CAV_R + WALL, x0, x1, SHELL_H / 2)
    body = chamfer(body.faces().sort_by(Axis.X)[0].edges() + body.faces().sort_by(Axis.X)[-1].edges(), 0.4)
    tz = WALL + TUNNEL_H / 2
    cz = WALL + TUNNEL_H + WALL + CARD_H / 2
    body -= _prism(POCKET_W, TUNNEL_H, CAV_R, x0 - 1, x1 - WALL, tz)       # drawer tunnel, opens -X
    body -= _prism(POCKET_W, CARD_H, CAV_R, x0 + WALL, x1 + 1, cz)         # card pocket, opens +X
    sx = x0 + WALL + 5 + THUMB_SLOT_L / 2
    body -= Pos(sx, 0, SHELL_H + 1) * slot(THUMB_SLOT_L, THUMB_SLOT_W, WALL + 2)
    body -= Pos(x1, 0, cz) * Cylinder(NOTCH_R, WALL + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body -= Pos(x0, 0, tz) * Cylinder(NOTCH_R, WALL + 2, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return body


def drawer() -> Part:
    r = CAV_R - DRAWER_CLEAR
    d = _prism(DRAWER_W, DRAWER_H, r, -DRAWER_L / 2, DRAWER_L / 2, DRAWER_H / 2)
    d = chamfer(d.faces().sort_by(Axis.X)[0].edges(), 0.4)
    inner_l = DRAWER_L - 2 * DRAWER_WALL
    d -= Pos(0, 0, DRAWER_H + 1) * Box(inner_l, DRAWER_W - 2 * DRAWER_WALL, DRAWER_H - DRAWER_FLOOR + 1,
                                   align=(Align.CENTER, Align.CENTER, Align.MAX))
    bx = DRAWER_L / 2 - 8
    for s in (1, -1):
        y = s * (DRAWER_W / 2 + DRAWER_CLEAR + DETENT_INTERF - DETENT_R)
        d += Pos(bx, y, DRAWER_H / 2) * Sphere(DETENT_R)
    return d


def build():
    # drawer shown pulled out beside the shell for printing
    return [shell(), Pos(-(SHELL_L - DRAWER_L) / 2, -(POCKET_W + 2 * WALL) / 2 - PRINT_GAP - DRAWER_W / 2, 0) * drawer()]


assert 2 * COIN_D_MAX <= DRAWER_W - 2 * DRAWER_WALL, "drawer too narrow for 2 coins"
assert 3 * COIN_D_MAX <= DRAWER_L - 2 * DRAWER_WALL, "drawer too short for 3 coins"
