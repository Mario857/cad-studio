"""hat-rack: wall rack for 3 baseball caps on curved, upturned hooks.

Spec: a vertical wall strip with three hooks, one above the other. Each hook is a
50 mm wide blade that leaves the wall horizontally and curves gently upward
(~50 mm deep from the wall), so a cap sits over it like on a head: the blade
supports the back of the crown from inside and the upturned tip keeps the cap
from sliding off, without creasing the crown.
Mounting: 3x countersunk wood screws (default 4 mm, e.g. 4x30 + wall plugs),
or 3 adhesive pads on the flat back (e.g. Command large strips, ~20x70 mm or 3M VHB 19x50 mm).

Whole part is one extruded side profile (YZ) -> printed lying on its side
(print_orientation rotates X to Z): layers run along the hooks (strong in bending),
no overhangs, no supports. Screw holes are horizontal in print; the 4.5 mm shaft
bridge is tiny and the 90 deg countersink cone is self-supporting.

Assumptions:
- Caps hang stacked vertically at HOOK_PITCH 100 mm; crowns nest/overlap slightly, as on
  commercial vertical cap racks. Rack fits the bed (280 mm long when printed on its side).
- Cap weight ~120 g each; ABS PLUS is ample for that.
- Wall face is y=0, hooks project toward +Y; bottom of the strip at z=0.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,            # wall-mounted
    loads=[],
    print_orientation=(0, 90, 0),  # lie on its side: hook profile flat on bed, layers along hooks
    supports="off",
    brim="auto",
)

# Parameters
N_HOOKS = 3
HOOK_PITCH = 100.0         # vertical spacing between hooks
WIDTH = 50.0               # strip & hook blade width (X)
PLATE_T = 6.0              # back plate thickness (Y)
PLATE_H = 280.0            # back plate height (Z)
FIRST_HOOK_Z = 45.0        # centerline height of lowest hook root
HOOK_DEPTH = 50.0          # total depth from wall to hook tip
HOOK_SWEEP = 35.0          # deg the blade curves upward over its length
HOOK_T_ROOT = 10.0         # blade thickness at root
HOOK_T_TIP = 6.0           # blade thickness at tip
GUSSET = 12.0              # 45 deg gusset under each hook root
EDGE_CHAMFER = 0.6         # side edges (bed side gets elephant-foot chamfer)
SCREW = "M4"               # ~4 mm wood screw, countersunk 90 deg
SCREW_Z = (95.0, 195.0, 265.0)  # between hooks + above top hook (takes most moment)


def hook_profile(zc: float) -> Face:
    """Side profile (YZ) of one hook, root centerline at height zc."""
    tip_r = HOOK_T_TIP / 2
    ys = PLATE_T - 1.0                       # overlap into plate
    reach = HOOK_DEPTH - tip_r - ys
    th = math.radians(HOOK_SWEEP)
    r = reach / math.sin(th)
    n = 24
    upper, lower = [], []
    for i in range(n + 1):
        a = th * i / n
        cy, cz = ys + r * math.sin(a), zc + r * (1 - math.cos(a))
        ny, nz = -math.sin(a), math.cos(a)   # normal toward arc center (upward side)
        t = HOOK_T_ROOT + (HOOK_T_TIP - HOOK_T_ROOT) * i / n
        upper.append((cy + ny * t / 2, cz + nz * t / 2))
        lower.append((cy - ny * t / 2, cz - nz * t / 2))
    pts = upper + lower[::-1]
    blade = Polygon(*pts, align=None)
    ey, ez = ys + r * math.sin(th), zc + r * (1 - math.cos(th))
    tip = Pos(ey, ez) * Circle(tip_r)
    zb = zc - HOOK_T_ROOT / 2
    gusset = Polygon((ys, zb + 1), (ys, zb - GUSSET), (ys + GUSSET + 1, zb + 1), align=None)
    return blade + tip + gusset


def build() -> Part:
    # Profile in local (u=Y, v=Z) on Plane.YZ, extruded along X.
    prof = Pos(PLATE_T / 2, PLATE_H / 2) * Rectangle(PLATE_T, PLATE_H)
    for i in range(N_HOOKS):
        prof += hook_profile(FIRST_HOOK_Z + i * HOOK_PITCH)
    part = extrude(Plane.YZ * prof, WIDTH / 2, both=True)

    # Chamfer the outline edges on both side faces (one of them is on the bed).
    side_edges = part.faces().sort_by(Axis.X)[0].edges() + part.faces().sort_by(Axis.X)[-1].edges()
    part = chamfer(side_edges, EDGE_CHAMFER)

    # Countersunk screw holes, head on the front face (y=PLATE_T), drilled toward the wall.
    for z in SCREW_Z:
        part -= Pos(0, PLATE_T, z) * Rot(-90, 0, 0) * bolt_hole(SCREW, PLATE_T + 2, head="csk")
    return part
