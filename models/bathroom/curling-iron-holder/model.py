"""curling-iron-holder: wall-mounted holder with 2 ventilated holsters + cable horns.

Spec: back plate screwed to the wall with 3 countersunk M4 screws (2 above the holsters,
1 low in the centre). Two vertical holsters (HOLSTER_D = 40 mm bore) for a curling iron and a
hair straightener: open at the bottom (a 45 deg internal funnel narrows the exit to
BOTTOM_OPEN_D so the tool tip rests on it while air, hair and dust fall through), 45 deg flared
mouth on top, and vertical diamond-ended ventilation slots (45 deg pointed ends -> no supports)
around the front half of each tube. Between the holsters, two horns with upturned lips for
winding the cables (figure-8 around upper + lower horn).

Print orientation (0, 0, 0) = as mounted, plate standing on its bottom edge. Chosen for
strength: the tool weight (~500 g each) bends the holster/web off the wall plate about the X
axis; the resulting tension/compression runs along Y (away from the wall), which lies in the
layer plane, and the screw pull-out load runs along Y through the plate too. Printed lying on
its back, those stresses would instead pull layers apart. It also prints support-free: tubes
are vertical, flares and horn undersides are 45 deg, slot ends are pointed.

SAFETY: let the tools cool to under ~90 C before holstering - ABS softens around 95-100 C, and
a hot barrel (150-230 C) will deform the holster. Hot-holstering is not supported.

Assumptions: tool tips are wider than BOTTOM_OPEN_D (22 mm) so they rest on the funnel
(curling-iron barrels with a cool tip and closed straighteners are ~25-35 mm); total load 1 kg;
screws M4 countersunk wood/plug screws (~30-40 mm) into wall plugs.
Hardware: 3x M4 countersunk screws + 3 wall plugs.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[dict(at=(-45.2, 37.2, 60.0), grams=500), dict(at=(45.2, 37.2, 60.0), grams=500)],
    print_orientation=(0, 0, 0),
    supports="auto",
    brim="auto",
)

# Parameters
HOLSTER_D = 40.0          # holster bore
HOLSTER_WALL = 3.2
HOLSTER_H = 110.0
BOTTOM_OPEN_D = 22.0      # exit hole at bottom (tool tip rests on 45 deg funnel)
FLARE = 6.0               # mouth flare (radial = vertical, 45 deg)
STANDOFF = 8.0            # gap between plate front and holster outer wall
WEB_W = 24.0              # width of the web joining holster to plate
CABLE_GAP = 32.0          # clear width between the two holster flares (horn column)

PLATE_T = 6.0
PLATE_H = 140.0
PLATE_R = 6.0             # plate corner radius (front view)

SCREW = "M4"
SCREW_TOP_Z = 126.0
SCREW_BOTTOM_Z = 14.0

SLOT_W = 6.0
SLOT_Z0 = 16.0            # slot bottom tip
SLOT_Z1 = HOLSTER_H - FLARE - 10.0
SLOT_ANGLES = (-90, -60, -30, 0, 30, 60, 90)  # deg around tube, 0 = facing away from wall

HORN_W = 12.0
HORN_L = 30.0             # horn length from plate front to inner face of the lip
HORN_T = 6.0              # horn thickness / lip thickness
HORN_LIP = 8.0            # upturned lip height
HORN_TOP_Z = (70.0, 118.0)

R_IN = HOLSTER_D / 2
R_OUT = R_IN + HOLSTER_WALL
HOLSTER_Y = PLATE_T + STANDOFF + R_OUT
HOLSTER_X = R_OUT + FLARE + CABLE_GAP / 2
PLATE_W = 2 * (HOLSTER_X + R_OUT + FLARE)


def _holster_solid(x):
    tube = Pos(x, HOLSTER_Y, 0) * Cylinder(R_OUT, HOLSTER_H - FLARE, align=ON_BED)
    flare = Pos(x, HOLSTER_Y, HOLSTER_H - FLARE) * Cone(
        R_OUT, R_OUT + FLARE, FLARE, align=ON_BED)
    web = Pos(x, (PLATE_T + HOLSTER_Y) / 2, 0) * Box(
        WEB_W, HOLSTER_Y - PLATE_T + 0.5, HOLSTER_H - FLARE, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return tube + flare + web


def _holster_cut(x):
    funnel_h = R_IN - BOTTOM_OPEN_D / 2
    eps = 0.5
    funnel = Pos(x, HOLSTER_Y, -eps) * Cone(
        BOTTOM_OPEN_D / 2 - eps, R_IN, funnel_h + eps, align=ON_BED)
    bore = Pos(x, HOLSTER_Y, funnel_h) * Cylinder(R_IN, HOLSTER_H - FLARE - funnel_h + 0.01, align=ON_BED)
    mouth = Pos(x, HOLSTER_Y, HOLSTER_H - FLARE) * Cone(R_IN, R_IN + FLARE + eps, FLARE + eps, align=ON_BED)
    cut = funnel + bore + mouth
    # diamond-ended vertical slot, drawn in XZ, extruded radially (along +Y)
    h = SLOT_W / 2
    prof = Polygon((0, SLOT_Z0), (h, SLOT_Z0 + h), (h, SLOT_Z1 - h), (0, SLOT_Z1),
                   (-h, SLOT_Z1 - h), (-h, SLOT_Z0 + h), align=None)
    slot = extrude(Plane.XZ * prof, -(R_OUT + 2))  # Plane.XZ normal is -Y; negative -> +Y
    for a in SLOT_ANGLES:
        cut += Pos(x, HOLSTER_Y, 0) * Rot(0, 0, a) * slot
    return cut


def _horn(z_top):
    L, T = HORN_L, HORN_T
    prof = Polygon(
        (0, z_top - T - (L + T)), (L + T, z_top - T), (L + T, z_top + HORN_LIP),
        (L, z_top + HORN_LIP), (L, z_top), (0, z_top), align=None)
    # YZ plane: local x = +Y, local y = +Z; extrude along X
    h = extrude(Plane.YZ * prof, HORN_W / 2, both=True)
    return Pos(0, PLATE_T - 0.5, 0) * h


def build() -> Part:
    plate_sk = RectangleRounded(PLATE_W, PLATE_H, PLATE_R)
    plate = Pos(0, 0, PLATE_H / 2) * extrude(Plane.XZ * plate_sk, -PLATE_T)  # y 0..PLATE_T
    part = plate
    for x in (-HOLSTER_X, HOLSTER_X):
        part += _holster_solid(x)
    for z in HORN_TOP_Z:
        part += _horn(z)
    for x in (-HOLSTER_X, HOLSTER_X):
        part -= _holster_cut(x)
    screw = Rot(-90, 0, 0) * bolt_hole(SCREW, PLATE_T + 1, head="csk")  # head on front face
    for (x, z) in ((-HOLSTER_X, SCREW_TOP_Z), (HOLSTER_X, SCREW_TOP_Z), (0, SCREW_BOTTOM_Z)):
        part -= Pos(x, PLATE_T, z) * screw
    try:
        part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    except Exception:
        pass
    return part
