"""curtain-rod-hook-clamp: screw-mounted cup with a screw-secured cap that closes the loop.

Spec: version 3 of 5 window curtain-rod hooks (print 2 sets: left + right are identical).
- Mount: 2 countersunk 3.5 x 16 mm self-tapping screws, both BELOW the cup so nothing sits above
  the cap screw; 4 mm base.
- Open-top cup (bore = rod + 1.5 mm): drop the rod in, then slide the cap on sideways (its front
  hook runs along a ledge on the cup front) and fix its back end with one M3 x 8 screw into an
  M3 heat-set insert (4.0 mm hole) in the hook's back block.
- Retention: a fully closed loop held by a screw - the strongest hold of the set; nothing can
  open it short of breaking the part. CLAMP_PAD sets how much the cap's pad reaches into the bore:
  1.0 (default) leaves the rod free with 0.5 mm play; 1.5 or more grips it so it cannot slide.
Print: hook and cap on their sides, no supports.
Assumptions: rod 10 mm, rod axis 15 mm from the frame face, M3 insert 4.0 x 4 mm.
Two bodies per set (hook + cap) are intended.
OpenSCAD twin: curtain-rod-hook-clamp.scad (same parameters; MOUNT = "screw" | "vhb").
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
WIDTH = 14.0
BASE_T = 4.0
WALL = 2.4
CAP_T = 3.0
CLAMP_PAD = 1.0      # pad depth under the cap (>= ROD_CLEAR grips the rod)
LEDGE = 1.6          # ledge on the cup front the cap hooks under
LEDGE_T = 1.6
HOOK_T = 1.8         # cap front hook wall
CLR = 0.3
INSERT_D = 4.0       # M3 heat-set insert hole
INSERT_DEPTH = 6.0
M3_CLEAR = 3.4
SCREW_HOLE = 3.9
CSK_D = 7.2
SCREW_EDGE = 6.0
SCREW_PITCH = 12.0   # both mount screws below the cup
ACCESS = 4.5
CHAMFER = 0.4

R_IN = (ROD_D + ROD_CLEAR) / 2
R_OUT = R_IN + WALL
D = ROD_OFFSET
Z_SCREWS = (SCREW_EDGE, SCREW_EDGE + SCREW_PITCH)
ZC = Z_SCREWS[1] + ACCESS + R_OUT
Z_WALL = ZC + R_IN
Y_FO = D + R_OUT + 0.4
Y_S = (D - R_IN) / 2                        # cap screw, centred in the back block


def rect(y0, y1, z0, z1):
    return Pos((y0 + y1) / 2, (z0 + z1) / 2) * Rectangle(y1 - y0, z1 - z0)


def tear(r):
    """Teardrop section, tip toward +local x (= +X, up in print)."""
    return Circle(r) + Pos(r * 0.7071, 0) * Rot(0, 0, 45) * Rectangle(r, r)


def csk_hole(x, z):
    r = SCREW_HOLE / 2
    hole = extrude(Plane.XZ * tear(r), 40, both=True)
    h = (CSK_D - SCREW_HOLE) / 2
    cone = Rot(-90, 0, 0) * Cone(r, CSK_D / 2, h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cone += Pos(0, h, 0) * Rot(-90, 0, 0) * Cylinder(CSK_D / 2, 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Pos(x, 0, z) * (hole + Pos(0, BASE_T - h, 0) * cone)


def v_hole(d, y, z_top, depth):
    """Vertical (in use) teardrop hole from z_top downward."""
    return Pos(WIDTH / 2, y, z_top - depth) * extrude(Plane.XY * tear(d / 2), depth + 1)


def bed_chamfer(part):
    for c in (CHAMFER, 0.3, 0.2):
        try:
            return chamfer(part.faces().sort_by(Axis.X)[0].edges(), c)
        except ValueError:
            pass
    return part


def slab(prof):
    return extrude(Plane.YZ * prof, WIDTH)


def hook() -> Part:
    prof = rect(0, BASE_T, 0, Z_WALL)
    prof += rect(0, D - R_IN, ZC - R_OUT, Z_WALL)
    prof += Pos(D, ZC) * Circle(R_OUT)
    prof += rect(D + R_IN, Y_FO, ZC - 2, Z_WALL)
    prof += rect(Y_FO - 0.01, Y_FO + LEDGE, Z_WALL - LEDGE_T, Z_WALL)
    prof -= Pos(D, ZC) * Circle(R_IN)
    prof -= rect(D - R_IN, D + R_IN, ZC, Z_WALL + 1)
    prof -= rect(-1, Y_FO + LEDGE + 1, Z_WALL, Z_WALL + R_OUT)
    part = bed_chamfer(slab(prof))
    part -= v_hole(INSERT_D, Y_S, Z_WALL, INSERT_DEPTH)
    for z in Z_SCREWS:
        part -= csk_hole(WIDTH / 2, z)
    return part


def cap() -> Part:
    """Cap in its installed position."""
    y_leg = Y_FO + LEDGE + CLR
    z_lip = Z_WALL - LEDGE_T - CLR
    prof = rect(0, y_leg + HOOK_T, Z_WALL, Z_WALL + CAP_T)
    prof += rect(y_leg, y_leg + HOOK_T, z_lip - HOOK_T, Z_WALL + 0.01)
    prof += rect(Y_FO + CLR, y_leg + 0.01, z_lip - HOOK_T, z_lip)
    if CLAMP_PAD > 0:
        prof += rect(D - 3, D + 3, Z_WALL - CLAMP_PAD, Z_WALL + 0.01)
    part = bed_chamfer(slab(prof))
    part -= v_hole(M3_CLEAR, Y_S, Z_WALL + CAP_T + 1, CAP_T + 2)
    return part


def build():
    return [hook(), Pos(0, 32, 0) * cap()]
