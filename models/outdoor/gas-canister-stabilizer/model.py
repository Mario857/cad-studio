"""gas-canister-stabilizer: clip-on tripod leg for a screw-on stove gas canister (print 3).

Spec: three identical flat legs. Each leg has a curved "head" with a groove that the canister's
bottom rim drops into (outer wall hugs the canister body, inner nub sits in the concave base),
and a flat arm running radially outward to a round foot pad. Set the canister down onto the three
heads spaced ~120 deg apart: the rim is trapped laterally in the three grooves, the canister rests
on the legs, and the footprint grows to Ø 2 x CAN_D (220 mm for a 230 g canister).
Legs are flat (stack/nest flat in the pot or a pocket), printed flat = in-use orientation, so the
bending load from a tipping stove runs along the layers.

SAFETY: keep it away from the flame. The legs only touch the cool canister base at ground level;
never use under a remote-canister / inverted-canister stove, never let a windscreen trap heat
around the canister, and do not use as a pot support. ABS softens around 90-100 C.

Assumptions:
- Default canister = 230 g class (Ø 110 mm body). For 100 g (Ø 90) set CAN_D = 90.0
  (footprint becomes 180 mm). 450 g canisters are ~Ø 110 too but taller - works, less stable.
- The rim the canister stands on is within RIM_W (4.5 mm) inside the body diameter and the
  concave base recess is ≥ NUB_H + 1 mm deep (typical Lindal-valve canisters: 5-8 mm).
- Grip is by geometry (rim trapped in the grooves of 3 legs) plus slight friction, not a snap;
  slide fit RIM_CLR each side.
- Stove + pot + water on top ≤ ~2 kg; arm 4 mm thick with 2 x 4 mm side rails is ample.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,            # single leg is not free-standing; the assembled tripod is
    loads=[],
    print_orientation=(0, 0, 0),  # flat, as used: loads run along the layers
    supports="off",
    brim="auto",
    copies=3,
)

# --- Canister (choose one) ---
CAN_D = 110.0          # 230 g canister body Ø (100 g: 90.0)
RIM_W = 4.5            # rim / seam zone width inside the body diameter
RIM_CLR = 0.4          # clearance each side of the rim in the groove

# --- Leg ---
FOOT_R = CAN_D         # foot centre radius -> footprint Ø 2 x CAN_D
T = 4.0                # plate / arm thickness (loaded)
ARM_W = 16.0           # arm width
ARM_SLOT_W = 8.0       # lightening slot width (leaves 4 mm rails)
FOOT_D = 26.0          # foot pad Ø
FOOT_HOLE_D = 10.0     # lightening hole in foot pad (also a peg/stake hole)
HEAD_ANG = 32.0        # angular span of the head (deg)
HEAD_IN = 12.0         # head plate extends this far inside the rim
WALL_T = 3.0           # outer wall thickness (loaded, hugs canister)
WALL_H = 10.0          # outer wall height above the plate
NUB_T = 3.0            # inner nub radial thickness
NUB_H = 3.0            # inner nub height (sits in concave base)
LEAD = 1.5             # lead-in chamfer on the groove edges

R_BODY = CAN_D / 2
R_WALL_IN = R_BODY + RIM_CLR
R_WALL_OUT = R_WALL_IN + WALL_T
R_NUB_OUT = R_BODY - RIM_W - RIM_CLR
R_NUB_IN = R_NUB_OUT - NUB_T
R_HEAD_IN = R_BODY - RIM_W - HEAD_IN


def _sector(r_in, r_out, h, z0=0.0):
    ring = Cylinder(r_out, h, align=ON_BED) - Cylinder(r_in, h, align=ON_BED)
    L = 2 * r_out
    y = L * math.tan(math.radians(HEAD_ANG / 2))
    wedge = extrude(Polygon((0, 0), (L, -y), (L, y), align=None), h)
    return Pos(0, 0, z0) * (ring & wedge)


def build() -> Part:
    # head plate
    head = _sector(R_HEAD_IN, R_WALL_OUT, T)
    # arm from inside the head to the foot
    arm_x0 = R_HEAD_IN + 4
    arm = Pos((arm_x0 + FOOT_R) / 2, 0, 0) * Box(FOOT_R - arm_x0, ARM_W, T, align=ON_BED)
    foot = Pos(FOOT_R, 0, 0) * Cylinder(FOOT_D / 2, T, align=ON_BED)
    leg = head + arm + foot
    leg = chamfer(leg.edges().group_by(Axis.Z)[0], 0.4)

    # outer wall + inner nub
    wall = _sector(R_WALL_IN, R_WALL_OUT, WALL_H, T)
    wall = chamfer(wall.edges().group_by(Axis.Z)[-1].filter_by(GeomType.CIRCLE)
                   .sort_by(SortBy.RADIUS)[0], LEAD)
    nub = _sector(R_NUB_IN, R_NUB_OUT, NUB_H, T)
    nub = chamfer(nub.edges().group_by(Axis.Z)[-1].filter_by(GeomType.CIRCLE)
                  .sort_by(SortBy.RADIUS)[-1], 1.0)
    leg = leg + wall + nub

    # lightening
    s0 = R_WALL_OUT + 6
    s1 = FOOT_R - FOOT_D / 2 - 3
    leg = leg - Pos((s0 + s1) / 2, 0, T) * slot(s1 - s0, ARM_SLOT_W, T)
    leg = leg - Pos(FOOT_R, 0, 0) * Cylinder(FOOT_HOLE_D / 2, T, align=ON_BED)
    return leg
