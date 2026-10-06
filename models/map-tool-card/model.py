"""map-tool-card: credit-card navigation tool - romers 1:25k/1:50k, slope inclinometer, ruler edge.

Spec: 85.6 x 54 x 2 mm (ID-1 card). All marks engraved 0.6 mm into the top face, computed from scale.
- Top-right sharp corner: 1:25 000 romer, 1 km legs (40 mm) along top + right edges, tick per 100 m
  (4 mm), long tick every 500 m. Read grid refs with the corner on the point.
- Top-left sharp corner: 1:50 000 romer, 1 km legs (20 mm), tick per 100 m (2 mm), long tick at 500 m.
- Bottom edge: ruler, zero at the bottom-left corner, 80 mm, ticks open to the edge every 5 mm
  (long + numbered "cm" marks every 10 mm would collide with the arc, so cm are long ticks only).
- Inclinometer: Ø2 mm pivot hole; tie a 15 cm thread through it with a small weight (nut, split shot).
  Hold the card upright with the TOP edge sighted along the slope; the thread crosses the arc at the
  slope angle. Arc 0-60° both ways, tick every 5°, long tick every 10°, labels 0/30/60.
Hardware: ~15 cm thread + small weight (M4 nut or fishing split shot).
Assumptions: 1 mm ruler graduations are not printable cleanly with a 0.4 nozzle -> 5 mm pitch;
grooves 0.6 mm wide; card corners used as romer zero are sharp, the bottom-right corner is rounded.
Print flat, marks up; fill the grooves with a permanent marker and wipe for contrast.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # flat, marks on top
    supports="off",
    brim="auto",
)

CARD_L = 85.6
CARD_W = 54.0
CARD_T = 2.0
CORNER_R = 3.0            # only the bottom-right corner (no scale zero there)
GROOVE_W = 0.6            # engraved line width
GROOVE_D = 0.6            # engraving depth
TEXT_SIZE = 7.0           # font size -> ~5 mm cap/digit height
# romers: mm on the card per 100 m on the ground = 100 000 mm / scale
ROMER_25K = 100_000 / 25_000   # 4.0 mm
ROMER_50K = 100_000 / 50_000   # 2.0 mm
ROMER_STEPS = 10               # 1 km legs
TICK_SHORT = 2.5
TICK_LONG = 5.0
# ruler
RULER_LEN = 80.0
RULER_PITCH = 5.0
# inclinometer
PIVOT = (0.0, 12.0)
PIVOT_HOLE_D = 2.0
ARC_R = 30.0
ARC_MAX = 60
ARC_STEP = 5

X0, X1 = -CARD_L / 2, CARD_L / 2
Y0, Y1 = -CARD_W / 2, CARD_W / 2


def _groove(x, y, length, angle=0.0) -> Part:
    """Groove centred on (x, y), long axis rotated `angle` deg from +X, cut into the top face."""
    g = Box(length, GROOVE_W, GROOVE_D + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Pos(x, y, CARD_T - GROOVE_D) * Rot(0, 0, angle) * g


def _text(t, x, y) -> Part:
    return Pos(x, y, CARD_T - GROOVE_D) * label(t, size=TEXT_SIZE, depth=GROOVE_D + 1)


def _romer(cx, cy, sx, sy, pitch) -> list:
    """Ticks along both legs from corner (cx, cy); sx/sy = +-1 direction into the card."""
    cuts = []
    for i in range(1, ROMER_STEPS + 1):
        ln = TICK_LONG if i % 5 == 0 else TICK_SHORT
        d = i * pitch
        # leg along the horizontal edge (ticks perpendicular to it, open to the edge)
        cuts.append(_groove(cx + sx * d, cy + sy * (ln / 2 - 0.5), ln + 1, 90))
        # leg along the vertical edge
        cuts.append(_groove(cx + sx * (ln / 2 - 0.5), cy + sy * d, ln + 1, 0))
    return cuts


def build() -> Part:
    card = Box(CARD_L, CARD_W, CARD_T, align=ON_BED)
    br = card.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:].sort_by(Axis.Y)[0]
    card = fillet(br, CORNER_R)
    card = chamfer(card.edges().group_by(Axis.Z)[0], 0.4)

    cuts = []
    cuts += _romer(X1, Y1, -1, -1, ROMER_25K)
    cuts += _romer(X0, Y1, +1, -1, ROMER_50K)
    cuts.append(_text("1:25k", X1 - 20, Y1 - 12))
    cuts.append(_text("1:50k", X0 + 17, Y1 - 12))

    # ruler, zero at the bottom-left corner
    n = int(RULER_LEN / RULER_PITCH)
    for i in range(1, n + 1):
        ln = TICK_LONG if i % 2 == 0 else TICK_SHORT
        cuts.append(_groove(X0 + i * RULER_PITCH, Y0 + ln / 2 - 0.5, ln + 1, 90))

    # inclinometer arc around the pivot (0 deg = straight down)
    px, py = PIVOT
    for a in range(-ARC_MAX, ARC_MAX + 1, ARC_STEP):
        ln = 4.0 if a % 10 == 0 else 2.5
        r = ARC_R - ln / 2
        v = Vector(0, -1).rotate(Axis.Z, a)
        cuts.append(_groove(px + v.X * r, py + v.Y * r, ln, a + 90))
    for a in (-60, -30, 0, 30, 60):
        v = Vector(0, -1).rotate(Axis.Z, a)
        r = ARC_R - 9
        cuts.append(_text(str(abs(a)), px + v.X * r, py + v.Y * r))

    for c in cuts:
        card -= c
    card -= Pos(px, py, -1) * Cylinder(PIVOT_HOLE_D / 2, CARD_T + 2, align=ON_BED)
    return card
