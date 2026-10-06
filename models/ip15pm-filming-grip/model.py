"""ip15pm-filming-grip: hand grip for the ip15pm-tripod-clamp with two cold shoes.

Spec: a 120 x 35 x 14 mm top platform on an octagonal 35 mm handle (110 mm long, lanyard hole).
The ip15pm-tripod-clamp (holding the iPhone 15 Pro Max in landscape) is bolted on top with a
1/4"-20 screw from below (head in a counterbore beside the handle, 6 mm of thread protrudes into
the clamp's nut). Two cold shoes cut flush into the platform (left end, and right end above the
handle) take a mic and a light; their feet slide in from the back (+Y) against a front stop.
The phone itself only touches the clamp, so its buttons/ports/camera are as clear as the clamp
leaves them.

Print: on its front face (-Y down): every profile is extruded vertically, the cold-shoe dovetails
need no support, and the handle-to-platform joint bends within the layers (strong). The 1/4"
hole is a teardrop.

Assumptions:
- 1/4"-20 x 3/4" (19 mm) screw, head <= 12 mm (thumb screw or socket cap).
- Standard cold-shoe foot 18 x 18 x 2 mm.
- Clamp base footprint 30 x 35 mm (ip15pm-tripod-clamp); a 1 mm rubber pad between clamp and
  platform stops it rotating. Hand-held load ~ phone 251 g + clamp 50 g + mic/light 2 x 100 g.

MEASURE BEFORE PRINTING (unverified values):
- SCREW_LEN / SCREW_HEAD_D: your 1/4"-20 screw (PROTRUDE must stay < clamp nut depth ~8 mm).
- CS_FOOT_W / CS_FOOT_T: cold-shoe feet of your mic/light.
- GRIP_AF: hand size (35 mm across flats suits most hands; changing it also changes PLAT_D).
"""

from build123d import *

from cadlib import *

# Accessories
SCREW14_D = 6.6
SCREW_LEN = 19.0
SCREW_HEAD_D = 12.5
PROTRUDE = 6.0
CS_FOOT_W, CS_FOOT_T = 18.0, 2.0
CLAMP_G, PHONE_G, ACC_G = 50, 251, 100

# Grip
PLAT_L, PLAT_D, PLAT_T = 120.0, 35.0, 14.0
GRIP_AF = PLAT_D             # same as the platform: both lie flat on the bed
GRIP_L = 110.0
GRIP_X = 40.0
SCREW_X = -2.0
SHOE_X = (-44.0, GRIP_X)
CS_W, CS_L = 24.0, 20.0
LANYARD_D = 5.0

CAV_W = CS_FOOT_W + 0.6
TOP = GRIP_L + PLAT_T

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[dict(at=(SCREW_X, 0, TOP + 50), grams=CLAMP_G + PHONE_G),
           dict(at=(SHOE_X[0], 0, TOP + 30), grams=ACC_G),
           dict(at=(SHOE_X[1], 0, TOP + 30), grams=ACC_G)],
    print_orientation=(90, 0, 0),   # front face (-Y) on the bed
    supports="auto",
    brim="on",                 # ABS, 120 x 124 mm L-shaped footprint on the bed
)


def build() -> Part:
    plat = Pos(0, 0, GRIP_L) * Box(PLAT_L, PLAT_D, PLAT_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    plat = fillet(plat.edges().filter_by(Axis.Y), 4)
    grip = Pos(GRIP_X, 0, 0) * extrude(RegularPolygon(GRIP_AF / 2, 8, major_radius=False, rotation=22.5), GRIP_L + 1)
    part = plat + grip
    part = part - Pos(GRIP_X, 0, 12) * Rot(90, 0, 0) * Cylinder(LANYARD_D / 2, 2 * GRIP_AF)
    # 1/4"-20 screw from below, head in a counterbore
    floor = SCREW_LEN - PROTRUDE
    vert = Rot(0, 0, 90) * Rot(0, 90, 0)          # vertical teardrop, tip towards +Y (print up)
    part = part - Pos(SCREW_X, 0, TOP) * vert * teardrop_hole(SCREW14_D, 2 * PLAT_T + 2, along="X")
    part = part - Pos(SCREW_X, 0, GRIP_L) * vert * teardrop_hole(SCREW_HEAD_D, 2 * (PLAT_T - floor), along="X")
    # cold shoes: dovetail cavity, open towards +Y, 3 mm stop at -Y
    h = CS_FOOT_T + 0.4
    prof = Polygon((-CAV_W / 2, 0), (CAV_W / 2, 0), (CAV_W / 2, h), (CAV_W / 2 - 3, h + 3), (CAV_W / 2 - 3, 10),
                   (-CAV_W / 2 + 3, 10), (-CAV_W / 2 + 3, h + 3), (-CAV_W / 2, h), align=None)
    cav = extrude(Plane.XZ * prof, PLAT_D - 2)           # towards -Y, leaves a 3 mm stop
    for x in SHOE_X:
        part = part - Pos(x, PLAT_D / 2 + 1, TOP - (h + 3 + 2)) * cav
    return part
