"""coin-counting-tray: cashier counting tray, one 20-coin channel per euro coin.

Spec: 8 U-channels (round bottom) run front->back and slope down toward the back by TILT,
so coins stand on edge and lean against a stop face that is square to the channel axis.
Each channel is exactly 20 coin thicknesses long: a channel filled level with the front
edge holds 20 coins (value engraved behind it). Engraved tick marks every 5 coins on the
land beside each channel. All channels open at the front into a funnel pocket ending in a
pour spout: tip the tray forward to pour the counted coins into a bag.

MEASURE BEFORE PRINTING (calipers, Ø / thickness mm): 1c 16.25/1.67, 2c 18.75/1.67,
5c 21.25/1.67, 10c 19.75/1.93, 20c 22.25/2.14, 50c 24.25/2.38, €1 23.25/2.33, €2 25.75/2.20.

Assumptions: channel width = coin Ø + CH_CLEAR (0.8 mm) so coins drop in easily;
channel length uses nominal thickness (+0.05 mm/coin LEN_ALLOW for burrs/air between coins);
tray ~ 209 x 95 x 24 mm, solid block (sparse infill keeps it light and stable).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="on",              # large flat ABS footprint
)

# (label, 20-coin value, Ø, thickness)
COINS = [
    ("1c", "€0.20", 16.25, 1.67), ("2c", "€0.40", 18.75, 1.67),
    ("5c", "€1", 21.25, 1.67), ("10c", "€2", 19.75, 1.93),
    ("20c", "€4", 22.25, 2.14), ("50c", "€10", 24.25, 2.38),
    ("€1", "€20", 23.25, 2.33), ("€2", "€40", 25.75, 2.20),
]
N_COINS = 20
MARK_EVERY = 5
LEN_ALLOW = 0.05       # extra length per coin
CH_CLEAR = 0.8         # channel width = coin Ø + this
LAND = 3.0             # wall between channels
TILT = 10.0            # channel slope, back end lower (deg)
FLOOR = 2.0            # min material under the deepest channel
MARGIN = 5.0           # side walls
POCKET_D = 26.0        # funnel pocket front->back
SPOUT_W = 34.0
FRONT_WALL = 3.0
LABEL_D = 18.0         # label strip behind the channels
TEXT_SIZE = 5.0
TEXT_DEPTH = 0.6
MARK_W = 0.8
MARK_DEPTH = 0.6


def build() -> Part:
    t = math.radians(TILT)
    widths = [c[2] + CH_CLEAR for c in COINS]
    lens = [N_COINS * (c[3] + LEN_ALLOW) for c in COINS]
    pitch = [w + LAND for w in widths]
    total_w = sum(pitch) - LAND + 2 * MARGIN
    max_r = max(widths) / 2
    drop = max(lens) * math.sin(t)
    H = FLOOR + max_r + drop + max_r * (1 - math.cos(t))
    y_f = 0.0                                            # channel fronts
    y_back = max(lens) * math.cos(t)
    depth = FRONT_WALL + POCKET_D + y_back + LABEL_D
    y0 = -FRONT_WALL - POCKET_D
    part = Pos(0, (y0 + y_back + LABEL_D) / 2, 0) * rounded_box(total_w, depth, H, radius=5)

    cuts = []
    x = -total_w / 2 + MARGIN
    for (name, value, d, th), w, L, p in zip(COINS, widths, lens, pitch):
        xc = x + w / 2
        x += p
        r = w / 2
        ext = 6.0  # run the cutter forward into the pocket
        ch = Pos(0, -ext, 0) * (Rot(-90, 0, 0) * Cylinder(r, L + ext, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        ch += Pos(0, -ext, 0) * Box(w, L + ext, 3 * H, align=(Align.CENTER, Align.MIN, Align.MIN))
        ch = Rot(-TILT, 0, 0) * ch
        cuts.append(Pos(xc, y_f, H - r) * ch)
        # tick marks every MARK_EVERY coins, on the land right of the channel
        for k in range(MARK_EVERY, N_COINS, MARK_EVERY):
            s = k * (th + LEN_ALLOW)
            ym = y_f + (N_COINS * (th + LEN_ALLOW) - s) * math.cos(t)
            cuts.append(Pos(xc + r + LAND / 2, ym, H - MARK_DEPTH)
                        * Box(LAND + 2, MARK_W, 2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        # label behind the channels
        yl = y_back + LABEL_D / 2
        for txt, yy in ((name, yl + 3.6), (value, yl - 3.6)):
            sk = Text(txt, font_size=TEXT_SIZE, font_style=FontStyle.BOLD)
            cuts.append(Pos(xc, yy, H - TEXT_DEPTH) * extrude(sk, TEXT_DEPTH + 1))

    # funnel pocket + spout
    zf = H - max_r - 1.0
    half = total_w / 2 - MARGIN
    fun = Polygon((-half, 0.5), (-SPOUT_W / 2, y0 + FRONT_WALL), (-SPOUT_W / 2, y0 - 1),
                  (SPOUT_W / 2, y0 - 1), (SPOUT_W / 2, y0 + FRONT_WALL), (half, 0.5),
                  align=None)
    cuts.append(Pos(0, 0, zf) * extrude(fun, H))
    part -= Part() + cuts
    return part
