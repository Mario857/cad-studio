"""curtain-hook-peg: tool-free clothes-peg style clip with a J-hook for a light curtain rod.

HOW IT WORKS
  A one-piece printed spring clip straddles the top edge of a uPVC window-frame ledge
  (thickness FRAME_T). Two parallel jaws (20 mm deep, 20 mm wide) are joined at the back by a
  U-loop (binder-clip style flexure). The rest gap between the jaw faces is FRAME_T - 1 mm, so
  the jaws pre-load the ledge; 0.6 mm 45-degree teeth on both inner faces bite into the frame,
  and 45-degree lead-ins on the jaw tips let it push on by hand. The back of the loop sits on
  top of the ledge, so rod weight is carried by the ledge edge, not only by friction.
  On the room-side jaw a 45-degree gusseted arm carries a J-cradle: bore 10.5 mm for a 9 mm rod,
  axis ROD_OUT (25 mm) out from the frame face. The right side of the ring is a slender snap
  finger (1.6 mm, free-standing) so the mouth (8.2 mm) opens ~0.8 mm to take the rod, then
  retains it with its shoulder so it cannot fall out when the window moves.
  Profile lies in the XZ plane and is extruded along Y (width), so printed on its side every
  layer is the full profile: zero supports, layers follow the spring curve.

NUMBERS (ABS+, E ~ 2000 MPa)
  Spring arms/loop 2.6 mm thick. Tip deflection to open from gap to FRAME_T plus teeth is
  ~1.1 mm per jaw: arm-cantilever strain 3*t*d/(2*L^2) = ~1.1 %; loop adds <1 %. Total <= ~1.8 %
  worst case (limit 2 %). Snap finger: t 1.6, free arc ~12 mm, d 0.8 mm -> ~1.3 %.
  Grip force ~ 20 N per jaw before friction; hold-down by gravity on the ledge edge.

PROS / CONS vs SCREWS
  + no tools, no holes in the frame, removable, no damage. 
  - Holding force is limited: it relies on spring grip plus the ledge edge. Suits only a LIGHT
    rod and light curtain (about 0.5 kg total across 2-3 clips); a pull-off/upward force, a
    heavy net or a knock will dislodge it. Use screws for anything heavy.
  - ABS creeps slowly under permanent spring preload; the clip may lose some grip over months.

ASSUMPTIONS
  FRAME_T = 10 mm ledge thickness (measure yours and edit FRAME_T; the rest gap, teeth, loop and
  hook position follow). Works for ledges roughly FRAME_T +/- 1.5 mm. Ledge is >= 20 mm deep and
  flat-topped. Rod axis is measured from the frame face (x = FRAME_T).

SLICER SETTINGS (Bambu Studio, ABS+ 0.4 mm)
  Orientation: as supplied (profile flat on the bed, 20 mm tall). Layer 0.20 mm, walls 4,
  top/bottom 4, infill 40-100 % gyroid (tiny part: use 100 % for the spring). No supports,
  brim optional. Keep enclosed chamber / draft shield on to avoid ABS warping.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(90, 0, 0),  # profile (XZ) lies flat in XY; layers follow the spring curve
    supports="off",
    brim="auto",
    copies=2,
)

# Parameters (mm)
FRAME_T = 10.0       # frame ledge thickness to clamp (measure!)
PRELOAD = 1.0        # rest gap = FRAME_T - PRELOAD
JAW_D = 20.0         # jaw depth
WIDTH = 20.0         # clip width (along Y)
ARM_T = 2.6          # spring arm / loop thickness
LEAD = 1.2           # 45 deg lead-in at jaw tips
TOOTH_H = 0.6
TOOTH_P = 2.0
N_TEETH = 6
TOOTH_Z0 = -3.0      # first tooth z (below the loop)
ROD_D = 9.0
BORE_D = 10.5
MOUTH = 8.2
ROD_OUT = 25.0       # rod axis out from the frame face
RING_WALL = 1.8      # rigid ring wall
FINGER_T = 1.6       # snap finger thickness
ARM_Z = -16.0        # rod axis height (z)
HOOK_ARM_T = 3.0
GUSSET = 9.0

GAP = FRAME_T - PRELOAD
XB = GAP + ARM_T          # outer face of room-side jaw
XR = FRAME_T + ROD_OUT    # rod axis x
RB = BORE_D / 2


def prof(pts):
    return extrude(Plane.XZ * Polygon(*pts, align=None), amount=WIDTH / 2, both=True)


def sector(ri, ro, a0, a1, n=24):
    """annular sector in XZ, angles in deg (CCW from +X), centered at 0,0 -> polygon points."""
    import math
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((ro * math.cos(a), ro * math.sin(a)))
    for i in range(n + 1):
        a = math.radians(a1 + (a0 - a1) * i / n)
        pts.append((ri * math.cos(a), ri * math.sin(a)))
    return pts


def build() -> Part:
    import math
    # --- jaws (inner faces at x=0 and x=GAP), lead-in cut on inner tip corners
    jaw_a = prof([(-ARM_T, 0), (0, 0), (0, -JAW_D + LEAD), (-LEAD, -JAW_D), (-ARM_T, -JAW_D)])
    jaw_b = prof([(GAP, 0), (XB, 0), (XB, -JAW_D), (GAP + LEAD, -JAW_D), (GAP, -JAW_D + LEAD)])
    # --- U-loop (upper half annulus)
    cx = GAP / 2
    ri, ro = GAP / 2, GAP / 2 + ARM_T
    loop = prof([(cx + x, z) for x, z in sector(ri, ro, 0, 180, 36)])
    part = jaw_a + jaw_b + loop
    # --- teeth: 45 deg triangles
    for i in range(N_TEETH):
        z = TOOTH_Z0 - i * TOOTH_P
        part += prof([(0, z + TOOTH_H), (TOOTH_H, z), (0, z - TOOTH_H)])
        part += prof([(GAP, z + TOOTH_H), (GAP - TOOTH_H, z), (GAP, z - TOOTH_H)])
    # --- hook arm + 45 deg gusset
    ring_l = XR - (RB + RING_WALL)
    part += prof([(XB - 0.5, ARM_Z - HOOK_ARM_T / 2), (ring_l + 1, ARM_Z - HOOK_ARM_T / 2),
                  (ring_l + 1, ARM_Z + HOOK_ARM_T / 2), (XB - 0.5, ARM_Z + HOOK_ARM_T / 2)])
    part += prof([(XB - 0.5, ARM_Z + HOOK_ARM_T / 2), (XB + GUSSET, ARM_Z + HOOK_ARM_T / 2),
                  (XB - 0.5, ARM_Z + HOOK_ARM_T / 2 + GUSSET + 0.5)])
    # --- cradle: rigid left/bottom body + free-standing snap finger on the outboard side
    ang = math.degrees(math.acos((MOUTH / 2) / RB))      # angle of mouth corner on bore circle
    zc_corner = math.sqrt(RB**2 - (MOUTH / 2) ** 2)
    ang_top = math.degrees(math.atan2(zc_corner, MOUTH / 2))   # ~39 deg
    body = [(XR + x, ARM_Z + z) for x, z in sector(RB, RB + RING_WALL, 180 - ang_top, 310 + 0, 40)]
    part += prof(body)
    finger = [(XR + x, ARM_Z + z) for x, z in sector(RB, RB + FINGER_T, -50, ang_top, 24)]
    part += prof(finger)
    # shoulder blend on finger root: small block joining finger to body bottom
    # (the sectors overlap at -50 deg, so they are fused already)
    return part
