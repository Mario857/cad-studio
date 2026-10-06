"""sim-passport-card: credit-card-size travel tool (SIM pin, 3 SIM pockets, coin gauge, 50 mm ruler).

Spec: ISO ID-1 outline 85.6 x 54 mm, R3.18 corners, 3.0 mm thick, printed flat (top face up).
- SIM eject pin: 22 mm groove 1.1 wide x 1.4 deep with two 3 mm pinch zones 0.8 wide (friction snap)
  and a 5x4 mm head pocket; finger-lift notch at the head end.
- SIM pockets 0.8 deep (card 0.67 mm): 2x nano (12.3 x 8.8) and 1x nano/micro adapter tray (15 x 12),
  +0.12 mm per side clearance, each with a through finger notch (d 7) on the lower edge to push the card out.
- Coin gauge: stepped concentric well for EUR coins 2 EUR 25.75 / 1 EUR 23.25 / 5c 21.25 / 2c 18.75 /
  1c 16.25 (through). Each coin drops onto its own ledge (0.45 mm steps); +0.3 mm diameter clearance.
- Ruler: 0..50 mm along the bottom long edge, engraved 0.6 deep, 0.8 mm wide ticks every 5 mm
  (10 mm ticks longer), cm numbers 0..5 at 5 mm text. Tick centres at exact mm positions.
Assumptions: EUR coin set; 1 mm ticks omitted (0.8 mm ticks at 1 mm pitch are unprintable);
pin is a straight ~0.8-1.0 mm wire with flat head <= 5 x 4 mm; pinch zones rely on PLA compliance.
"""

from build123d import *

from cadlib import *

META = dict(
    material="PLA",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # flat, top face up: pockets/engraving need no supports
    supports="off",
    brim="auto",
)

# Card
CARD_L = 85.6
CARD_W = 54.0
CARD_T = 3.0
CARD_R = 3.18
TOP_R = 0.6

# SIM pockets
SIM_DEPTH = 0.8
SIM_CLR = 0.12          # per side
SIM_CORNER_R = 0.6
NANO = (12.3, 8.8)
ADAPTER = (15.0, 12.0)
POCKET_Y = 3.0
POCKETS = [(-30.5, ADAPTER), (-14.5, NANO), (0.5, NANO)]  # (x centre, (l, w))
NOTCH_D = 7.0

# SIM pin
PIN_Y = 19.5
PIN_X0 = -38.0          # head end
PIN_LEN = 22.0
PIN_W = 1.1
PIN_PINCH_W = 0.8
PIN_PINCH_L = 3.0
PIN_DEPTH = 1.4
PIN_HEAD = (5.0, 4.0)

# Coin gauge (EUR)
COINS = [25.75, 23.25, 21.25, 18.75, 16.25]   # large -> small
COIN_CLR = 0.3
COIN_STEP = 0.45
COIN_C = (26.0, 4.0)

# Ruler
RULER_X0 = -38.0
RULER_LEN = 50
TICK_W = 0.8
TICK_MINOR = 3.0
TICK_MAJOR = 5.0
TICK_PITCH = 5
ENGRAVE = 0.6
NUM_SIZE = 5.0
NUM_Y = -18.0


def _top(z_depth: float) -> float:
    return CARD_T - z_depth


def build() -> Part:
    card = rounded_box(CARD_L, CARD_W, CARD_T, radius=CARD_R, top_radius=TOP_R, bottom_chamfer=0.4)

    cuts = []
    # SIM pockets + through finger notches
    for x, (l, w) in POCKETS:
        cuts.append(Pos(x, POCKET_Y, _top(SIM_DEPTH)) *
                    extrude(RectangleRounded(l + 2 * SIM_CLR, w + 2 * SIM_CLR, SIM_CORNER_R), SIM_DEPTH + 1))
        cuts.append(Pos(x, POCKET_Y - w / 2, -1) * Cylinder(NOTCH_D / 2, CARD_T + 2, align=ON_BED))

    # SIM pin groove (wide), head pocket, lift notch
    gx = PIN_X0 + PIN_HEAD[0] / 2 + PIN_LEN / 2
    cuts.append(Pos(gx, PIN_Y, _top(PIN_DEPTH)) * Box(PIN_LEN, PIN_W, PIN_DEPTH + 1, align=ON_BED))
    cuts.append(Pos(PIN_X0 + PIN_HEAD[0] / 2, PIN_Y, _top(PIN_DEPTH)) *
                extrude(RectangleRounded(PIN_HEAD[0], PIN_HEAD[1], 1.0), PIN_DEPTH + 1))
    cuts.append(Pos(PIN_X0 + PIN_HEAD[0] / 2, PIN_Y - PIN_HEAD[1] / 2, _top(PIN_DEPTH)) *
                Cylinder(3.0, PIN_DEPTH + 1, align=ON_BED))

    # Coin gauge: stepped well, last coin through
    cx, cy = COIN_C
    for i, d in enumerate(COINS):
        last = i == len(COINS) - 1
        depth = CARD_T + 1 if last else COIN_STEP * (i + 1)
        z0 = -1 if last else _top(depth)
        h = CARD_T + 2 if last else depth + 1
        cuts.append(Pos(cx, cy, z0) * Cylinder((d + COIN_CLR) / 2, h, align=ON_BED))

    # Ruler ticks from the bottom edge
    y_edge = -CARD_W / 2
    for mm in range(0, RULER_LEN + 1, TICK_PITCH):
        ln = TICK_MAJOR if mm % 10 == 0 else TICK_MINOR
        cuts.append(Pos(RULER_X0 + mm, y_edge - 1 + (ln + 1) / 2, _top(ENGRAVE)) *
                    Box(TICK_W, ln + 1, ENGRAVE + 1, align=ON_BED))
        if mm % 10 == 0:
            cuts.append(Pos(RULER_X0 + mm, NUM_Y, _top(ENGRAVE)) *
                        label(str(mm // 10), size=NUM_SIZE, depth=ENGRAVE + 0.5))

    part = card
    for c in cuts:
        part = part - c

    # restore pin pinch zones (narrow sections of the groove)
    for fx in (0.25, 0.75):
        px = PIN_X0 + PIN_HEAD[0] + PIN_LEN * fx - PIN_HEAD[0] / 2
        for s in (-1, 1):
            sliver = Pos(px, PIN_Y + s * (PIN_PINCH_W / 2 + (PIN_W - PIN_PINCH_W) / 4), _top(PIN_DEPTH)) * \
                Box(PIN_PINCH_L, (PIN_W - PIN_PINCH_W) / 2, PIN_DEPTH, align=ON_BED)
            part = part + sliver
    return part
