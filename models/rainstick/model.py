"""rainstick: 3-segment Ø50 rainstick (~0.9 m) with a helix of 50°-sloped diametral pins.

Spec
- Tube OD 50 mm, wall 2.4 mm (bore 45.2 mm), 3 segments x 290 mm -> ~870 mm overall.
- Each segment carries a helix of diametral rods (Ø3 mm), one every ROD_DZ = 7 mm, rotated
  HELIX_STEP = 40° per rod (helix pitch 63 mm/turn). Rods slope 50° from horizontal, so they
  print upright without supports (start embedded in the wall, underside 40° from vertical); all
  rods cross the axis at different heights (vertical gap ≥ 2.3 mm), so they never fuse.
- Segments 1 and 2 end in a 12 mm spigot that slides (0.3 mm diametral gap) into the bore of
  the next segment; the spigot contains a 45° funnel ending in an ORIFICE (Beverloo restrictor)
  that sets how long the rain lasts. Glue the spigots (or tape them, to swap fills).
- 2 end caps plug the open ends (friction fit + tape so the fill can be changed).
- Parts laid out in print orientation (segments upright, spigot up; caps disc-down).

TUNING / physics
| quantity | target | computed dimension |
|----------|--------|--------------------|
| rain duration (flow) | 10 s for 80 g rice | orifice D0 = 10.9 mm (Beverloo W = C·ρb·√g·(D0−k·d)^2.5, C 0.58, k 1.5, ρb 800 kg/m³, d 2 mm) -> 8 g/s |
| rod coverage per rod | – | 2·d/(π·R) = 8.4 % of bore area |
| mean free drop | – | Δh = ROD_DZ / coverage ≈ 83 mm |
| single-grain transit | ~1.4 s | T = L·√(2/(g·Δh)) (grain stops at each hit, then free-falls Δh) |
| click rate | ~3400 /s | (W / 0.025 g per grain) × L/Δh hits per grain |
| air-column mode 1/2/3 | 197 / 394 / 591 Hz | closed-closed tube: f = n·c/(2L), L = 870 mm |
Denser rods (smaller ROD_DZ) -> longer single-grain transit, softer "drizzle"; larger ORIFICE
-> louder, shorter rain. Cavity modes colour the hiss slightly; caps closed both ends.

Fine-tune after printing: try the fill first with tape-on caps. Too short -> add rice or
narrow the orifice (glue in a washer); too long/thin -> drill the orifice out 1 mm at a time
(Beverloo: +1 mm D0 ≈ +30 % flow). Mixing in a few lentils/beads adds bright clicks.

Hardware to buy: ~80 g long-grain rice (or 2 mm beads / lentil mix), ABS cement or tape.

Assembly
1. Deburr spigots; dry-fit seg1 spigot into seg2, seg2 spigot into seg3 (align helices freely).
2. Glue the two joints (ABS cement) or wrap with tape for a re-fillable stick.
3. Fill 60-100 g of rice through an open end, press the caps in, tape or glue them.

Assumptions
- Rice bulk density 800 kg/m³, grain 2 mm thick / 0.025 g; c = 343 m/s.
- The orifice is what limits the flow (the 45.2 mm bore and the rod gaps are much wider).
- Parts are laid out in print orientation; WARN "separate bodies" is intended (5-part kit).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # parts already laid out in print orientation
    supports="off",
    brim="auto",
)

# Physics targets
C = 343.0
G = 9.81
RAIN_S = 10.0             # target rain duration, s
FILL_G = 80.0             # rice fill, g
RHO_BULK = 800.0          # kg/m3
GRAIN_D = 2.0             # mm
BEV_C, BEV_K = 0.58, 1.5

# Geometry
OD = 50.0
WALL = 2.4
SEG_H = 290.0
N_SEG = 3
SPIG = 12.0
GAP = 0.3
ROD_D = 3.0
ROD_DZ = 7.0
HELIX_STEP = 40.0         # deg per rod
ROD_ANGLE = 50.0          # deg from horizontal
CAP_T = 3.0
CAP_PLUG = 10.0

R_IN = OD / 2 - WALL
W_KGS = FILL_G / 1000 / RAIN_S
ORIFICE = ((W_KGS / (BEV_C * RHO_BULK * math.sqrt(G))) ** 0.4 + BEV_K * GRAIN_D / 1000) * 1000
ROD_SPAN = 2 * R_IN * math.tan(math.radians(ROD_ANGLE))
L_TOTAL = N_SEG * SEG_H
COVER = 2 * ROD_D / (math.pi * R_IN)
DROP = ROD_DZ / COVER
T_GRAIN = L_TOTAL / 1000 * math.sqrt(2 / (G * DROP / 1000))
MODES = [n * C / (2 * L_TOTAL / 1000) for n in (1, 2, 3)]


def rods(z_lo, z_hi, phase=0):
    out = []
    n = int((z_hi - ROD_SPAN - z_lo) // ROD_DZ) + 1
    length = 2 * R_IN / math.cos(math.radians(ROD_ANGLE)) + 2.0
    for k in range(n):
        zc = z_lo + k * ROD_DZ + ROD_SPAN / 2
        rod = Rot(0, -(90 - ROD_ANGLE), 0) * Cylinder(ROD_D / 2, length)
        out.append(Rot(0, 0, phase + k * HELIX_STEP) * Pos(0, 0, zc) * rod)
    return Compound(out) & Cylinder(R_IN + 1.0, SEG_H, align=ON_BED)


def segment(idx):
    with_spigot = idx < N_SEG - 1
    t = Cylinder(OD / 2, SEG_H, align=ON_BED)
    t = chamfer(t.edges().group_by(Axis.Z)[0], 0.4)
    t -= Pos(0, 0, -0.01) * Cylinder(R_IN, SEG_H + 0.02, align=ON_BED)
    t -= Pos(0, 0, -0.01) * Cone(R_IN + 0.6, R_IN, 0.6, align=ON_BED)
    top_free = 12.0 if with_spigot else CAP_PLUG + 3
    t += rods(SPIG + 3, SEG_H - top_free, phase=idx * 120)
    if with_spigot:
        top = SEG_H + SPIG
        r0 = ORIFICE / 2
        sp = Pos(0, 0, SEG_H - 8) * Cylinder(R_IN + 0.5, 8, align=ON_BED)
        sp += Pos(0, 0, SEG_H) * Cylinder(R_IN - GAP / 2, SPIG, align=ON_BED)
        sp = chamfer(sp.edges().group_by(Axis.Z)[-1], 0.6)
        cone_h = R_IN + 0.5 - r0
        cut = Pos(0, 0, top - 2 - cone_h) * Cone(R_IN + 0.5, r0, cone_h, align=ON_BED)
        cut += Pos(0, 0, top - 2.01) * Cylinder(r0, 2.1, align=ON_BED)
        cut += Pos(0, 0, top - 2 - cone_h - 5) * Cylinder(R_IN + 0.5, 5.01, align=ON_BED)
        t += sp - cut
    return t


def cap():
    c = Cylinder(OD / 2, CAP_T, align=ON_BED)
    c = chamfer(c.edges().group_by(Axis.Z)[0], 0.4)
    plug = Pos(0, 0, CAP_T) * Cylinder(R_IN - GAP / 2, CAP_PLUG, align=ON_BED)
    plug -= Pos(0, 0, CAP_T) * Cylinder(R_IN - GAP / 2 - 2.0, CAP_PLUG + 0.1, align=ON_BED)
    plug = chamfer(plug.edges().group_by(Axis.Z)[-1], 0.5)
    return c + plug


def build():
    parts = [Pos(-60 + 60 * i, 0, 0) * segment(i) for i in range(N_SEG)]
    parts += [Pos(-30 + 60 * i, 60, 0) * cap() for i in range(2)]
    return parts


if __name__ == "__main__":
    print(f"orifice={ORIFICE:.2f} span={ROD_SPAN:.1f} cover={COVER:.3f} drop={DROP:.0f} "
          f"Tgrain={T_GRAIN:.2f} modes={[round(m) for m in MODES]}")
