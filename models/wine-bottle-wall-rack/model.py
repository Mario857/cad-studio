"""wine-bottle-wall-rack: wall rack holding 3 wine bottles horizontally, stacked.

Spec: two identical wall brackets (print copies=2), mounted 150 mm apart (outer). Each is a
6 mm cheek plate reaching 105 mm off the wall, 270 mm tall, with a 32 mm wide back flange
carrying 3 countersunk screws. Each cheek has 3 round seats (R 41) at 92 mm pitch, open to the front-top, so
a bottle is laid in from the front and a front lip keeps it from rolling out. Bottles lie
parallel to the wall (label visible). 6 x countersunk 4-4.5 mm screws + plugs.
Mount both brackets the same way round (flange to the right) at the same height (use a level).
Printed on its side (cheek face on bed) so the cantilevered cheeks are in-plane with the
layers: the bottle load runs along the layers, not across them.
Assumptions: 750 ml bottle up to 82 mm dia, 1.3 kg full; bottle >= 250 mm long so it
spans both cheeks (150 mm apart). Separate brackets avoid a
bridged second cheek when printed flat. Use wall plugs rated for ~5 kg total.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[dict(at=(-3, 55, 50 + i * 92), grams=650) for i in range(3)],
    print_orientation=(0, 90, 0),
    supports="auto",
    brim="auto",
    copies=2,
)

# Parameters
FLANGE_W = 32.0        # back flange width (X), excluding the cheek
HEIGHT = 270.0         # Z
BACK_T = 5.0           # back plate thickness (Y)
CHEEK_T = 6.0          # side cheek thickness (X)
CHEEK_D = 105.0        # cheek depth off the wall (Y)
SEAT_R = 41.0          # bottle seat radius (82 mm bottle)
SEAT_Y = 55.0          # seat centre distance from wall
TIER_PITCH = 92.0
TIER0_Z = 50.0
TIERS = 3
OPEN_H = 45.0          # height of the front-top loading opening above seat centre
SCREW_D = 4.5
SCREW_HEAD_D = 9.0
SCREW_Z = (25.0, 140.0, 255.0)


def build() -> Part:
    # cheek occupies x in [-CHEEK_T, 0]; flange extends toward -X. Print: +X face on the bed.
    back = Box(FLANGE_W + CHEEK_T, BACK_T, HEIGHT, align=(Align.MAX, Align.MIN, Align.MIN))
    cheek_prof = Rectangle(CHEEK_D, HEIGHT, align=(Align.MIN, Align.MIN))
    for i in range(TIERS):
        zc = TIER0_Z + i * TIER_PITCH
        cheek_prof -= Pos(SEAT_Y, zc) * Circle(SEAT_R)
        cheek_prof -= Pos(SEAT_Y - SEAT_R, zc) * Rectangle(200, OPEN_H, align=(Align.MIN, Align.MIN))
    cheek = Pos(-CHEEK_T, 0, 0) * extrude(Plane.YZ * cheek_prof, CHEEK_T)
    part = back + cheek
    part = fillet(part.edges().filter_by(Axis.X).group_by(Axis.Y)[-1], 3.0)

    # countersunk screw holes through the flange (teardrop tip toward -X = up in print)
    sx = -CHEEK_T - FLANGE_W / 2
    for sz in SCREW_Z:
        shank = Rot(0, -90, 0) * teardrop_hole(SCREW_D, BACK_T * 3, along="Y")
        head = Pos(0, BACK_T, 0) * Rot(90, 0, 0) * Cone(
            SCREW_HEAD_D / 2 + 0.5, SCREW_D / 2, (SCREW_HEAD_D - SCREW_D) / 2 + 0.5,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        part -= Pos(sx, 0, sz) * (shank + head)
    part = chamfer(part.edges().group_by(Axis.X)[-1], 0.4)
    return part
