"""temple-block: set of 3 Helmholtz-tuned temple/slit blocks (G4-B4-D5) + mallet head.

Spec
- Three closed, thick-walled (4 mm) resonators with a slit mouth on the player-facing front
  (-Y). Each cavity is a prism (along X) with a 45° gable roof so it prints with no support;
  the slit is cut at 45° through the wall (louvre) so its roof is a 45° overhang, not a bridge.
- Pitches a major + minor third apart: G4 392.00, B4 493.88, D5 587.33 Hz.
- Rear mounting boss per block: Ø10 mm horizontal stand-rod hole (along X, teardrop) with an
  M5 set screw from the back bearing on the rod; the M5 nut drops into a top-open slot.
  All three blocks slide onto one Ø10 rod (or one each on separate rods).
- Mallet head: Ø30 mm ABS head with a domed striking end and an Ø8 dowel socket.
- Everything prints together, upright, one plate, no supports. Quality "strong".
  Mesh WARN (4 bodies) is intended: 3 blocks + mallet head on one plate.

Physics (in code): f = c/(2 pi) * sqrt(A / (V * L_eff)), c = 343 m/s.
- Cavity volume V_target is derived from a nominal slit (SLIT_LEN_NOM) and then the cavity is
  built by scaling a fixed profile; V is then MEASURED from the CAD solid and the slit length
  is re-solved (bisection) for the exact target, so the printed geometry is self-consistent.
- Slit: vertical opening SLIT_H through a 45° louvre -> aperture width w = SLIT_H*cos45,
  neck length t = WALL/cos45; A = w*len; r_eq = sqrt(A/pi); L_eff = t + 1.7*r_eq.
- Designed TUNE_SHARP = +2 % (~34 cents) high on purpose: tape over the slit lowers f.

TUNING
  note | target Hz | design Hz (+2%) | cavity V cm3 (measured) | inner L x W x H mm | slit len x w x t mm
  G4   | 392.00    | 399.84          | 226.4                   | 94.0 x 47.0 x 63.0 | 60.0 x 4.24 x 5.66
  B4   | 493.88    | 503.76          | 142.6                   | 80.6 x 40.3 x 54.0 | 60.0 x 4.24 x 5.66
  D5   | 587.33    | 599.08          | 100.8                   | 71.8 x 35.9 x 48.1 | 60.0 x 4.24 x 5.66
  (printed by `python model.py`; slit w/t = aperture width / neck length along the 45° louvre;
  the same 60 mm slit on all three -> pitch set purely by cavity volume, V ~ 1/f^2)

Fine-tune after printing
- Strike the block, read the pitch with a tuner app (the air resonance is the sustained tone).
- Lower: cover part of the slit with tape from one end (A down -> f down, f ~ sqrt(A)).
  Each 10 % of slit length covered lowers ~5 % (~0.9 semitone).
- Raise: file the slit ends longer (each +1 mm of slit ~ +0.7 %), up to the cavity length.
- Brighter attack: hit the flat top band near the slit edge; for a drier click strike the ends.

Hardware to buy
- 1 x Ø10 mm rod, ~300 mm (steel/aluminium/wood dowel) for the stand, or a mic-stand adapter.
- 3 x M5 x 12 socket set screws or bolts + 3 x M5 hex nuts (rod clamps).
- 1 x Ø8 mm hardwood dowel, ~250 mm (mallet handle) + a drop of CA/epoxy.
- Optional: 6 thin rubber O-rings (10 mm ID) on the rod either side of each block (decoupling).

Assembly
1. Drop an M5 nut (flat down) into the slot on top of each boss.
2. Thread the M5 screw in from the back face through the nut; slide the blocks onto the rod
   (low -> high, left to right, slits facing the player), tighten lightly - over-tight
   clamping damps the ring.
3. Glue the dowel into the mallet head socket.

Assumptions
- c = 343 m/s (20 °C). Slit end correction approximated by the circle of equal area
  (1.7 r_eq, flanged); real slits radiate slightly less -> the +2 % sharp margin covers it.
- Walls 4 mm solid (ring); the shell's own plate modes are not tuned, only the air cavity.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,  # hangs on a stand rod
    loads=[],
    print_orientation=(0, 0, 0),  # upright: gable roofs + 45° slit louvres print support-free
    supports="off",
    brim="auto",
)

# physics
C_AIR = 343.0
NOTES = [("G4", 392.00), ("B4", 493.88), ("D5", 587.33)]
TUNE_SHARP = 1.02        # design this much sharp; tape lowers pitch
END_CORR = 1.7
SLIT_LEN_NOM = 60.0      # nominal slit length used to size the cavity [mm]

# geometry
WALL = 4.0
SLIT_H = 6.0             # vertical opening height of the louvre slit
PROF_W = 0.50            # cavity width / length
PROF_HW = 0.42           # vertical wall height / length (gable on top)
ROOF_FLAT = 0.0          # inner ridge flat width (0 = sharp 45° peak, no bridging)
ROOF_OUT_ANGLE = 60.0    # outer roof slope [deg from horizontal] -> wide flat strike band
SLIT_BELOW_EAVE = 3.0    # slit top this far below the inner eave
GAP = 10.0

ROD_D = 10.0
ROD_Z = 16.0             # rod axis height
BOSS_W = 26.0            # X
BOSS_D = 30.0            # Y, behind the back wall
BOSS_TOP = 38.0
NUT = "M5"

MALLET_D = 30.0
MALLET_H = 38.0
DOWEL_D = 8.0
DOWEL_DEPTH = 22.0


def k2(f):
    return (2 * math.pi * f / C_AIR) ** 2


def slit_neck():
    w = SLIT_H * math.cos(math.radians(45))   # aperture width perpendicular to the neck
    t = WALL / math.cos(math.radians(45))     # neck length along the 45° axis
    return w, t


def a_over_leff(length):
    w, t = slit_neck()
    A = w * length
    r = math.sqrt(A / math.pi)
    return A / (t + END_CORR * r) / 1000.0     # mm^2/mm -> m


def profile_area(s):
    wi, hw = PROF_W * s, PROF_HW * s
    roof_h = (wi - ROOF_FLAT) / 2
    return wi * hw + (wi + ROOF_FLAT) / 2 * roof_h


def cavity_scale(v_mm3):
    lo, hi = 20.0, 200.0
    for _ in range(60):
        s = (lo + hi) / 2
        if s * profile_area(s) < v_mm3:
            lo = s
        else:
            hi = s
    return s


def solve_slit(v_mm3, f):
    target = k2(f) * v_mm3 * 1e-9
    lo, hi = 2.0, 200.0
    for _ in range(60):
        L = (lo + hi) / 2
        if a_over_leff(L) < target:
            lo = L
        else:
            hi = L
    return L


def helm_f(v_mm3, length):
    return C_AIR / (2 * math.pi) * math.sqrt(a_over_leff(length) / (v_mm3 * 1e-9))


def profile(wi, hw, grow):
    """Gable profile in (Y, Z) of the cavity, grown by `grow` (outer = WALL, sharp corners)."""
    w = wi + 2 * grow
    roof_h = (wi - ROOF_FLAT) / 2
    z0 = -grow
    eave = hw + grow * math.tan(math.radians(22.5)) if grow else hw
    flat_half = ROOF_FLAT / 2 + grow * math.tan(math.radians(22.5))
    ridge = eave + (w / 2 - flat_half)
    top = [(flat_half, ridge), (-flat_half, ridge)] if flat_half > 0.05 else [(0, ridge)]
    return [(-w / 2, z0), (w / 2, z0), (w / 2, eave), *top, (-w / 2, eave)]


def outer_profile(wi, hw):
    """Outer (Y, Z) profile: walls WALL thick, 60° outer roof, flat striking band on top."""
    w = wi + 2 * WALL
    eave = hw + WALL
    ridge = hw + (wi - ROOF_FLAT) / 2 + WALL
    flat_half = w / 2 - (ridge - eave) / math.tan(math.radians(ROOF_OUT_ANGLE))
    return [(-w / 2, -WALL), (w / 2, -WALL), (w / 2, eave), (flat_half, ridge),
            (-flat_half, ridge), (-w / 2, eave)]


def prism(pts, length):
    """Extrude a (Y, Z) profile along X, centred on X=0."""
    # Plane.YZ: local x = +Y, local y = +Z, normal +X
    return extrude(Plane.YZ.offset(-length / 2) * Polygon(*pts, align=None), length)


def block(f):
    f_design = f * TUNE_SHARP
    v_target = a_over_leff(SLIT_LEN_NOM) / k2(f_design) * 1e9
    s = cavity_scale(v_target)
    li, wi, hw = s, PROF_W * s, PROF_HW * s
    cav = Pos(0, 0, WALL) * prism(profile(wi, hw, 0), li)
    outer = Pos(0, 0, WALL) * prism(outer_profile(wi, hw), li + 2 * WALL)
    v = cav.volume
    slit_len = solve_slit(v, f_design)
    assert slit_len < li - 8, "slit longer than the cavity"
    body = outer - cav
    # 45° louvre slit through the front (-Y) wall, rising toward the inside
    z_top = WALL + hw - SLIT_BELOW_EAVE
    y_in, y_out = -wi / 2, -wi / 2 - WALL
    sl = [(y_out - 1, z_top - SLIT_H - WALL - 1), (y_in + 0.01, z_top - SLIT_H),
          (y_in + 0.01, z_top), (y_out - 1, z_top - WALL - 1)]
    body -= prism(sl, slit_len)
    # rear boss with rod hole + set screw + side-loaded nut slot
    y0 = wi / 2 + WALL - 1
    boss = Pos(0, y0 + (BOSS_D + 1) / 2, 0) * Box(BOSS_W, BOSS_D + 1, BOSS_TOP,
                                                  align=(Align.CENTER, Align.CENTER, Align.MIN))
    body += boss
    yc = y0 + 1 + BOSS_D / 2
    body -= Pos(0, yc, ROD_Z) * teardrop_hole(clearance(ROD_D, "slide"), BOSS_W + 2, along="X")
    m = METRIC[NUT]
    y_back = y0 + 1 + BOSS_D
    # set screw from the back along Y (teardrop), nut dropped into a top-open slot (no ceiling)
    body -= Pos(0, (yc + y_back) / 2 + 1, ROD_Z) * teardrop_hole(m["clear"], y_back - yc + 2, along="Y")
    nut_y = yc + ROD_D / 2 + 2.0 + (m["nut_h"] + 0.5) / 2
    across_corners = m["nut_af"] / math.cos(math.radians(30))
    slot_bot = ROD_Z - m["nut_af"] / 2 - 0.2
    body -= Pos(0, nut_y, (slot_bot + BOSS_TOP + 1) / 2) * Box(
        across_corners + 0.4, m["nut_h"] + 0.5, BOSS_TOP + 1 - slot_bot)
    try:
        body = chamfer(body.edges().group_by(Axis.Z)[0], 0.4)
    except Exception:
        pass
    info = dict(v=v, L=li, W=wi, H=hw + (wi - ROOF_FLAT) / 2, slit=slit_len,
                f=helm_f(v, slit_len), fd=f_design)
    return body, info


def mallet():
    r = MALLET_D / 2
    pts = [(0, 0), (r - 0.4, 0), (r, 0.4), (r, MALLET_H - r)]
    for i in range(1, 21):  # dome to 75° then a small flat (no pole -> clean mesh)
        a = math.radians(75 * i / 20)
        pts.append((r * math.cos(a), MALLET_H - r + r * math.sin(a)))
    pts.append((0, pts[-1][1]))
    head = revolve(Plane.XZ * Polygon(*pts, align=None), Axis.Z, 360)
    d = hole_d(DOWEL_D)  # socket with a 90° drill-point roof (no flat ceiling)
    head -= Cylinder(d / 2, DOWEL_DEPTH, align=ON_BED) + Pos(0, 0, DOWEL_DEPTH) * Cone(
        d / 2, 0.01, d / 2, align=ON_BED)
    return head


def blocks():
    return [block(f) for _, f in NOTES]


def build():
    parts = []
    x = 0.0
    for b, info in blocks():
        bb = b.bounding_box()
        parts.append(Pos(x - bb.min.X, -bb.min.Y, 0) * b)
        x += bb.size.X + GAP
    ymax = max(p.bounding_box().max.Y for p in parts)
    parts.append(Pos(MALLET_D / 2, ymax + GAP + MALLET_D / 2, 0) * mallet())
    return parts


if __name__ == "__main__":
    w, t = slit_neck()
    for (n, f), (b, i) in zip(NOTES, blocks()):
        print(f"{n} | {f:.2f} | {i['fd']:.2f} | {i['v'] / 1000:.1f} | {i['L']:.1f} x {i['W']:.1f} x "
              f"{i['H']:.1f} | {i['slit']:.1f} x {w:.2f} x {t:.2f} | check {i['f']:.2f}  bbox {b.bounding_box().size}")
