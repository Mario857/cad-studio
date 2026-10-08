"""curtain-hook-snap: screw-mounted J-hook for a Ø9 mm curtain rod with a snap-fit retention lip.

HOW IT WORKS
  Base plate (20 x 38 x 4) screws to the uPVC frame face (x=0 plane) with 2 csk screws.
  A 12 mm wide arm projects 25 mm; its end is a U-cup (bore Ø10.5, rod axis 25 mm from the frame
  face). The outer wall of the cup continues upward as a flexible cantilever finger (2 mm thick,
  ~11.8 mm free length) ending in an inward lip: 45 deg lead-in on top, small shoulder below.
  Push the rod down into the mouth: the finger flexes 0.8 mm (mouth rest 8.2 mm vs rod 9 mm),
  clicks past the lip and the rod drops into the cup. Rod axis in use is along Y.

NUMBERS
  Finger strain (cantilever eps = 3*t*d / (2*L^2)) = 3*2*0.8/(2*11.8^2) = ~1.7 % (< 2 % ABS limit).
  Lip engagement 2.3 mm, shoulder face ~21 deg from horizontal (retains, but a deliberate lift
  of ~2-3 N with a slight sideways push on the finger frees it). Rod-to-lip gap in the cup 0.3 mm.
  Hold strength: against vertical jerk the rod must flex the finger; typical snap-out force
  roughly 5-10 N, far above a ~0.1 kg curtain-rod inertial load during window slamming.
  Downward load is carried by the stiff cup (2.5 mm bottom wall), not the lip.
  Screws: base 4 mm, csk 2 mm deep, so a 12 mm screw enters the frame max 12-4 = 8 mm (head flush
  to the csk). uPVC outer wall + chamber is normally >8 mm before the steel reinforcement,
  but a shorter 10 mm screw is safer if the profile is shallow (ASSUMPTION; check frame).

PROS: tool-free rod insertion, no extra parts, quiet, prints with zero supports.
CONS: lip can fatigue/creep after many cycles; fixed-size rod; ABS shrink may change the
  gap by ~0.1 mm (tune LIP_PROTRUSION).

PRINTING: 2 hooks per print (META copies=2: identical copies arranged by the studio).
  The 12 mm hook is flush with one long edge of the 20 mm base (offset 4 mm) so the whole
  part lies flat on that face with no overhang.
  Orientation: rotated 90 deg about X so the hook profile (J-curve and finger) lies in the XY
  plane; layer lines run across the 12 mm width and do NOT cross the load path or the finger
  bending plane. Zero supports. Slicer: ABS+ 0.20 mm layers (standard), 4 walls, 40 % gyroid
  (grid also fine) infill, 5 top/bottom layers, no supports, brim only if the base warps
  (ABS: enclosed chamber, 100 C bed, close the H2C door).
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(90, 0, 0),
    supports="off",
    brim="auto",
    copies=2,
)

# Parameters
ROD_D = 9.0
BORE_D = 10.5
BASE_W = 20.0
BASE_L = 38.0
BASE_T = 4.0
HOOK_W = 12.0
ROD_X = 25.0            # rod axis distance from frame face
ARM_H = 6.0
CUP_R = 7.75            # outer radius of the cup (wall 2.5 around the bore)
FINGER_T = 2.0
FINGER_ROOT = 3.0       # finger free below zc - this
FINGER_TOP = 8.8        # above rod axis
LIP_Z = 4.8             # lip start above rod axis
LIP_TIP = 2.3           # protrusion into bore
SCREW_D = 3.6
CSK_D = 7.8
CSK_DEPTH = 2.0
SCREW_Z = (15.0, 32.0)

ZC = CUP_R
R = BORE_D / 2


def build() -> Part:
    cup = Pos(ROD_X, 0, ZC) * (Rot(90, 0, 0) * Cylinder(CUP_R, HOOK_W))
    arm = Pos(0, -HOOK_W / 2, 0) * Box(ROD_X, HOOK_W, ARM_H, align=(Align.MIN, Align.MIN, Align.MIN))
    base = Pos(0, -BASE_W / 2, 0) * Box(BASE_T, BASE_W, BASE_L, align=(Align.MIN, Align.MIN, Align.MIN))
    gusset = Pos(BASE_T, 0, ARM_H) * rib(12, 12, HOOK_W)
    lwall = Pos(ROD_X - CUP_R, -HOOK_W / 2, ZC) * Box(CUP_R - R, HOOK_W, 4.5, align=(Align.MIN, Align.MIN, Align.MIN))
    fx = ROD_X + R
    finger = Pos(fx, -HOOK_W / 2, ZC - 4.5) * Box(FINGER_T, HOOK_W, FINGER_TOP + 4.5, align=(Align.MIN, Align.MIN, Align.MIN))
    zl = ZC + LIP_Z
    tipx = fx - LIP_TIP
    lip = extrude(Plane.XZ * Polygon((fx + 0.1, zl), (tipx, zl + 0.9), (tipx, zl + 1.6),
                                     (fx + 0.1, zl + 3.9), align=None), amount=HOOK_W / 2, both=True)
    part = arm + gusset + cup + lwall
    # free the finger from the cup above FINGER_ROOT
    part = part - Pos(ROD_X, -HOOK_W, ZC - FINGER_ROOT) * Box(CUP_R + 1, 2 * HOOK_W, 20, align=(Align.MIN, Align.MIN, Align.MIN))
    # bore + open throat above the rod axis (between left wall and finger)
    part = part - Pos(ROD_X, 0, ZC) * (Rot(90, 0, 0) * Cylinder(R, 40))
    part = part - Pos(ROD_X - R, -20, ZC) * Box(2 * R, 40, 30, align=(Align.MIN, Align.MIN, Align.MIN))
    part = part + finger + lip
    # hook is flush with the base side face y=-10 so it prints with zero supports on that face
    part = Pos(0, -(BASE_W - HOOK_W) / 2, 0) * part + base
    # csk screw holes (axis X, head side at x = BASE_T)
    for z in SCREW_Z:
        cutter = Pos(0, 0, -6) * Cylinder(SCREW_D / 2, 8, align=ON_BED) \
            + Pos(0, 0, -CSK_DEPTH) * Cone(SCREW_D / 2, CSK_D / 2, CSK_DEPTH, align=ON_BED) \
            + Pos(0, 0, 0) * Cylinder(CSK_D / 2, 1, align=ON_BED)
        part = part - at(BASE_T, 0, z, 0, 90, 0) * cutter
    return part
