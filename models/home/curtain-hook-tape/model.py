"""curtain-hook-tape: no-drill J-hook with spring-tab retention for a light round curtain rod.

Stuck to a PVC/uPVC window frame with 3M VHB tape (no screws). Print 2 identical hooks per
plate (build() returns two identical parts side by side, META copies=1).

HOW IT WORKS
- Flat pad (21.6 x 39.6 x 3 mm) with a 20 x 38 mm x 0.6 mm tape pocket (0.8 mm raised border)
  on the frame face. Rod axis 25 mm out from the frame face, hole D10.5 for a D9 rod.
- The profile (XZ plane) is extruded 21.6 mm along Y; the part is printed standing on its side
  (print_orientation rx=90) so layers are parallel to the profile and never cross the curved
  hook, the arm or the tab. Zero supports.
- Spring tab: the right side of the ring is a thin curved leaf (1.6 mm, ~12 mm long arc) molded
  into the ring at the bottom and free at the top. Mouth is 8.2 mm (< 9 mm rod): press the rod
  down through the mouth, the tab flexes outward ~0.9 mm and springs back, trapping the rod.
  Lifting the rod out needs a deliberate push, so slamming/opening the window does not eject it.
- Tab strain (cantilever, eps = 3*t*d/(2*L^2)): t=1.6, L~12.1, d~0.9 -> ~1.5 % (ABS yield ~2 %,
  so no snapping and no creep set under occasional use). The load-bearing bottom of the ring is
  rigid 2.4 mm wall; the tab only retains, it does not carry the curtain weight.

PROS: no drilling, removable (heat + floss), one printed piece, no hardware, rod can be snapped
in/out. CONS: tab fatigues after many cycles; only 8.2 mm mouth so rod must be pressed in;
tape holds only if surface prepared; not for heavy/lined curtains.

HOLD STRENGTH (estimate): VHB pad 760 mm2; conservative long-term shear on clean PVC ~0.15-0.2
MPa -> ~110-150 N (11-15 kg) per pad in pure shear; curtain load per hook is ~0.2-0.5 kg.
PEEL WARNING: VHB is weak in peel/cleave (~1/10 of shear). The rod is 25 mm out, so any upward
or outward pull on the rod (tugging curtain, pulling rod out) levers the pad off the frame. Load
should be mostly SHEAR (straight down, pad vertical and flat on the frame). Never pull the
curtain/rod outward or upward; keep the frame face flat (no bead/curved profile under the pad).
To remove: warm with hair dryer, saw with dental floss behind the pad.

SLICER SETTINGS: orientation as modeled (profile flat on bed, Y up, rx=90; pad wall vertical),
supports off, brim off; 0.2 mm layer (standard), 4 walls (>=1.6 mm), 5 top/bottom layers,
infill 40 % gyroid (or 100 % walls only), 250-260 C ABS+, bed 100 C, enclosed/no draft
(ABS warps). Tape pocket face is a vertical wall - print slowly on outer wall for flatness.

TAPE PREP: clean PVC with 70-99 % isopropyl alcohol (no household cleaners or silicone polish),
let it dry; also wipe the printed pad and lightly sand glossy pad face if needed; apply tape
to the hook first, press 20 s with firm pressure, then stick to the frame at 20 C+ (not in
cold), press hard 30 s; wait 24 h before loading to reach ~90 % strength; trim tape 20 x 38.

NOTE: the 0.8 mm walls flagged by the audit are the intentional tape-pocket border.

ASSUMPTIONS: tape thickness ~0.6 mm (VHB 4950 is 1.1 mm and compresses - recess then stands
slightly proud, which is intended); pad is 21.6 x 39.6 to keep 0.8 mm border around a 20 x 38
tape; ABS+ treated as ABS (yield ~40 MPa, E ~2 GPa).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[dict(at=(25, 0, 20), grams=300)],
    print_orientation=(90, 0, 0),  # profile (XZ) flat on bed, Y up
    supports="off",
    brim="auto",
    copies=1,
)

# Parameters
TAPE_W = 20.0
TAPE_L = 38.0
BORDER = 0.8
POCKET_D = 0.6
PAD_T = 3.0
PAD_W = TAPE_W + 2 * BORDER     # along Y
PAD_L = TAPE_L + 2 * BORDER     # along Z
ROD_D = 9.0
HOLE_D = 10.5
ROD_OFFSET = 25.0               # rod axis distance from frame face
WALL = 2.4
TAB_T = 1.6
MOUTH = 8.2
TAB_END_DEG = 180 - 15          # tab root (clockwise from top)
ZC = PAD_L / 2

R_H = HOLE_D / 2
R_O = R_H + WALL


def pol(r, deg):
    a = math.radians(deg)
    return (r * math.sin(a), r * math.cos(a))


def sector(r0, r1, a0, a1, step=3):
    n = max(2, int(abs(a1 - a0) / step) + 1)
    angs = [a0 + (a1 - a0) * i / (n - 1) for i in range(n)]
    pts = [pol(r1, a) for a in angs] + [pol(r0, a) for a in reversed(angs)]
    return Polygon(*reversed(pts), align=None)


def wedge(a0, a1, r=40):
    pts = [(0, 0)] + [pol(r, a0 + (a1 - a0) * i / 10) for i in range(11)]
    return Polygon(*pts, align=None)


def build() -> Part:
    # mouth half-angle at hole radius
    half = math.degrees(math.asin(MOUTH / 2 / R_H))
    tip = half + 1.0
    plate = Pos(PAD_T / 2, ZC) * Rectangle(PAD_T, PAD_L)
    ox = ROD_OFFSET
    arm = Pos(ox, ZC) * Polygon(
        (-ox, -17), (0, -R_O), (0, 0), (-ox, 9), align=None)
    ring = Pos(ox, ZC) * (Circle(R_O)
                          - wedge(tip, TAB_END_DEG)     # free space on tab side
                          - wedge(-half, tip))
    ring = ring + Pos(ox, ZC) * sector(R_H - 0.01, R_H + TAB_T, tip + 2, TAB_END_DEG + 1)
    profile = plate + arm + ring
    profile = profile - Pos(ox, ZC) * Circle(R_H)
    profile = profile - Pos(ox, ZC) * wedge(-half, tip - 0.0)
    # extrude along Y (Plane.XZ normal = -Y), then centre on Y
    body = extrude(Plane.XZ * profile, PAD_W)
    body = Pos(0, PAD_W / 2, 0) * body
    pocket = Pos(0, 0, ZC) * Box(2 * POCKET_D, TAPE_W, TAPE_L)
    one = body - pocket
    return [one, Pos(0, 0, PAD_L + 4) * one]   # 2 identical hooks, side by side on the bed

L_TAB = math.radians(TAB_END_DEG - (math.degrees(math.asin(MOUTH / 2 / R_H)) + 3)) * (R_H + TAB_T / 2)
print(f"tab L={L_TAB:.1f} mm, strain(d=0.9)={3*TAB_T*0.9/(2*L_TAB**2)*100:.2f} %")
