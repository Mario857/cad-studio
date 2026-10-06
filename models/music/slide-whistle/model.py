"""slide-whistle: fipple slide whistle, 20 mm bore, O-ring piston, ~1.5 octaves G4..D6.

Spec
- One-piece body (fipple head + 20 mm bore tube), printed vertically mouthpiece-up: the
  windway (1.2 x 14 mm, 30 mm long) is a vertical slot, the bore is smooth and vertical, the
  bore ceiling under the block is a 45 deg ramp - no supports anywhere inside.
- Mouth 14 x 5 mm, labium edge 0.6 mm, outer bevel 18 deg; the bore is flattened (14 mm wide
  flat) under the window so the labium edge is straight.
- Piston (closed end of the pipe) with an O-ring groove, glued onto a flat 8 x 6 mm rod that
  ends in a flat finger ring; rod is guided by a push-on bottom cap with a slot.
- All 4 parts on one plate: body standing, piston and cap standing, rod+ring lying flat
  (rod bends within its layers).

Physics (c = 343 m/s, 20 C). Stopped pipe excited through a mouth of area S_m in a bore of
area S_p; the mouth is an acoustic mass L_m = t_m + 1.6 r_m (r_m = sqrt(S_m/pi)):
    cot(k L) = k L_m S_p / S_m ,  k = 2 pi f / c   ->  L(f) = arccot(k L_m S_p/S_m) / k
L = mouth centre to piston face. Range: F_LOW .. F_LOW * 2^RANGE_OCT.
Body length follows from L(F_LOW); stroke = L(F_LOW) - L(F_HIGH); rod length from stroke.

TUNING (S_p = 314 mm2, S_m = 70 mm2, L_m ~ 9.0 mm)
  note | target Hz | piston face below mouth centre L (mm)
  G4   | 392.00    | 179.6  (lowest, piston at bottom stop)
  C5   | 523.25    | 125.5
  G5   | 783.99    |  72.9
  C6   | 1046.50   |  47.7
  D6   | 1174.66   |  39.9  (highest, piston near the top)
  stroke ~ 140 mm (exact values: `python model.py`, recomputed from params on every build)

Fine-tuning after printing
- A slide whistle is pitched by ear; the piston position IS the tuning. Check the end
  points with a tuner: lowest note with the piston at the bottom stop (G4 if leak-free), the
  top note with the piston ~40 mm below the mouth centre.
- Lowest note too sharp/weak -> leak: reseat the O-ring, grease it, seal the head with no cracks.
  Lowest note too flat -> trim the rod ring-side stop: glue a spacer in the cap (raises the stop).
- Tone/airy: filing the labium to lengthen the window flattens slightly and softens the tone;
  keep the edge >= 0.4 mm and straight. Clear the windway with a 1 mm card.
- Optional: mark note positions on the rod with a fine marker using a tuner (table above
  gives the starting points: distance from mouth centre to piston face).
- Piston too stiff -> a drop of silicone grease on the O-ring; leaky -> O-ring 16x2.5 or wrap
  felt tape in the groove instead.

Hardware: 1x NBR O-ring 16 x 2 mm (ID x CS) [alt: 16x2.5 or self-adhesive felt strip 3 mm],
silicone grease, CA or ABS glue (rod into piston).
Assembly: 1) slide cap onto the rod from the plain end (cup opening toward the plain end);
2) glue the rod end into the piston socket, let cure; 3) fit O-ring, grease lightly;
4) push piston into the tube bottom; 5) push cap onto the tube end (snug, add tape if loose).
ABS is not food-safe — personal use, rinse after playing.

Assumptions
- A4 = 440 Hz equal temperament; mouth correction factor 1.6 r_m; the small flat bulge under
  the window and the ramp volume are ignored (a slide whistle is pitched by ear anyway).
- Model coordinates = print layout (hand-held instrument, no resting pose).
- Bore via hole_d() so the printed vertical bore comes out at 20 mm.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,
    loads=[],                     # 4 separate bodies intended: body, piston, cap, rod+ring
    print_orientation=(0, 0, 0),  # body mouthpiece-up: windway is vertical walls, no supports
    supports="off",
    brim="auto",
)

# Acoustics
C_SOUND = 343_000.0
F_LOW = 392.00          # G4
RANGE_OCT = 19 / 12     # ~1.5 octaves (19 semitones) -> D6
MOUTH_K = 1.6

# Bore / head
BORE_D = 20.0
TUBE_WALL = 2.4
R_HEAD = 15.5
WW_H = 1.2
WW_W = 14.0             # 0.7 x bore
WW_LEN = 30.0
WIN_L = 5.0
EDGE = 0.6
LAB_ANGLE = 18.0
COVER = 1.6
T_FRONT = WW_H + COVER
BULGE_DOWN = 8.0        # flat-front bore section below the labium
BEAK = (18.0, 9.0, 8.0)  # mouthpiece beak w, d, h on top of the head
BEAK_Y = -9.0           # beak centre (kept inside the head outline: no overhang)

# Piston / rod / cap
PISTON_GAP = 0.4        # radial clearance piston to bore (O-ring seals)
P_LEN = 14.0
ORING_CS = 2.0
ORING_SQUEEZE = 0.15
GROOVE_W = ORING_CS * 1.3
ROD_W, ROD_T = 8.0, 6.0
SOCKET = 8.0
GLUE_GAP = 0.1
BOTTOM_MARGIN = 2.0     # piston bottom above tube end at lowest note
CAP_T = 3.0
CAP_DEPTH = 8.0
CAP_WALL = 2.0
CAP_FIT = 0.15          # snug
SLOT_GAP = 0.3
RING_ID, RING_OD = 22.0, 34.0
RING_GAP = 12.0         # rod sticking out below cap at the highest note

R_B = hole_d(BORE_D) / 2
R_T = BORE_D / 2 + TUBE_WALL
S_P = math.pi * (BORE_D / 2) ** 2
S_M = WW_W * WIN_L
L_M = T_FRONT / 2 + MOUTH_K * math.sqrt(S_M / math.pi)
F_HIGH = F_LOW * 2 ** RANGE_OCT


def pipe_len(f):
    k = 2 * math.pi * f / C_SOUND
    return math.atan(1 / (k * L_M * S_P / S_M)) / k


L_LOW, L_HIGH = pipe_len(F_LOW), pipe_len(F_HIGH)
STROKE = L_LOW - L_HIGH
Z_MC = L_LOW + P_LEN + BOTTOM_MARGIN
Z_LAB = Z_MC - WIN_L / 2
Z_W = Z_LAB + WIN_L
ROD_LEN = SOCKET + (Z_MC - L_HIGH - P_LEN) + CAP_T + RING_GAP


def yz_prism(pts, width):
    return extrude(Plane.YZ * Polygon(*pts, align=None), width / 2, both=True)


def body():
    ramp_h = 2 * R_B
    z_head0 = Z_LAB - BULGE_DOWN - 6
    z_top = Z_W + WW_LEN - BEAK[2]
    b = Cylinder(R_T, z_head0, align=ON_BED)
    b = chamfer(b.edges().group_by(Axis.Z)[0], 0.4)
    b += Pos(0, 0, z_head0) * Cone(R_T, R_HEAD, R_HEAD - R_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    b += Pos(0, 0, z_head0 + R_HEAD - R_T) * Cylinder(R_HEAD, z_top - z_head0 - (R_HEAD - R_T), align=ON_BED)
    y_ww = -R_B - WW_H / 2
    beak = Pos(0, BEAK_Y, z_top) * extrude(RectangleRounded(BEAK[0], BEAK[1], 3), BEAK[2])
    b += fillet(beak.edges().group_by(Axis.Z)[-1], 2)

    # bore + flat-front bulge + 45 deg ramp ceiling
    b -= Pos(0, 0, -1) * Cylinder(R_B, Z_W + 1, align=ON_BED)
    b -= Pos(0, -R_B / 2, Z_LAB - BULGE_DOWN) * Box(WW_W, R_B, Z_W - Z_LAB + BULGE_DOWN, align=ON_BED)
    envelope = Pos(0, 0, Z_W - 0.01) * (Cylinder(R_B, ramp_h + 1, align=ON_BED)
                                        + Pos(0, -R_B / 2, 0) * Box(WW_W, R_B, ramp_h + 1, align=ON_BED))
    ramp = yz_prism([(-R_B, Z_W - 0.01), (R_B + 1, Z_W - 0.01), (R_B + 1, Z_W + ramp_h + 1)], 2 * R_B + 2)
    b -= ramp & envelope
    # windway
    b -= Pos(0, y_ww, Z_W - 0.01) * Box(WW_W, WW_H, WW_LEN + 1, align=ON_BED)
    big = R_HEAD - R_B + 3
    # window
    b -= yz_prism([(-R_B, Z_LAB), (-R_B - big, Z_LAB), (-R_B - big, Z_W), (-R_B, Z_W)], WW_W)
    # upper lip 45 deg
    b -= yz_prism([(-R_B - WW_H, Z_W - 0.01), (-R_B - big, Z_W - 0.01),
                   (-R_B - big, Z_W + big - WW_H)], WW_W)
    # labium bevel
    drop = (big - EDGE) / math.tan(math.radians(LAB_ANGLE))
    b -= yz_prism([(-R_B - EDGE, Z_LAB + 0.01), (-R_B - big, Z_LAB + 0.01),
                   (-R_B - big, Z_LAB - drop)], WW_W)
    return b


def piston():
    r = BORE_D / 2 - PISTON_GAP
    p = Cylinder(r, P_LEN, align=ON_BED)
    p = chamfer(p.edges().group_by(Axis.Z)[0], 0.4)
    r_root = BORE_D / 2 - ORING_CS * (1 - ORING_SQUEEZE)
    z0 = (P_LEN - GROOVE_W) / 2
    dz = r + 0.5 - r_root
    groove = revolve(Plane.XZ * Polygon((r_root, z0), (r + 1, z0), (r + 1, z0 + GROOVE_W + dz),
                                        (r_root, z0 + GROOVE_W), align=None), Axis.Z, 360)
    p -= groove
    sx, sy = ROD_T + 2 * GLUE_GAP, ROD_W + 2 * GLUE_GAP
    p -= Pos(0, 0, -1) * Box(sx, sy, SOCKET + 1, align=ON_BED)
    roof = Polygon((-sx / 2, SOCKET - 0.01), (sx / 2, SOCKET - 0.01), (0, SOCKET + sx / 2), align=None)
    p -= extrude(Plane.XZ * roof, sy / 2, both=True)  # 45 deg gable instead of a flat bridge
    return p


def cap():
    r_in = R_T + CAP_FIT
    c = Cylinder(r_in + CAP_WALL, CAP_T + CAP_DEPTH, align=ON_BED)
    c = chamfer(c.edges().group_by(Axis.Z)[0], 0.4)
    c -= Pos(0, 0, CAP_T) * Cylinder(r_in, CAP_DEPTH + 1, align=ON_BED)
    c -= Pos(0, 0, -1) * Box(ROD_T + 2 * SLOT_GAP, ROD_W + 2 * SLOT_GAP, CAP_T + 2, align=ON_BED)
    return c


def rod():
    # lying flat: rod along +X, thickness ROD_T in Z, width ROD_W in Y; ring at x<0
    r = Pos(ROD_LEN / 2, 0, 0) * Box(ROD_LEN, ROD_W, ROD_T, align=ON_BED)
    ring = Pos(-RING_OD / 2 + 2, 0, 0) * (Cylinder(RING_OD / 2, ROD_T, align=ON_BED)
                                          - Cylinder(RING_ID / 2, ROD_T + 1, align=ON_BED))
    r = r + ring
    return chamfer(r.edges().group_by(Axis.Z)[0], 0.4)


def build():
    return [body(),
            Pos(R_HEAD + 18, 0, 0) * piston(),
            Pos(R_HEAD + 18, 32, 0) * cap(),
            Pos(-R_HEAD - 5, -40, 0) * Rot(0, 0, -90) * rod()]


if __name__ == "__main__":
    print(f"L_LOW {L_LOW:.1f} L_HIGH {L_HIGH:.1f} F_HIGH {F_HIGH:.1f} stroke {STROKE:.1f} "
          f"Z_MC {Z_MC:.1f} rod {ROD_LEN:.1f} L_M {L_M:.2f}")
    for n, f in [("G4", 392), ("C5", 523.25), ("G5", 783.99), ("C6", 1046.5), ("D6", 1174.66)]:
        print(n, f, round(pipe_len(f), 1))
