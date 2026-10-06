"""money-clip: U-shaped flex money clip, 55 x 25 mm, for 5-20 folded banknotes.

Spec: U profile (spring bend + two legs) extruded CLIP_W. The inner leg is angled towards the outer leg
so the jaws are preloaded (TIP_GAP at rest); a flared lip at the tip guides notes in.
In-use orientation = print orientation: the U lies flat on the bed, so the spring bends WITHIN the
layers (perimeters run around the U) - no layer lines across the bend.
Clamp range: 5 folded notes ~1 mm, 20 folded notes ~4 mm (0.1 mm paper, folded = 2 sheets).

Fatigue note: at 4 mm opening the bending strain in each leg is ~0.3 % (ABS yield ~2-3 %), so the clip
should survive thousands of cycles. ABS creeps if left fully open (stack > 4 mm) for weeks and loses
preload; heat (car dashboard > 80 C) relaxes it. Reprint or reduce MAX_OPEN use if it gets loose.
Assumptions: notes folded once; plain ABS+ strength; 100 % solid via strong process + thin legs.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # U flat on the bed: spring bends within layers
    supports="off",
    brim="auto",
)

# Parameters
CLIP_L = 55.0          # overall length
CLIP_W = 25.0          # clip width (Z, print height)
LEG_T = 1.6            # leg / spring thickness (4 perimeters)
BEND_RI = 2.6          # inner radius of the U bend (sets max open gap at the root)
TIP_GAP = 0.4          # preload gap between jaws at rest
LIP_L = 6.0            # flared lead-in lip on the inner leg
LIP_ANGLE = 25.0       # deg, flare away from the outer leg
EDGE_CHAMFER = 0.4     # bed elephant-foot relief height (inset by half of it)

BEND_RO = BEND_RI + LEG_T
LEG_L = CLIP_L - BEND_RO - LIP_L * 0.9


def build() -> Part:
    import math
    # bend: half annulus on -X side
    ring = Circle(BEND_RO) - Circle(BEND_RI)
    bend = ring - Pos(BEND_RO, 0) * Rectangle(2 * BEND_RO, 3 * BEND_RO)
    # outer leg (top, straight)
    top = Pos((CLIP_L - BEND_RO) / 2, BEND_RI + LEG_T / 2) * Rectangle(CLIP_L - BEND_RO, LEG_T)
    # inner leg (bottom) angled up so the jaw closes to TIP_GAP
    rise = 2 * BEND_RI - TIP_GAP
    ang = math.degrees(math.atan2(rise, LEG_L))
    leg_len = math.hypot(rise, LEG_L)
    leg = Pos(leg_len / 2, -LEG_T / 2) * Rectangle(leg_len, LEG_T)
    leg = Pos(0, -BEND_RI) * Rot(0, 0, ang) * leg
    tip = Pos(LEG_L, -BEND_RI + rise)
    lip = Pos(LIP_L / 2, -LEG_T / 2) * Rectangle(LIP_L, LEG_T)
    lip = tip * Rot(0, 0, -LIP_ANGLE) * lip
    knee = tip * Pos(0, -LEG_T / 2) * Circle(LEG_T / 2)
    root = Pos(0, -BEND_RI - LEG_T / 2) * Circle(LEG_T / 2)
    prof = bend + top + leg + lip + knee + root
    # elephant-foot relief: first EDGE_CHAMFER mm inset (a chamfer fails on this profile)
    clip = extrude(offset(prof, -EDGE_CHAMFER / 2), EDGE_CHAMFER)
    clip += Pos(0, 0, EDGE_CHAMFER) * extrude(prof, CLIP_W - EDGE_CHAMFER)
    return clip
