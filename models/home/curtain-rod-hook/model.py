"""curtain-rod-hook: screw-on J hook with a snap clip that locks a curtain rod in place.

Spec: a back plate screws flat onto the window frame/sash with 2 countersunk wood screws
(one above the other). At the bottom a J cradle wraps ~250° around the rod; its mouth is
narrower than the rod (ROD_D * SNAP), so the rod snaps in with a push from the
front/top and cannot jump out when the window is swung open. The mouth faces up and
forward with chamfered lead-ins; pull the rod forward/up firmly to unclip it.
Printed lying on its side, so the layers follow the J profile (hook and clip flex along
the layers, not across them). Print 2 copies (META copies=2).

Assumptions: rod diameter 12 mm (change ROD_D; fits 10-16 mm rods by editing one line),
screws ~3.5-4 mm countersunk wood screws (M4 clearance hole, 90° countersink),
rod + curtain load ≤ 0.5 kg per hook, PETG for toughness/heat near a sunny window.
The clip-mouth edges on the side faces are left sharp (OCC chamfer limitation).
"""

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm. X = away from the window frame (plate back at x=0).
META = dict(
    material="PETG",
    quality="strong",
    standing=False,
    loads=[],                       # set below once geometry is known
    print_orientation=(90, 0, 0),   # lie on its side: layers follow the J profile
    supports="off",
    brim="auto",
    copies=2,
)

# Parameters
ROD_D = 12.0          # curtain rod diameter
ROD_CLEAR = 0.3       # radial clearance around the rod
WALL = 3.0            # cradle wall thickness
SNAP = 0.80           # mouth width as a fraction of ROD_D (smaller = firmer clip)
MOUTH_ANGLE = 40.0    # mouth tilt from vertical toward the front (deg)
LEAD_IN = 1.5         # extra mouth width at the outside (lead-in chamfer)
WIDTH = 15.0          # hook width (along the rod)
PLATE_T = 5.0         # back plate thickness
PLATE_H = 62.0        # overall height
SHAFT_D = 4.4         # screw clearance (3.5-4 mm wood screws)
HEAD_D = 8.4          # countersink diameter at the front face
SCREW_Z = (30.0, 52.0)  # screw centres above the bottom
TOP_R = 2.0           # top corner rounding of the plate
EDGE_CHAMFER = 0.4    # chamfer on the side-face edges (elephant foot) (side face is on the bed)
LOAD_G = 500          # rod + curtain share per hook

R_IN = ROD_D / 2 + ROD_CLEAR
R_OUT = R_IN + WALL
CX = PLATE_T + R_IN   # rod centre: inner surface touches the plate front face
CZ = R_OUT            # cradle rests on z=0
GAP = ROD_D * SNAP
ALIGN_CSK = (Align.CENTER, Align.CENTER, Align.MIN)

META["loads"] = [dict(at=(CX, 0, CZ), grams=LOAD_G)]


def profile(with_mouth: bool = True) -> Sketch:
    plate = Pos(PLATE_T / 2, CZ + (PLATE_H - CZ) / 2) * Rectangle(PLATE_T, PLATE_H - CZ)
    plate = fillet(plate.vertices().group_by(Axis.Y)[-1], TOP_R)
    ring = Pos(CX, CZ) * Circle(R_OUT)
    base = Pos(CX / 2, CZ / 2) * Rectangle(CX, CZ)
    shoulder_h = CZ + R_OUT - 1.5
    shoulder = Pos((CX - 1) / 2, shoulder_h / 2) * Rectangle(CX - 1, shoulder_h)
    s = plate + ring + base + shoulder
    s -= Pos(CX, CZ) * Circle(R_IN)
    return s - mouth() if with_mouth else s


def mouth() -> Sketch:
    g = GAP / 2
    m = Polygon(
        (-g, 0), (g, 0), (g, R_IN + 0.8), (g + LEAD_IN, R_OUT + 0.5),
        (-g - LEAD_IN, R_OUT + 0.5), (-g, R_IN + 0.8), align=None,
    )
    return Pos(CX, CZ) * Rot(0, 0, -MOUTH_ANGLE) * m


def build() -> Part:
    # chamfer the side-face edges (one side is on the bed when printed) before cutting
    # the clip mouth; OCC cannot chamfer the mouth corners together with the rest
    part = extrude(Plane.XZ * profile(with_mouth=False), WIDTH / 2, both=True)
    part = chamfer(part.edges().group_by(Axis.Y)[0] + part.edges().group_by(Axis.Y)[-1],
                   EDGE_CHAMFER)
    part -= extrude(Plane.XZ * mouth(), WIDTH, both=True)
    for z in SCREW_Z:
        # teardrop shaft (tip toward +Y = up when printed) + 90° countersink on the front
        part -= Pos(PLATE_T / 2, 0, z) * Rot(-90, 0, 0) * teardrop_hole(SHAFT_D, PLATE_T + 2, along="X")
        part -= Pos(PLATE_T + 0.01, 0, z) * Rot(0, -90, 0) * Cone(HEAD_D / 2, 0, HEAD_D / 2, align=ALIGN_CSK)
    return part
