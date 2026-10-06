"""mug-tree: 6-mug tree, stable without a weighted base.

Spec: 28 mm post, 6 round arms (12 mm) on two levels of 3 (120 deg apart, levels offset
60 deg, 105 mm apart so hanging mugs never touch). Arms rise at 50 deg so they print
without supports and mugs slide to the root. Base = 6 radial gussets ending in 24 mm
round feet on a 210 mm circle: wide stance, little plastic, small ABS warp areas.
Assumptions: mugs up to 90 mm dia x 100 mm tall, handle opening >= 16 mm, 350 g each.
Even one mug alone stays inside the foot circle (lowest stability case).
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 0, 150), grams=6 * 350)],
    print_orientation="auto",
    supports="auto",
    brim="auto",
)

# Parameters
POST_R = 14.0
ARM_R = 6.0
ARM_L = 75.0
ARM_ELEV = 50.0        # deg above horizontal
LEVEL_Z = (125.0, 230.0)
ARMS_PER_LEVEL = 3
FOOT_CIRCLE_R = 105.0
FOOT_R = 12.0
FOOT_T = 3.0
LEG_H = 40.0           # gusset height at the post
LEG_T = 8.0


def build() -> Part:
    import math
    top_z = LEVEL_Z[-1] + ARM_L * math.sin(math.radians(ARM_ELEV)) - 5
    post = Cylinder(POST_R, top_z, align=ON_BED)
    post = fillet(post.edges().group_by(Axis.Z)[-1], POST_R / 2)
    part = post
    arm = Cylinder(ARM_R, ARM_L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    arm = fillet(arm.edges().group_by(Axis.Z)[-1], ARM_R * 0.6)
    arm = Rot(0, 90 - ARM_ELEV, 0) * arm
    for lvl, z in enumerate(LEVEL_Z):
        for i in range(ARMS_PER_LEVEL):
            a = i * 360 / ARMS_PER_LEVEL + lvl * 180 / ARMS_PER_LEVEL
            part += Pos(0, 0, z) * Rot(0, 0, a) * arm
    # base: radial gussets + round feet
    leg = rib(FOOT_CIRCLE_R, LEG_H, LEG_T)
    for i in range(6):
        a = i * 60 + 30
        part += Rot(0, 0, a) * leg
        part += Rot(0, 0, a) * Pos(FOOT_CIRCLE_R, 0, 0) * Cylinder(FOOT_R, FOOT_T, align=ON_BED)
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    return part
