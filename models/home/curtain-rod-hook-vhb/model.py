"""curtain-rod-hook-vhb: no-drill tape-mounted hook with a gravity-lock (labyrinth) seat.

Spec: version 5 of 5 window curtain-rod hooks (print 2 per window: left + right are identical).
- Mount: 20 x 50 mm flat back for one strip of 19 mm 3M VHB (e.g. 5952/4910) - no screws, no
  holes in the frame. Clean the PVC with isopropyl alcohol, press hard for 30 s, wait 24 h
  before hanging the rod. Hook sits low on the plate so the long plate above resists peel.
- Retention: no moving parts and no snap force, so inserting/removing the rod never pulls on
  the tape. The rod drops down the front channel, then rolls back under a roof into a pocket
  that is 4.6 mm deeper than the channel floor. To get out it must lift 4.6 mm AND move 7 mm
  forward AND then go up - a slam or quick swing of the window cannot do that; the pocket wall
  at the sill is ~78 deg steep, so a sideways jolt needs > 4 g to climb it.
Print: on its side (hook flush with the bed side of the plate), no supports.
Assumptions: rod 10 mm, rod axis 15 mm from the frame face, frame face >= 20 mm wide.
OpenSCAD twin: curtain-rod-hook-vhb.scad (same parameters; MOUNT = "screw" | "vhb").
"""

from build123d import *

from cadlib import *

META = dict(
    material="ASA",
    quality="standard",
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
PLATE_W = 20.0       # tape plate width (matches 19 mm VHB)
PLATE_H = 50.0
PLATE_T = 3.0
HOOK_W = 12.0        # hook width along the rod
HOOK_LIFT = 4.0      # hook bottom above plate bottom
WALL = 2.4
SILL = 0.8           # pocket depth below the channel floor, as a fraction of the bore radius
ROOF_TIP = 1.0       # roof reaches this far past the rod axis
HEAD_CLR = 0.5       # rod clearance under the roof when it rolls from channel to pocket
CHAMFER = 0.4

R_IN = (ROD_D + ROD_CLEAR) / 2
R_OUT = R_IN + WALL
D = ROD_OFFSET
ZC = HOOK_LIFT + R_OUT
Z_FLOOR = ZC - R_IN + SILL * R_IN           # channel floor
Z_ROOF = Z_FLOOR + ROD_D + HEAD_CLR         # roof underside
Y_RT = D + ROOF_TIP                         # roof tip = channel back
Y_CF = Y_RT + ROD_D + ROD_CLEAR             # channel front


def rect(y0, y1, z0, z1):
    return Pos((y0 + y1) / 2, (z0 + z1) / 2) * Rectangle(y1 - y0, z1 - z0)


def bed_chamfer(part):
    for c in (CHAMFER, 0.3, 0.2):
        try:
            return chamfer(part.faces().sort_by(Axis.X)[0].edges(), c)
        except ValueError:
            pass
    return part


def build() -> Part:
    top = Z_ROOF + WALL
    prof = rect(0, Y_CF + WALL, ZC - R_OUT + 2, top)
    prof += rect(0, Y_CF + WALL, ZC - R_OUT, ZC)
    prof += Pos(D, ZC) * Circle(R_OUT)
    prof -= Pos(D, ZC) * Circle(R_IN)
    prof -= rect(D - R_IN, Y_CF, ZC, Z_ROOF)
    prof -= rect(D, Y_CF, Z_FLOOR, ZC + 0.01)
    prof -= rect(Y_RT, Y_CF, Z_ROOF - 0.01, top + 1)
    y1, z0 = Y_CF + WALL, ZC - R_OUT
    prof -= Polygon((y1 - 6, z0 - 0.01), (y1 + 0.01, z0 - 0.01), (y1 + 0.01, z0 + 6), align=None)
    hook = extrude(Plane.YZ * prof, HOOK_W)
    plate = Pos(PLATE_W / 2, PLATE_T / 2, PLATE_H / 2) * Box(PLATE_W, PLATE_T, PLATE_H)
    return bed_chamfer(hook + plate)
