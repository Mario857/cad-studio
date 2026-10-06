"""bottle-trap-funnel: funnel insert turning a cut-off 2 L PET bottle (90 mm OD) into a stink-bug trap.

Spec: 45 deg funnel wall, 80 mm mouth, 18 mm throat, flange OD 100 resting on the cut bottle rim,
3 arms (45 deg, lean inward) holding a 30 mm bait/lure cup ring above the mouth, 2 hang holes in flange.
In-use orientation: flange at top (z=0..10), funnel hangs below (z<0), cup ring above.
Assumptions: printed as modelled (throat on bed, flange up) because arms/cup sit on the other side of
the mouth, so "mouth on bed" is impossible; flange underside is a 45 deg chamfer (no support needed).
Cup: 30 mm OD, ring ID 31, 8 mm deep with a 3 mm wide ledge. Funnel wall 2.4 mm horizontal.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="auto",
)

MOUTH_D = 80.0
THROAT_D = 18.0
WALL = 2.4
FLANGE_D = 100.0
FL_T = 2.4
CUP_D = 30.0
CUP_CLR = 1.0
RING_WALL = 2.4
RING_H = 8.0
LEDGE = 2.0
ARM_T = 6.0
ARM_W = 5.0
ARM_ANGLES = (0, 120, 240)
HANG_ANGLES = (60, 180)
HANG_D = 4.5
HANG_R = 46.2

FL_TOP = FLANGE_D / 2 - MOUTH_D / 2 - WALL + FL_T   # flange underside is a 45 deg chamfer
FUN_H = (MOUTH_D - THROAT_D) / 2                    # 45 deg
RING_ID = CUP_D + CUP_CLR
RING_OR = RING_ID / 2 + RING_WALL
ARM_Z0 = FL_TOP - 3.3
ARM_Z1 = ARM_Z0 + 22.5


def build() -> Part:
    ri_m, ri_t = MOUTH_D / 2, THROAT_D / 2
    zf = FLANGE_D / 2 - ri_m - WALL
    pts = [(ri_t, -FUN_H), (ri_t + WALL, -FUN_H), (ri_m + WALL, 0), (FLANGE_D / 2, zf),
           (FLANGE_D / 2, FL_TOP), (ri_m, FL_TOP), (ri_m, 0)]
    prof = Polygon(*pts[::-1], align=None)   # clockwise in XZ plane -> valid revolve orientation
    body = revolve(Plane.XZ * prof, Axis.Z, 360)

    d = ARM_W * 1.4142
    zt = ARM_Z1 + 4.0
    xin = lambda z: RING_OR - 1.0 + (ARM_Z1 + 2 - z)   # inner edge, 45 deg
    arm2d = Polygon((xin(ARM_Z0) + d, ARM_Z0), (xin(ARM_Z0), ARM_Z0),
                    (xin(zt), zt), (xin(zt) + d, zt), align=None)

    arms = Pos(0, 0, ARM_Z1) * Cylinder(RING_OR, RING_H, align=ON_BED)
    for a in ARM_ANGLES:
        arms = arms + extrude(Plane.XZ.rotated((0, 0, a)) * arm2d, ARM_T / 2, both=True)
    part = body + arms
    # cup bore with ledge
    sk = RING_OR - (RING_ID / 2 - 3.0)
    part = part + Pos(0, 0, ARM_Z1 - sk) * Cone(RING_ID / 2 - 3.0, RING_OR, sk, align=ON_BED)   # 45 deg underside
    part = part - Pos(0, 0, ARM_Z1 + LEDGE) * Cylinder(RING_ID / 2, RING_H, align=ON_BED)
    part = part - Pos(0, 0, ARM_Z1 - sk - 1) * Cylinder(RING_ID / 2 - 4.5, RING_H + sk + 1, align=ON_BED)

    for a in HANG_ANGLES:
        part = part - Rot(0, 0, a) * (Pos(HANG_R, 0, 0) * Cylinder(HANG_D / 2, 20, align=ON_BED))
    return part
