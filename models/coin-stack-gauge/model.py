"""coin-stack-gauge: upright gauge that reads the € value of a coin stack from its height.

Spec: a vertical slab with a foot/platform at the bottom; stack coins on the platform in
front of their column and read the value at the top of the stack. 8 columns (one per coin),
each with notched (engraved) ticks every MINOR coins and a longer tick + € value every MAJOR
coins; denomination at the top of each column. Zero = platform top. A short rear foot
(FOOT_BACK) keeps it from tipping backwards. Printed standing, foot on the bed.

Tick height for k coins = k x coin thickness (+ STACK_ALLOW per coin for burrs/air gaps).

MEASURE BEFORE PRINTING (calipers, thickness mm): 1c 1.67, 2c 1.67, 5c 1.67, 10c 1.93,
20c 2.14, 50c 2.38, €1 2.33, €2 2.20 — or better: measure a stack of 10 of each and set
THICK accordingly (worn coins are thinner).

Assumptions: 120 mm scale (≈ 50-70 coins per column); values in € without trailing zeros
except for cents ("€0.10").
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",   # ticks are horizontal: 0.2 mm layers = ±0.1 mm, well below 1 coin
    standing=True,
    loads=[],
    print_orientation=(0, 0, 0),    # as used: foot on the bed; engraved ticks/letters only
                                    # have <=1 mm ceilings
    supports="off",       # remaining 'support' area = ceilings of engraved letters (<1 mm)
    brim="auto",
)

# (label, value in € per coin, thickness)
COINS = [
    ("1c", 0.01, 1.67), ("2c", 0.02, 1.67), ("5c", 0.05, 1.67), ("10c", 0.10, 1.93),
    ("20c", 0.20, 2.14), ("50c", 0.50, 2.38), ("€1", 1.00, 2.33), ("€2", 2.00, 2.20),
]
STACK_ALLOW = 0.0      # extra height per coin
MINOR = 5              # tick every N coins
MAJOR = 10             # long tick + value every N coins
SCALE_H = 120.0
COL_W = 24.0
MARGIN = 3.0
SLAB_T = 4.0
HEADER = 11.0
FOOT_D = 40.0          # platform depth (coin stacks sit here)
FOOT_T = 4.0
FOOT_BACK = 22.0      # foot behind the slab (anti-tip)
TICK_W = 0.8          # divider line width
MINOR_L = 3.0
MAJOR_L = 6.0
GROOVE_D = 0.6         # tick / text depth
TEXT_SIZE = 5.0
HEAD_SIZE = 6.0


def fmt(v: float) -> str:
    if v < 1:
        return f"€{v:.2f}"
    return f"€{v:g}"


def build() -> Part:
    W = 8 * COL_W + 2 * MARGIN
    H = FOOT_T + SCALE_H + HEADER
    slab = Box(W, SLAB_T, H, align=(Align.CENTER, Align.MIN, Align.MIN))
    foot = Pos(0, SLAB_T + FOOT_BACK, 0) * Box(W, FOOT_D + SLAB_T + FOOT_BACK, FOOT_T,
                                            align=(Align.CENTER, Align.MAX, Align.MIN))
    part = slab + foot
    part = fillet(part.edges().filter_by(Axis.Y).group_by(Axis.Z)[-1], 2.0)
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    part += Pos(0, SLAB_T, FOOT_T) * extrude(Plane.YZ * Polygon((0, 0), (6, 0), (0, 6), align=None),
                                              W / 2 - 2, both=True)  # rear fillet gusset

    cuts = []
    fp = Plane.XZ  # front face y=0, normal -Y; local x = X, local y = Z
    for i, (name, val, th) in enumerate(COINS):
        x0 = -W / 2 + MARGIN + i * COL_W
        # column divider line
        if i:
            cuts.append(Pos(x0, 0, FOOT_T) * Box(TICK_W, 2 * GROOVE_D, SCALE_H, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        k = MINOR
        while True:
            z = FOOT_T + k * (th + STACK_ALLOW)
            if z > FOOT_T + SCALE_H - 1:
                break
            major = k % MAJOR == 0
            L = MAJOR_L if major else MINOR_L
            q = GROOVE_D * 2 ** 0.5   # 45° V-notch, 2 x GROOVE_D wide
            cuts.append(Pos(x0, 0, z) * Rot(45, 0, 0) * Box(L, q, q, align=(Align.MIN, Align.CENTER, Align.CENTER)))
            if major:
                t = Text(fmt(round(k * val, 2)), font_size=TEXT_SIZE, font_style=FontStyle.BOLD,
                         align=(Align.MIN, Align.CENTER))
                cuts.append(extrude(fp.offset(-GROOVE_D) * Pos(x0 + MAJOR_L + 1.2, z) * t, 2))
            k += MINOR
        t = Text(name, font_size=HEAD_SIZE, font_style=FontStyle.BOLD)
        cuts.append(extrude(fp.offset(-GROOVE_D) * Pos(x0 + COL_W / 2, FOOT_T + SCALE_H + HEADER / 2) * t, 2))
    part -= Part() + cuts
    return part
