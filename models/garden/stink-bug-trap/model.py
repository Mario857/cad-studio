"""stink-bug-trap: light-attracted funnel trap for brown marmorated stink bugs (no poison).

Spec: 3 parts. Basin (OD 120 x 65, fill ~20 mm with soapy water), lid (plate on the basin rim,
3 arms rising at ~40 deg to a hub with an LED-tealight pocket = carry handle) and a funnel that
drops through the lid (flange rests on the plate; 45 deg wall, 92 mm mouth, 16 mm throat ending
~20 mm above the floor so bugs fall into the water and cannot climb out).
Bugs fly to the light above the mouth, drop through the funnel and drown.
Layout: all parts are laid out side by side exactly as printed (zero supports). The funnel is
shown printed mouth-down; in use it is flipped (throat down) and sits in the lid hole.
Assumptions: ABS+ (AzureFilm), LED tealight d 38 x 14 mm, water + dish soap, indoor/sheltered use.
Known: ~2 cm2 of tree support remains (accepted; slicer adds it automatically).
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,            # parts are laid out for printing, not as assembled
    loads=[],
    print_orientation=(0, 0, 0),
    supports="auto",
    brim="auto",
)

# Parameters
BASIN_R = 60.0
BASIN_H = 65.0
WALL = 2.4
FLOOR = 3.0
PLATE_T = 3.0
MOUTH_R = 46.0         # funnel mouth radius (inner)
THROAT_R = 8.0         # funnel throat radius (inner)
FUNNEL_WALL = 4.0      # horizontal wall thickness (2.8 mm normal at 45 deg)
FLANGE_T = 2.4
FLANGE_R = 54.0
THROAT_LEN = 6.0
HOLE_CLEAR = 0.4
ARM_W = 6.0
ARM_FOOT_R0 = 55.5
ARM_FOOT_R1 = 59.5
HUB_R = 23.0
HUB_Z = 41.0           # hub cylinder bottom
HUB_H = 8.0
LIGHT_D = 38.0
LIGHT_POCKET_D = hole_d(LIGHT_D)
LIGHT_POCKET_DEPTH = 6.0
GAP = 12.0


def basin() -> Part:
    body = Cylinder(BASIN_R, BASIN_H, align=ON_BED)
    body = chamfer(body.edges().group_by(Axis.Z)[0], 0.4)
    cavity = Pos(0, 0, FLOOR) * Cylinder(BASIN_R - WALL, BASIN_H, align=ON_BED)
    return body - cavity


def lid() -> Part:
    plate = chamfer(Cylinder(BASIN_R, PLATE_T, align=ON_BED).edges().group_by(Axis.Z)[0], 0.4)
    plate -= Cylinder(MOUTH_R + FUNNEL_WALL + HOLE_CLEAR, PLATE_T + 1, align=ON_BED)

    # Hub: 45 deg cone underneath (no flat ceiling) + cylinder with the light pocket.
    cone_h = HUB_R - 8.0
    hub = Pos(0, 0, HUB_Z) * Cylinder(HUB_R, HUB_H, align=ON_BED)
    hub += Pos(0, 0, HUB_Z - cone_h) * Cone(8.0, HUB_R, cone_h, align=ON_BED)
    hub -= Pos(0, 0, HUB_Z + HUB_H - LIGHT_POCKET_DEPTH) * Cylinder(
        LIGHT_POCKET_D / 2, LIGHT_POCKET_DEPTH + 1, align=ON_BED)

    arm_profile = Polygon(
        (ARM_FOOT_R0, PLATE_T - 0.5), (ARM_FOOT_R1, PLATE_T - 0.5),
        (HUB_R + 1, HUB_Z + 3), (HUB_R - 5, HUB_Z + 3),
        align=None,
    )
    arm = extrude(Plane.XZ * arm_profile, ARM_W / 2, both=True)
    arms = arm + Rot(0, 0, 120) * arm + Rot(0, 0, 240) * arm
    return plate + hub + arms


def funnel() -> Part:
    """As printed: flange + wide mouth on the bed, 45 deg wall narrowing upward, throat tube on top."""
    drop = MOUTH_R - THROAT_R
    outer = MOUTH_R + FUNNEL_WALL
    profile = Polygon(
        (MOUTH_R, 0), (FLANGE_R, 0), (FLANGE_R, FLANGE_T), (outer, FLANGE_T),
        (THROAT_R + FUNNEL_WALL, FLANGE_T + drop - FUNNEL_WALL * 0 ),
        (THROAT_R + FUNNEL_WALL, FLANGE_T + drop + THROAT_LEN),
        (THROAT_R, FLANGE_T + drop + THROAT_LEN), (THROAT_R, FLANGE_T + drop),
        align=None,
    )
    return revolve(Plane.XZ * profile, Axis.Z, 360)


def build():
    return [
        Pos(-(BASIN_R + GAP / 2), 0, 0) * basin(),
        Pos(BASIN_R + GAP / 2, 0, 0) * lid(),
        Pos(BASIN_R + GAP / 2, BASIN_R + FLANGE_R + GAP, 0) * funnel(),
    ]
