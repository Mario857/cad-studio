"""pan-flute: 8-pipe edge-blown pan flute in C major, C5..C6, closed (stopped) pipes.

Spec
- 8 stopped pipes, bore BORE_D = 14 mm, wall 1.6 mm, fused side by side along a gentle arc
  (radius ARC_R) so the blowing rims follow the lower lip. All open ends at the same height.
- Each open top is bevelled on the outside (cone, BEVEL_ANGLE from vertical) down to a sharp
  rim EDGE = 0.6 mm thick: that rim is the "labium" the air jet splits on. No windway.
- Closed end = solid floor (FLOOR mm) at the bottom of each bore. Below the floor of the shorter
  pipes is a dead cavity open at the bottom (45° conical ceiling, prints support-free) so every
  pipe stands on the bed and the block prints pipes-vertical, open end up, zero supports.
- Acoustic lengths are derived below from physics and printed TRIM_ALLOW (3 %) long for sanding.

Physics (c = 343 m/s at 20 °C)
  stopped pipe: f = c / (4 (L + dL)),   dL = 0.61 r  (unflanged open end)
  => L = c / (4 f) - 0.61 r      ;  printed bore depth = L * (1 + TRIM_ALLOW)

TUNING (bore 14 mm, r = 7 mm, dL = 4.27 mm)
  note | target Hz | acoustic L (mm) | printed bore depth (mm, +3 %)
  C5   | 523.25    | 159.6           | 164.4
  D5   | 587.33    | 141.7           | 146.0
  E5   | 659.26    | 125.8           | 129.6
  F5   | 698.46    | 118.5           | 122.1
  G5   | 783.99    | 105.1           | 108.3
  A5   | 880.00    |  93.2           |  96.0
  B5   | 987.77    |  82.5           |  85.0
  C6   | 1046.50   |  77.7           |  80.0
  (exact values are recomputed by pipe_lengths() whenever a param changes)

Fine-tuning after printing (each pipe prints ~3 % flat, ~50 cents)
- Play each pipe against a tuner (blow gently across the rim, lip covering ~1/4 of the opening).
- Too flat -> sand the TOP flat on 240-grit paper on a table (1 mm shortening ~ +0.6..1.3 %
  pitch, long..short pipe), then re-cut the outer bevel with a deburring tool / 400 grit until
  the rim is sharp again (~0.5 mm).
- Fine upward steps without sanding: press beeswax pellets to the bottom of the bore (raises
  the closed end = shorter pipe = sharper; remove wax to go back).
- Too sharp (over-sanded) -> glue a 1-2 mm ABS ring on the top and re-bevel, or reprint.
- Ultra-fine: tilt the instrument / cover more of the opening with the lip (flattens ~20 cents).

Hardware: none. Optional: beeswax for tuning, 400-grit paper.
Assembly: one piece. Deburr rims, wash out, tune as above.
ABS is not food-safe — personal use, rinse after playing.

Assumptions
- Equal-tempered A4 = 440 Hz; end correction 0.61 r (unflanged), lip partly shading the end
  lowers pitch slightly - compensated by the sanding allowance.
- Print quality "fine" (edge-blown instrument; smooth bore and crisp rims matter).
- Rim EDGE 0.6 mm is the thinnest wall the audit accepts; sand to ~0.5 mm by hand if wanted.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,            # hand-held
    loads=[],
    print_orientation=(0, 0, 0),  # pipes vertical, open end up (as modelled) -> bores & rims clean
    supports="off",
    brim="auto",
)

# Acoustics
C_SOUND = 343_000.0  # mm/s at 20 C
NOTES = [("C5", 523.25), ("D5", 587.33), ("E5", 659.26), ("F5", 698.46),
         ("G5", 783.99), ("A5", 880.00), ("B5", 987.77), ("C6", 1046.50)]
END_CORR_K = 0.61      # x radius, unflanged open end
TRIM_ALLOW = 0.03      # print 3 % long, sand down to pitch

# Geometry
BORE_D = 14.0
WALL = 1.6
FLOOR = 3.0            # closed-end floor thickness
EDGE = 0.6             # rim (labium) thickness at the top
BEVEL_ANGLE = 30.0     # outer bevel, degrees from vertical
FUSE_OVERLAP = 1.2     # adjacent outer walls overlap so pipes fuse into one block
ARC_R = 90.0           # row curvature radius; tighter arc also gives a deeper, stable print footprint
BOTTOM_CHAMFER = 0.4

R_BORE = BORE_D / 2
R_OUT = R_BORE + WALL


def pipe_lengths():
    """Printed bore depth for each note (closed pipe, unflanged end correction, +trim)."""
    out = []
    for name, f in NOTES:
        l_ac = C_SOUND / (4 * f) - END_CORR_K * R_BORE
        out.append((name, f, l_ac, l_ac * (1 + TRIM_ALLOW)))
    return out


def build() -> Part:
    lens = pipe_lengths()
    top = max(l for *_, l in lens) + FLOOR
    pitch = 2 * R_OUT - FUSE_OVERLAP
    dtheta = pitch / ARC_R
    n = len(lens)
    bev_h = (R_OUT - (R_BORE + EDGE)) / math.tan(math.radians(BEVEL_ANGLE))

    centers = []
    for i in range(n):
        th = (i - (n - 1) / 2) * dtheta
        # arc bulges toward -Y (player side); center of arc at (0, ARC_R)
        centers.append((ARC_R * math.sin(th), ARC_R - ARC_R * math.cos(th)))

    body = None
    for (x, y) in centers:
        shaft = Cylinder(R_OUT, top - bev_h, align=ON_BED)
        shaft = Pos(x, y, 0) * chamfer(shaft.edges().group_by(Axis.Z)[0], BOTTOM_CHAMFER)
        cone = Pos(x, y, top - bev_h) * Cone(R_OUT, R_BORE + EDGE, bev_h,
                                              align=(Align.CENTER, Align.CENTER, Align.MIN))
        p = shaft + cone
        body = p if body is None else body + p

    for (x, y), (_, _, _, lp) in zip(centers, lens):
        body -= Pos(x, y, top - lp) * Cylinder(R_BORE, lp + 1, align=ON_BED)
        h_dead = top - lp - FLOOR
        if h_dead > R_BORE + 2:
            cyl_h = h_dead - R_BORE
            dead = Pos(x, y, -1) * Cylinder(R_BORE, cyl_h + 1, align=ON_BED)
            dead += Pos(x, y, cyl_h) * Cone(R_BORE, 0.5, R_BORE - 0.5,
                                            align=(Align.CENTER, Align.CENTER, Align.MIN))
            body -= dead
    return body


if __name__ == "__main__":
    for name, f, la, lp in pipe_lengths():
        print(f"{name} | {f:.2f} | {la:.1f} | {lp:.1f}")
