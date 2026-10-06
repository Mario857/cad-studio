"""tick-remover: flat tick-removal hook with a fine (0.5 mm) and a wide (1.2 mm) V-slot + keyring hole.

How to use: pick the slot that fits (FINE "0.5" for nymphs / small ticks, WIDE "1.2" for adult ticks).
Lay the tool flat on the skin, slide the open V under the tick from the side until the tick's head
sits in the narrow end of the V (the thin wedge tip slides between skin and tick body). Keep light
contact with the skin, then slowly twist the tool a few full turns (or lift steadily) until the tick
lets go - do not squeeze the tick's body, do not use oil/heat. Disinfect the bite and the tool, wash
hands, note the date. If the head/mouthparts stay in the skin, the bite gets a spreading red rash,
or you get fever/flu symptoms in the following weeks: SEE A DOCTOR.

Spec: 60 x 16 mm, 3 mm body tapering to 1.2 mm wedge tips, keyring hole Ø5. Printed flat ("fine").
Hardware: small split ring / keyring.
Assumptions: 0.5 mm tip gap is at the limit of a 0.4 nozzle (walls are perimeter-defined in XY, so it
prints as a gap of ~0.4-0.6 mm); clean any stringing out of the slot with a blade before use.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # flat
    supports="off",
    brim="auto",
)

LENGTH = 60.0
WIDTH = 16.0
THICK = 3.0
TIP_THICK = 1.2           # wedge tip thickness
TAPER_LEN = 14.0          # wedge length at each end
CORNER_R = 4.0
# V-slots: (tip gap, mouth width at the edge, V length)
FINE_GAP = 0.5
FINE_MOUTH = 4.0
WIDE_GAP = 1.2
WIDE_MOUTH = 5.5
V_LEN = 9.0
TAIL_LEN = 2.0            # parallel part at the tip gap
KEYRING_D = 5.0
TEXT_SIZE = 7.0           # ~5 mm digits
TEXT_DEPTH = 0.6


def _v_slot(x_end, direction, gap, mouth) -> Part:
    """V-slot cutter open at x_end, pointing inward (direction = -1 at the +X end)."""
    d = direction
    pts = [
        (x_end - d * 1.0, mouth / 2 + 0.6), (x_end, mouth / 2), (x_end + d * V_LEN, gap / 2),
        (x_end + d * (V_LEN + TAIL_LEN), gap / 2), (x_end + d * (V_LEN + TAIL_LEN), -gap / 2),
        (x_end + d * V_LEN, -gap / 2), (x_end, -mouth / 2), (x_end - d * 1.0, -mouth / 2 - 0.6),
    ]
    if d < 0:
        pts = pts[::-1]
    return extrude(Plane.XY.offset(-1) * Polygon(*pts, align=None), THICK + 2)


def _taper(x_end, direction) -> Part:
    d = direction
    pts = [(x_end + d * TAPER_LEN, THICK), (x_end, TIP_THICK), (x_end - d, TIP_THICK),
           (x_end - d, THICK + 1), (x_end + d * TAPER_LEN, THICK + 1)]
    if d > 0:
        pts = pts[::-1]
    return extrude(Plane.XZ * Polygon(*pts, align=None), WIDTH, both=True)


def build() -> Part:
    x0, x1 = -LENGTH / 2, LENGTH / 2
    part = rounded_box(LENGTH, WIDTH, THICK, radius=CORNER_R)
    part -= _taper(x0, +1)
    part -= _taper(x1, -1)
    part -= _v_slot(x0, +1, FINE_GAP, FINE_MOUTH)
    part -= _v_slot(x1, -1, WIDE_GAP, WIDE_MOUTH)
    part -= Pos(0, 0, -1) * Cylinder(KEYRING_D / 2, THICK + 2, align=ON_BED)
    for txt, x in (("0.5", x0 + TAPER_LEN + 6), ("1.2", x1 - TAPER_LEN - 6)):
        part -= Pos(x, 0, THICK - TEXT_DEPTH) * label(txt, size=TEXT_SIZE, depth=TEXT_DEPTH + 1)
    return part
