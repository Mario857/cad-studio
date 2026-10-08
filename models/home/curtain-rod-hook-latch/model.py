"""curtain-rod-hook-latch: screw-mounted J-hook with a hinged gate that clicks shut over the rod.

Spec: version 2 of 5 window curtain-rod hooks (print 2 sets: left + right are identical).
- Same mount as the other screw versions: 2 countersunk 3.5 x 16 mm self-tapping screws, 4 mm base.
- Open-top cup (bore = rod + 1.5 mm): the rod just drops in, no force on the frame.
- Retention: a gate pivots on a pin at the back of the mouth (pin = 14 mm piece of 1.75 mm
  filament, press-fit in the hook, free in the gate; or an M2 x 14 screw). Swing it down: its
  leg slides over a ridge on the cup front and the barb clicks under it (0.6 mm overlap,
  ~1.7 % strain in the 9 mm leg). Lifting the rod pushes the gate up, which drives the barb's
  flat top into the ridge's flat underside: a positive lock, not a friction catch. Open by
  pulling the thumb tab at the bottom of the leg outward.
- Half-width knuckles (hook knuckle x 0..7, gate knuckle x 7..14) so both parts print flat on
  their side with no overhangs; the gate is laid out mirrored next to the hook for printing.
Print: on its side, no supports.
Assumptions: rod 10 mm, rod axis 15 mm from the frame face (min ~14 mm for this gate layout).
Two bodies per set (hook + gate) are intended.
OpenSCAD twin: curtain-rod-hook-latch.scad (same parameters; MOUNT = "screw" | "vhb").
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
ROD_OFFSET = 15.0    # rod axis -> frame face
WIDTH = 14.0
BASE_T = 4.0
WALL = 2.4
FRONT_DROP = 4.5     # flat front face extends this far below the rod axis
GATE_T = 2.4         # gate arm thickness
GATE_GAP = 0.3       # arm above the cup wall top
KNUCKLE_R = 2.6
PIN_HOOK = 1.8       # 1.75 filament press fit
PIN_GATE = 2.05      # free pivot
CLR = 0.4            # moving clearance
LEG_T = 1.6
LEG_GAP = 0.2
RIDGE = 0.65         # ridge height on the cup front (barb overlap = RIDGE - 0.05)
RIDGE_Z = -3.0       # ridge underside relative to rod axis
TAB = 2.5            # thumb tab length
SCREW_HOLE = 3.9
CSK_D = 7.2
SCREW_EDGE = 6.0
ACCESS = 4.5
CHAMFER = 0.4

R_IN = (ROD_D + ROD_CLEAR) / 2
R_OUT = R_IN + WALL
D = ROD_OFFSET
ZC = SCREW_EDGE + ACCESS + R_OUT
Z_WALL = ZC + R_IN                          # cup wall top
PY = BASE_T + CLR + KNUCKLE_R               # pivot
PZ = Z_WALL + GATE_GAP + GATE_T / 2
Z_BACK = PZ - KNUCKLE_R - CLR               # full-width back block top
Z_SCREWS = (SCREW_EDGE, PZ + KNUCKLE_R + ACCESS)
HEIGHT = Z_SCREWS[1] + SCREW_EDGE
Y_FO = D + R_OUT + 0.4                      # cup front face (proud of the ring: no tangent edge)
Y_LI = Y_FO + RIDGE + LEG_GAP               # leg inner face
ZR = ZC + RIDGE_Z
BARB = Y_LI - (Y_FO + 0.05)
Z_LEG = ZR - 0.5 - BARB * 1.4 - 1.0         # leg bottom


def rect(y0, y1, z0, z1):
    return Pos((y0 + y1) / 2, (z0 + z1) / 2) * Rectangle(y1 - y0, z1 - z0)


def poly(*pts):
    return Polygon(*pts, align=None)


def csk_hole(x, z):
    r = SCREW_HOLE / 2
    tear = Circle(r) + Polygon((0, r * 0.7071), (r * 1.4142, 0), (0, -r * 0.7071), align=None)
    hole = extrude(Plane.XZ * tear, 40, both=True)
    h = (CSK_D - SCREW_HOLE) / 2
    cone = Rot(-90, 0, 0) * Cone(r, CSK_D / 2, h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cone += Pos(0, h, 0) * Rot(-90, 0, 0) * Cylinder(CSK_D / 2, 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Pos(x, 0, z) * (hole + Pos(0, BASE_T - h, 0) * cone)


def bed_chamfer(part):
    """0.4 mm elephant-foot chamfer on the x=0 (bed) face; smaller where tiny features refuse it."""
    for c in (CHAMFER, 0.3, 0.2):
        try:
            return chamfer(part.faces().sort_by(Axis.X)[0].edges(), c)
        except ValueError:
            pass
    return part


def slab(prof, x0, x1):
    return Pos(x0, 0, 0) * extrude(Plane.YZ * prof, x1 - x0)


def pin(d):
    return Pos(0, PY, PZ) * Rot(0, 90, 0) * Cylinder(d / 2, 60)


def hook() -> Part:
    prof = rect(0, BASE_T, 0, HEIGHT)
    prof += rect(0, D - R_IN, ZC - R_OUT, Z_BACK)
    prof += Pos(D, ZC) * Circle(R_OUT)
    prof += rect(D + R_IN, Y_FO, ZC - FRONT_DROP, Z_WALL)
    prof += poly((Y_FO - 0.01, ZR), (Y_FO + RIDGE, ZR), (Y_FO + RIDGE, ZR + 0.6),
                 (Y_FO - 0.01, ZR + 0.6 + RIDGE * 1.5))
    prof -= Pos(D, ZC) * Circle(R_IN)
    prof -= rect(D - R_IN, D + R_IN, ZC, Z_WALL + 10)
    prof -= rect(BASE_T, Y_FO + 2, Z_WALL, Z_WALL + 10)
    prof -= rect(BASE_T, D - R_IN, Z_BACK, Z_WALL + 10)
    knuckle = Pos(PY, PZ) * Circle(KNUCKLE_R) + rect(BASE_T - 0.01, PY + KNUCKLE_R * 0.6, Z_BACK - 1, PZ + KNUCKLE_R)
    part = slab(prof, 0, WIDTH) + slab(knuckle, 0, WIDTH / 2)
    part = bed_chamfer(part)
    part -= pin(PIN_HOOK)
    for z in Z_SCREWS:
        part -= csk_hole(WIDTH / 2, z)
    return part


def gate() -> Part:
    """Gate in its closed position (in-use coordinates)."""
    top = Z_WALL + GATE_GAP + GATE_T
    prof = rect(PY + KNUCKLE_R + CLR, Y_LI + LEG_T, Z_WALL + GATE_GAP, top)
    prof += rect(Y_LI, Y_LI + LEG_T, Z_LEG, top)
    prof += poly((Y_LI + 0.01, ZR - 0.2), (Y_LI - BARB, ZR - 0.2), (Y_LI - BARB, ZR - 0.5),
                 (Y_LI + 0.01, ZR - 0.5 - BARB * 1.4))
    prof += rect(Y_LI + LEG_T - 0.01, Y_LI + LEG_T + TAB, Z_LEG, Z_LEG + 1.6)
    knuckle = Pos(PY, PZ) * Circle(KNUCKLE_R) + rect(PY, PY + KNUCKLE_R + CLR + 1, PZ - GATE_T / 2, PZ + GATE_T / 2)
    part = slab(prof, 0, WIDTH) + slab(knuckle, WIDTH / 2, WIDTH)
    part -= pin(PIN_GATE)
    return part


def build():
    g = Pos(WIDTH, 0, 0) * mirror(gate(), about=Plane.YZ)       # knuckle side down for printing
    g = bed_chamfer(g)
    return [hook(), Pos(0, 25, 0) * g]
