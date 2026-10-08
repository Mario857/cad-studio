"""curtain-rod-hook-tab: screw-mounted hook with a rigid back and one long spring tab in front.

Spec: version 4 of 5 window curtain-rod hooks (print 2 per window: left + right are identical).
- Mount: 2 countersunk 3.5 x 16 mm self-tapping screws, 4 mm base.
- Retention: the back of the mouth is rigid; the front of the cup is a single spring tab - the
  ring's front half, tied to the base only at the bottom, so it bends over a ~17 mm arc. The mouth
  is 1.2 mm narrower than the rod: push the rod down, the leaning thumb fin acts as a funnel, the
  tab springs 1.2 mm forward (~1.5 % strain in ASA) and clicks back over the rod.
- Release without force on the screws: hook a finger behind the thumb fin, pull it forward
  ~1.5 mm and lift the rod out.
Print: on its side so the tab bends within the layers, no supports.
Assumptions: rod 10 mm, rod axis 15 mm from the frame face.
OpenSCAD twin: curtain-rod-hook-tab.scad (same parameters; MOUNT = "screw" | "vhb").
"""

from build123d import *

from cadlib import *

META = dict(
    material="ASA",
    quality="strong",          # 4 walls: 2.4 mm flex lips print as solid perimeters
    standing=False,
    loads=[],
    print_orientation=(0, -90, 0),
    supports="off",
    brim="auto",
    copies=2,
)

# Parameters
ROD_D = 10.0
ROD_CLEAR = 1.5
ROD_OFFSET = 15.0
SNAP = 1.2           # mouth is this much narrower than the rod (all taken by the front tab)
BACK_LIP = 0.75      # rigid back edge overlaps the bore by this much
WIDTH = 14.0
BASE_T = 4.0
WALL = 2.4
BAR_T = 3.0
FIN_T = 2.4          # thumb fin thickness
FIN_TOP = 9.5        # fin top above the rod axis
FIN_LEAN = 3.0       # forward lean of the fin (funnel + finger grip)
SCREW_HOLE = 3.9
CSK_D = 7.2
SCREW_EDGE = 6.0
ACCESS = 4.5
CHAMFER = 0.4

R_IN = (ROD_D + ROD_CLEAR) / 2
R_OUT = R_IN + WALL
D = ROD_OFFSET
ZC = SCREW_EDGE + ACCESS + R_OUT
Y_B = D - R_IN + BACK_LIP                   # rigid back edge of the mouth
Y_N = Y_B + ROD_D - SNAP                    # tab tip (relaxed)
Z_BACK = ZC + 6.0                           # back block top
Z_SCREWS = (SCREW_EDGE, ZC + FIN_TOP + ACCESS)
HEIGHT = Z_SCREWS[1] + SCREW_EDGE


def rect(y0, y1, z0, z1):
    return Pos((y0 + y1) / 2, (z0 + z1) / 2) * Rectangle(y1 - y0, z1 - z0)


def poly(*pts):
    return Polygon(*pts, align=None)


def tear(r):
    return Circle(r) + Pos(r * 0.7071, 0) * Rot(0, 0, 45) * Rectangle(r, r)


def csk_hole(x, z):
    r = SCREW_HOLE / 2
    hole = extrude(Plane.XZ * tear(r), 40, both=True)
    h = (CSK_D - SCREW_HOLE) / 2
    cone = Rot(-90, 0, 0) * Cone(r, CSK_D / 2, h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cone += Pos(0, h, 0) * Rot(-90, 0, 0) * Cylinder(CSK_D / 2, 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Pos(x, 0, z) * (hole + Pos(0, BASE_T - h, 0) * cone)


def bed_chamfer(part):
    for c in (CHAMFER, 0.3, 0.2):
        try:
            return chamfer(part.faces().sort_by(Axis.X)[0].edges(), c)
        except ValueError:
            pass
    return part


def build() -> Part:
    prof = rect(0, BASE_T, 0, HEIGHT)
    prof += rect(0, D, ZC - R_OUT, ZC - R_OUT + BAR_T)
    prof += rect(0, Y_B, ZC - R_OUT, Z_BACK)
    prof += Pos(D, ZC) * Circle(R_OUT)
    z_tip = ZC + 4.4
    prof += poly((Y_N, z_tip), (Y_N + FIN_T + 0.3, z_tip - 0.4),
                 (Y_N + FIN_T + 0.3 + FIN_LEAN, ZC + FIN_TOP), (Y_N + FIN_LEAN, ZC + FIN_TOP))
    prof -= Pos(D, ZC) * Circle(R_IN)
    prof -= rect(Y_B, Y_N, ZC, ZC + FIN_TOP + 1)
    prof -= rect(BASE_T, Y_B + 0.01, Z_BACK, ZC + R_OUT + 1)
    prof -= poly((Y_B - 2, Z_BACK + 0.01), (Y_B + 0.01, Z_BACK + 0.01), (Y_B + 0.01, Z_BACK - 2))
    part = bed_chamfer(extrude(Plane.YZ * prof, WIDTH))
    for z in Z_SCREWS:
        part -= csk_hole(WIDTH / 2, z)
    return part
