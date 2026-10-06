"""spice-rack-tier: 3-step stadium riser for spice jars, 250 mm wide.

Spec: three treads (55 deep, 35 mm rise) on vertical legs that run down to the shelf,
each tread with an 8 mm front lip so jars can't slide off; back wall 105 mm with a 35 mm rear foot (full jars put the COM
near the back edge, so the foot keeps the tip angle >= 12 deg).
Constant profile extruded along X, printed standing on one end so every tread and
leg lies in the layer plane: no overhangs, no supports, load runs along layers.
Assumptions: jars Ø45-52 mm, <= 150 g each, ~5 jars per tread (2.25 kg total);
fits a cabinet shelf >= 205 mm deep and >= 105 mm + jar height clear.
"""

from build123d import *

from cadlib import *

# Parameters
WIDTH = 250.0
STEPS = 3
TREAD_D = 55.0
RISE = 35.0
T = 2.4            # tread / leg thickness
LIP = 8.0
FOOT = 35.0        # rear anti-tip foot behind the back wall
FOOT_T = 3.0
JAR_G = 150
JARS_PER_TREAD = 5

DEPTH = STEPS * TREAD_D + T
TOTAL_D = DEPTH + FOOT

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=True,
    loads=[dict(at=(0, i * TREAD_D + TREAD_D / 2, (i + 1) * RISE), grams=JAR_G * JARS_PER_TREAD)
           for i in range(STEPS)],
    print_orientation=(0, 90, 0),   # on its end: profile in layers, 250 mm tall print
    supports="auto",
    brim="on",
)


def bar(y0, y1, z0, z1):
    return Pos(0, (y0 + y1) / 2, z0) * Box(WIDTH, y1 - y0, z1 - z0, align=ON_BED)


def build() -> Part:
    parts = []
    for i in range(STEPS):
        top = (i + 1) * RISE
        parts.append(bar(i * TREAD_D, i * TREAD_D + T, 0, top + LIP))          # leg + lip
        parts.append(bar(i * TREAD_D, (i + 1) * TREAD_D + T, top - T, top))     # tread
    parts.append(bar(STEPS * TREAD_D, DEPTH, 0, STEPS * RISE))                  # back wall
    parts.append(bar(DEPTH - T, TOTAL_D, 0, FOOT_T))                            # anti-tip foot
    part = parts[0]
    for p in parts[1:]:
        part += p
    return part
