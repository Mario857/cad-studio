"""qr-payment-stand: desk stand for a 100x100 mm printed QR payment card, slide-in slot, SCAN TO PAY.

Spec: 120x70x12 mm base with raised "SCAN TO PAY" (8 mm text, 0.6 mm raised) on its top in front
of a holder leaning back 15 deg. Holder = back plate + two side grooves with 4 mm front lips; the
card slides in from the top and rests on the base; its top 10 mm stands proud for removal.
Visible QR area 92 mm wide (lips cover 4 mm per side; QR codes keep a quiet zone).

MEASURE BEFORE PRINTING: card size CARD_W (100) and thickness CARD_T (assumed 0.8 mm laminated;
plain 300 g/m2 card is ~0.4 mm and still fits).
Assumptions: WIDTH_CLEAR 1.0 mm and GAP_CLEAR 0.6 mm total play.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="auto",
)

# Parameters
CARD_W = 100.0
CARD_H = 100.0
CARD_T = 0.8
WIDTH_CLEAR = 1.0        # total
GAP_CLEAR = 0.6          # total, on thickness
TILT = 15.0              # lean back from vertical (deg)
PROUD = 10.0             # card top above the holder
BACK_T = 3.0
SIDE_T = 3.0
LIP_W = 4.0              # lip overlap on the card face
LIP_T = 2.0
EMBED = 6.0              # holder sunk into the base
BASE_L = 120.0
BASE_W = 70.0
BASE_H = 12.0
HOLDER_Y = 12.0          # holder groove centre behind base centre
TEXT = "SCAN TO PAY"
TEXT_SIZE = 8.0
TEXT_H = 0.6


def build() -> Part:
    gap = CARD_T + GAP_CLEAR
    in_w = CARD_W + WIDTH_CLEAR
    out_w = in_w + 2 * SIDE_T
    h = CARD_H - PROUD + EMBED

    # holder in local frame: card plane y=0..gap, back plate behind (+Y), lips in front (-Y)
    hold = Pos(0, gap + BACK_T / 2, 0) * Box(out_w, BACK_T, h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for sx in (-1, 1):
        hold += Pos(sx * (in_w + SIDE_T) / 2, gap / 2, 0) * Box(SIDE_T, gap + 0.02, h, align=(Align.CENTER, Align.CENTER, Align.MIN))
        lw = SIDE_T + LIP_W
        hold += Pos(sx * (out_w - lw) / 2, -LIP_T / 2, 0) * Box(lw, LIP_T, h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    hold = Pos(0, HOLDER_Y, BASE_H - EMBED) * Rot(-TILT, 0, 0) * hold

    base = rounded_box(BASE_L, BASE_W, BASE_H, radius=6)
    base = fillet(base.edges().group_by(Axis.Z)[-1], 1.5)
    part = base + hold

    txt = label(TEXT, size=TEXT_SIZE, depth=TEXT_H + 0.2)
    part += Pos(0, -BASE_W / 2 + 14, BASE_H - 0.2) * txt
    return part
