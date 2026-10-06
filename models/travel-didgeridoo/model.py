"""travel-didgeridoo: compact folded (5-run serpentine) didgeridoo, drone D2 = 73.4 Hz.

Spec
- Lip-buzzed pipe, closed at the lips / open at the bell. Bore flares linearly (conical) from
  ID 30 mm at the mouthpiece to ID 54 mm at the bell along a ~1.44 m centreline.
- Folded into 5 vertical straight runs (row, 66 mm pitch) joined by 4 return-bend blocks:
  vertical socket -> short riser -> horizontal teardrop channel -> riser -> socket.
  Assembled size ~ 325 x 66 x ~300 mm; bell opens downward at the end of run 5.
- Parts (10, one plate, laid out in PRINT orientation): 5 bore tubes (printed upright),
  4 bend blocks (printed sockets-down, channel teardrop tip up -> no internal support),
  1 mouthpiece (printed socket-down, rim up; 30 mm ID smooth rounded rim, beeswax-friendly).
- Tubes are thin conical shells (bore + 2.4 mm wall); tube ends are plain spigots that slide into 0.3 mm-oversize sockets (SOCK deep) and
  are glued (ABS cement / acetone-ABS slurry) -> airtight. Mouthpiece is a friction/tape fit so
  it can slide for tuning before gluing.

ABS is not food-safe — personal use, rinse after playing.

Physics (computed in code, see TUNING)
- Conical frustum closed at the narrow end, open at the wide end: with x1 = distance from the
  cone apex to the mouth (x1 = r_mouth * La / (r_bell - r_mouth)) the resonances satisfy
  k*La + arctan(k*x1) = n*pi  (cylinder limit gives the c/(4L) series; the flare raises f, so
  the physical bore is LONGER than c/(4f) = 1.17 m). La = L + 0.61*r_bell (unflanged end).
- The bends add their centreline (2 risers + pitch) to the path; the tube length per run is
  what is left after mouthpiece + bends, divided by 5.

TUNING
| note | target Hz | computed dimension |
|------|-----------|--------------------|
| D2 drone (n=1) | 73.4 | bore centreline L = 1440 mm (La 1456 mm, cone-closed root k*La = 1.955) |
| 1st toot (n=2) | 182.7 (~F#3) | same bore, root n=2 of k*La + atan(k*x1) = 2*pi |
| tube run length | - | 5 x TUBE_LEN 179.7 mm + 4 bends x 127.8 mm + mouthpiece 30 mm |
| tuning slide | -1.4 % (~-24 cents) | mouthpiece pulled out MP_PULL 8 mm nominal, 0..SOCK_MP range |

Fine-tune after printing: dry-assemble with tape on the bend joints, play against a tuner.
Flat -> push the mouthpiece further on (up to 8 mm = +12 cents) or saw/sand the bell end
(1 mm of bell ~ +1.2 cents). Sharp -> pull mouthpiece out (up to 27 mm more) and wrap the gap
with tape. Glue the bend joints only when happy; keep mouthpiece removable (tape) for cleaning.

Hardware to buy: ABS cement or acetone (glue), ~20 g natural beeswax (rim), PTFE/electrical tape.

Assembly
1. Deburr socket mouths; dry-fit every tube (runs numbered 1..5 by OD: smallest = run 1).
2. Glue run1-bend1(bottom)-run2-bend2(top)-run3-bend3(bottom)-run4-bend4(top)-run5; keep all
   runs parallel and in one plane (lay the assembly flat on a table while the glue sets).
3. Test-blow for leaks (soapy water on joints); seal pinholes with acetone-ABS slurry.
4. Fit mouthpiece on run 1 (tape), warm beeswax and form a 2-3 mm ring on the rim.

Assumptions
- c = 343 m/s (20 C); sharp bends treated as their centreline length (small effect at 73 Hz,
  corrected by the tuning slide). Bore ID 30 -> 54 mm (typical modern didge).
- One quality per model: "standard" (0.20 mm) chosen for the bulky tubes; there is no
  windway/fipple (lip-buzzed), and the lip-contact rim gets a beeswax ring, so 0.12 mm "fine"
  for the mouthpiece is optional (re-slice it alone at fine if wanted).
- Parts are laid out in print orientation (print_orientation fixed), not in-use orientation.
- WARN "separate bodies" is intended: the kit is 10 parts printed on one plate.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",        # lip-buzzed, no windway; rim gets beeswax (see docstring)
    standing=False,            # hand-held
    loads=[],
    print_orientation=(0, 0, 0),  # parts already laid out in print orientation
    supports="off",
    brim="auto",
)

# Acoustics
C = 343.0                 # m/s at 20 C
F_DRONE = 73.42           # D2
R_MOUTH = 15.0            # bore radius at mouthpiece (ID 30)
R_BELL = 27.0             # bore radius at bell (ID 54)
END_CORR = 0.61           # unflanged open end, x r_bell
MP_PULL = 8.0             # nominal mouthpiece pull-out (tuning range both ways)

# Construction
N_RUNS = 5
WALL = 2.4                # tube wall at the widest end of each tube
SOCK = 18.0               # bend socket depth
SOCK_MP = 35.0            # mouthpiece socket depth (tuning slide)
GAP = 0.3                 # diametral socket clearance (glued slide fit)
BLOCK_WALL = 2.6
PITCH = 2 * (R_BELL + WALL + GAP / 2 + BLOCK_WALL) + 1.5   # run spacing
RISER = 4.0               # straight bore above socket before the channel
MP_RIM_W = 7.0            # rim width (lip contact)
MP_RIM_R = 3.0            # rim rounding radius
MP_TOP = 22.0             # mouthpiece bore length rim -> socket shoulder


def _root(n):
    """Solve u + atan(alpha*u) = n*pi for the closed-narrow-end cone."""
    alpha = R_MOUTH / (R_BELL - R_MOUTH)
    lo, hi = 1e-6, n * math.pi
    for _ in range(80):
        mid = (lo + hi) / 2
        if mid + math.atan(alpha * mid) < n * math.pi:
            lo = mid
        else:
            hi = mid
    return lo


K_ROOT = _root(1)
LA = K_ROOT * C / (2 * math.pi * F_DRONE) * 1000.0       # acoustic length, mm
L_BORE = LA - END_CORR * R_BELL                          # physical centreline, mm
F_TOOT = F_DRONE * _root(2) / K_ROOT
Z_C = SOCK + RISER + R_BELL                               # channel centre in bend block
BEND_PATH = 2 * (Z_C - SOCK) + PITCH
MP_PATH = MP_TOP + MP_PULL
TUBE_LEN = (L_BORE - MP_PATH - (N_RUNS - 1) * BEND_PATH) / N_RUNS


def r_at(s):
    return R_MOUTH + (R_BELL - R_MOUTH) * min(max(s / L_BORE, 0), 1)


def tube_span(i):
    s0 = MP_PATH + i * (TUBE_LEN + BEND_PATH)
    return s0, s0 + TUBE_LEN


def tube_od(i):
    return 2 * (r_at(tube_span(i)[1]) + WALL)


def make_tube(i):
    s0, s1 = tube_span(i)
    t = Cone(r_at(s1) + WALL, r_at(s0) + WALL, TUBE_LEN, align=ON_BED)
    t = chamfer(t.edges().group_by(Axis.Z)[0], 0.4)
    # printed with the wide end down
    bore = Pos(0, 0, -0.01) * Cone(r_at(s1), r_at(s0), TUBE_LEN + 0.02, align=ON_BED)
    return t - bore


def make_bend(j):
    """Bend j joins tube j (end) and tube j+1 (start). Printed sockets down."""
    ra = r_at(tube_span(j)[1])
    rb = r_at(tube_span(j + 1)[0])
    rc = (ra + rb) / 2
    sa = r_at(tube_span(j)[1]) + WALL + GAP / 2
    sb = r_at(tube_span(j + 1)[0] + SOCK) + WALL + GAP / 2
    # light outer: two socket cylinders + web + teardrop-section pipe over the channel
    blk = Pos(-PITCH / 2, 0, 0) * Cylinder(sa + BLOCK_WALL, Z_C, align=ON_BED)
    blk += Pos(PITCH / 2, 0, 0) * Cylinder(sb + BLOCK_WALL, Z_C, align=ON_BED)
    blk += Box(PITCH, 2 * (rc + BLOCK_WALL), Z_C, align=ON_BED)
    blk = chamfer(blk.edges().group_by(Axis.Z)[0], 0.4)
    blk += Pos(0, 0, Z_C) * teardrop_hole(
        2 * (rc + BLOCK_WALL), PITCH + 2 * max(ra, rb) + 2 * BLOCK_WALL, along="X")
    for x, s, r in ((-PITCH / 2, sa, ra), (PITCH / 2, sb, rb)):
        cut = Cylinder(s, SOCK, align=ON_BED)
        cut += Pos(0, 0, SOCK) * Cone(s, r, s - r, align=ON_BED)
        cut += Cylinder(r, Z_C, align=ON_BED)
        cut += Pos(0, 0, -0.01) * Cone(s + 0.6, s, 0.6, align=ON_BED)   # lead-in / foot
        blk -= Pos(x, 0, 0) * cut
    blk -= Pos(0, 0, Z_C) * teardrop_hole(2 * rc, PITCH + 2 * max(ra, rb), along="X")
    return blk


def make_mouthpiece():
    s = r_at(MP_PATH + SOCK_MP) + WALL + GAP / 2
    r_in = R_MOUTH
    r_out = s + BLOCK_WALL
    r_rim = r_in + MP_RIM_W
    flare_z = SOCK_MP + (s - r_in) + 4
    top = flare_z + max(r_rim - r_out, 0) + 6
    top = max(top, SOCK_MP + MP_TOP)
    prof = Polygon(
        (r_in, SOCK_MP + (s - r_in)), (s, SOCK_MP), (s, 0), (r_out, 0),
        (r_out, flare_z), (r_rim, flare_z + max(r_rim - r_out, 0)), (r_rim, top), (r_in, top),
        align=None,
    )
    mp = revolve(Plane.XZ * prof, Axis.Z, 360)
    mp = fillet(mp.edges().group_by(Axis.Z)[-1], MP_RIM_R)
    mp -= Pos(0, 0, -0.01) * Cone(s + 0.6, s, 0.6, align=ON_BED)
    return mp


def build():
    parts = []
    # tubes: two rows
    for i in range(N_RUNS):
        row, col = (0, i) if i < 3 else (1, i - 3)
        x = [-95, -30, 35][col] if row == 0 else [-95, -30][col]
        parts.append(Pos(x, -110 + row * 68, 0) * make_tube(i))
    parts.append(Pos(60, -42, 0) * make_mouthpiece())
    for j in range(N_RUNS - 1):
        bx = -72 if j % 2 == 0 else 72
        by = 38 if j < 2 else 110
        parts.append(Pos(bx, by, 0) * make_bend(j))
    return parts


if __name__ == "__main__":
    print(f"La={LA:.1f} L={L_BORE:.1f} tube={TUBE_LEN:.1f} bend={BEND_PATH:.1f} "
          f"pitch={PITCH:.1f} toot={F_TOOT:.1f} ods={[round(tube_od(i),1) for i in range(5)]}")
