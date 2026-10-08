"""curtain-rod-hook-snap: screw-mounted J-hook whose C-ring snaps over a pen-sized curtain rod.

Spec: version 1 of 5 window curtain-rod hooks (print 2 per window: left + right are identical).
- Mounts on the face of a PVC/uPVC window frame with 2 countersunk 3.5 x 16 mm self-tapping
  screws stacked vertically (narrow 14 mm base fits frames >= 16 mm wide). 4 mm base -> ~12 mm
  of screw in the frame: bites the outer PVC wall, stays clear of the steel core.
- Retention: the cup is a C-ring whose mouth (8.8 mm) is 1.2 mm narrower than the rod. Press the
  rod down through the funnel: the ring lips spread and click shut. The ring is tied to the base
  only along its back-bottom, so the front lip flexes over a ~17 mm arc (~1.2 % strain in ASA,
  well inside its ~3 % yield). Pull up firmly to remove.
- Bore = rod + 1.5 mm clearance: the rod turns and slides freely.
Print: on its side (profile flat on the bed) so every layer contains the whole hook curve and
the snap lips flex in-plane, never across layer lines. No supports.
Assumptions: rod 10 mm (set ROD_D for 8-9 mm rods), rod axis 15 mm in front of the frame face.
OpenSCAD twin: curtain-rod-hook-snap.scad (same parameters; MOUNT = "screw" | "vhb").
"""

from build123d import *

from cadlib import *

META = dict(
    material="ASA",
    quality="strong",          # 4 walls: 2.4 mm flex lips print as solid perimeters
    standing=False,
    loads=[],
    print_orientation=(0, -90, 0),  # x=0 side face on the bed: hook profile lies in the layers
    supports="off",
    brim="auto",
    copies=2,
)

# Parameters
ROD_D = 10.0         # curtain rod diameter
ROD_CLEAR = 1.5      # diametral clearance, rod moves freely
ROD_OFFSET = 15.0    # rod axis -> frame face
SNAP = 1.2           # mouth is this much narrower than the rod
WIDTH = 14.0         # part width along the rod (= base width on the frame)
BASE_T = 4.0         # base plate thickness
WALL = 2.4           # ring wall (6 perimeters)
BAR_T = 3.0          # web tying ring bottom to the base
FUNNEL = 3.0         # 45 deg lead-in above the lips
SCREW_HOLE = 3.9     # clearance for 3.5 mm self-tapping screw
CSK_D = 7.2          # countersink diameter (90 deg head)
SCREW_EDGE = 6.0     # screw axis from base end
ACCESS = 4.5         # screw axis to nearest hook feature (driver clearance)
CHAMFER = 0.4        # elephant-foot chamfer on the bed face

R_IN = (ROD_D + ROD_CLEAR) / 2
R_OUT = R_IN + WALL
D = ROD_OFFSET
ZC = SCREW_EDGE + ACCESS + R_OUT          # rod axis height
Z_SCREWS = (SCREW_EDGE, ZC + R_OUT + ACCESS)
HEIGHT = Z_SCREWS[1] + SCREW_EDGE
MOUTH = ROD_D - SNAP


def rect(y0, y1, z0, z1):
    return Pos((y0 + y1) / 2, (z0 + z1) / 2) * Rectangle(y1 - y0, z1 - z0)


def csk_hole(x, z):
    """Countersunk hole along Y, head at the base front face, teardrop tip toward +X (up in print)."""
    r = SCREW_HOLE / 2
    tear = Circle(r) + Polygon((0, r * 0.7071), (r * 1.4142, 0), (0, -r * 0.7071), align=None)
    hole = extrude(Plane.XZ * tear, 40, both=True)
    h = (CSK_D - SCREW_HOLE) / 2
    cone = Rot(-90, 0, 0) * Cone(r, CSK_D / 2, h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cone += Pos(0, h, 0) * Rot(-90, 0, 0) * Cylinder(CSK_D / 2, 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Pos(x, 0, z) * (hole + Pos(0, BASE_T - h, 0) * cone)


def build() -> Part:
    prof = rect(0, BASE_T, 0, HEIGHT)
    prof += rect(0, D, ZC - R_OUT, ZC - R_OUT + BAR_T)
    prof += Pos(D, ZC) * Circle(R_OUT)
    prof -= Pos(D, ZC) * Circle(R_IN)
    prof -= rect(D - MOUTH / 2, D + MOUTH / 2, ZC, ZC + R_OUT + 1)
    zf = ZC + R_IN * 0.75
    prof -= Polygon((D - MOUTH / 2, zf), (D + MOUTH / 2, zf), (D + MOUTH / 2 + FUNNEL, zf + FUNNEL),
                    (D - MOUTH / 2 - FUNNEL, zf + FUNNEL), align=None)
    part = extrude(Plane.YZ * prof, WIDTH)
    part = chamfer(part.faces().sort_by(Axis.X)[0].edges(), CHAMFER)
    for z in Z_SCREWS:
        part -= csk_hole(WIDTH / 2, z)
    return part
