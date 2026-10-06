"""coin-capsules: set of 8 two-part press-fit collector capsules, one per euro coin, printed together.

Spec per coin: BASE = wide flange with the denomination raised on its rim (top face) + a thin spigot
ring that holds the coin (coin rests on a ledge over a viewing window). CAP = top plate with a viewing
window + skirt that presses over the spigot (fit CAP_FIT) and lands on the flange. Both faces of the
coin stay visible through the windows; the coin is held between the two ledges with COIN_PLAY axial.
Print pose: bases flange-down, caps top-down - no overhangs, no supports.

MEASURE BEFORE PRINTING (dia / thickness mm): 1c 16.25/1.67, 2c 18.75/1.67, 5c 21.25/1.67,
10c 19.75/1.93, 20c 22.25/2.14, 50c 24.25/2.38, EUR1 23.25/2.33, EUR2 25.75/2.20.
Assumptions: press fit = clearance(spigot OD, "press") (+0.2 mm on dia) suits the H2C; if too tight,
set CAP_FIT = "snug". Coins are circulated (not proof) - ABS ledges touch the coin edge only.
Hardware: none.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # parts already in print pose
    supports="off",
    brim="auto",
)

# Parameters
COINS = [  # label, diameter, thickness
    ("1c", 16.25, 1.67), ("2c", 18.75, 1.67), ("5c", 21.25, 1.67), ("10c", 19.75, 1.93),
    ("20c", 22.25, 2.14), ("50c", 24.25, 2.38), ("€1", 23.25, 2.33), ("€2", 25.75, 2.20),
]
COIN_FIT = "slide"        # coin pocket dia = clearance(d, COIN_FIT)
COIN_PLAY = 0.2           # axial play
LEDGE = 1.5               # window ledge width (radial)
SPIGOT_WALL = 1.2
SKIRT_WALL = 1.6
CAP_FIT = "press"         # cap bore over the spigot
FLANGE_T = 2.0
CAP_TOP_T = 1.6
RIM_BAND = 8.0            # flange band outside the cap carrying the text
LABEL_SIZE = 7.0          # font size -> ~5.2 mm tall digits
LABEL_DEPTH = 0.6
EDGE = 0.4
GRID_PITCH = 52.0


def _disc(d: float, h: float, z0: float = 0.0) -> Part:
    return Pos(0, 0, z0) * Cylinder(d / 2, h, align=ON_BED)


def dims(d: float, t: float):
    pocket = clearance(d, COIN_FIT)
    spigot_od = pocket + 2 * SPIGOT_WALL
    bore = clearance(spigot_od, CAP_FIT)
    cap_od = bore + 2 * SKIRT_WALL
    flange_od = cap_od + 2 * RIM_BAND
    window = d - 2 * LEDGE
    spigot_h = t + COIN_PLAY
    return pocket, spigot_od, bore, cap_od, flange_od, window, spigot_h


def base(text: str, d: float, t: float) -> Part:
    pocket, spigot_od, bore, cap_od, flange_od, window, spigot_h = dims(d, t)
    b = _disc(flange_od, FLANGE_T)
    b = chamfer(b.edges().group_by(Axis.Z)[0], EDGE)
    b = chamfer(b.edges().group_by(Axis.Z)[-1], 0.4)
    b += _disc(spigot_od, spigot_h, FLANGE_T - 0.01)
    b -= _disc(pocket, spigot_h + 1, FLANGE_T)
    b -= _disc(window, FLANGE_T + 2, -1)
    r_text = (cap_od / 2 + flange_od / 2) / 2
    b += Pos(0, -r_text, FLANGE_T) * label(text, size=LABEL_SIZE, depth=LABEL_DEPTH)
    return b


def cap(d: float, t: float) -> Part:
    """Cap in print pose: top plate on the bed, skirt up."""
    pocket, spigot_od, bore, cap_od, flange_od, window, spigot_h = dims(d, t)
    c = _disc(cap_od, CAP_TOP_T + spigot_h)
    c = chamfer(c.edges().group_by(Axis.Z)[0], EDGE)
    c -= _disc(bore, spigot_h + 1, CAP_TOP_T)
    c -= _disc(window, CAP_TOP_T + 2, -1)
    return c


def build():
    parts = []
    for i, (txt, d, t) in enumerate(COINS):
        col, row = i % 4, i // 4
        x = (col - 1.5) * GRID_PITCH
        parts.append(Pos(x, (1.5 - row) * GRID_PITCH, 0) * base(txt, d, t))
        parts.append(Pos(x, (-0.5 - row) * GRID_PITCH, 0) * cap(d, t))
    return parts
