"""train-whistle: 4-chamber steam-train whistle, C7 chord C5-E5-G5-Bb5, one mouthpiece.

Spec
- Four stopped square pipes (bore SQ_BORE = 16 mm square) in a 2x2 cluster, all fed from one
  mouthpiece through a tapered plenum into four vertical windways (1.2 x 12 mm, 25 mm long).
  Front pair's mouths face -Y, back pair's face +Y. Each mouth: 12 mm wide x 5 mm cut-up,
  labium edge 0.6 mm thick, outer labium bevel 18 deg; upper lip cut at 45 deg (no bridge).
- Pipes are open at the bottom and stopped by 4 printed sliding TUNING PLUGS (square bars).
  Plug length is computed so that, pushed in until PLUG_PROTRUDE (8 mm) sticks out, each pipe
  has its computed acoustic length. Slide to tune, then lock with PTFE tape friction / glue.
- Whole body prints mouthpiece-up, pipes vertical: windways are vertical slots (vertical walls,
  no support), bore ceilings are 45 deg ramps. Plugs print lying flat beside it, one plate.

Physics (c = 343 m/s, 20 C). Stopped pipe excited at a mouth (window) of area S_m in a bore of
area S_p. The mouth is an acoustic mass of length L_m = t_m + 1.6 r_m (r_m = sqrt(S_m/pi)).
Resonance of closed pipe + series mouth inertance:
    cot(k L) = k L_m S_p / S_m,   k = 2 pi f / c   =>   L = arccot(k L_m S_p/S_m) / k
(the plain c/4f - 0.61 r formula ignores the mouth constriction and would be ~25 % sharp).
L is measured from the plug face to the mouth centre.

TUNING (S_p = 256 mm2, S_m = 60 mm2, L_m ~ 8.4 mm; c/4f shown for reference)
  note | target Hz | c/4f (mm) | acoustic L plug->mouth (mm) | plug length (mm)
  C5   | 523.25    | 163.9     | 129.4                       | 28.0
  E5   | 659.26    | 130.1     |  96.3                       | 61.1
  G5   | 783.99    | 109.4     |  76.3                       | 81.1
  Bb5  | 932.33    |  92.0     |  59.8                       | 97.6
  (exact values: run `python model.py`; recomputed from params on every build)

Fine-tuning after printing
- Blow with steady moderate pressure; check each pipe with a tuner while covering the other
  three mouths with fingers (or before inserting the other plugs: an open-bottom pipe barely
  speaks). Push a plug in (shorter) to sharpen, pull out to flatten: ~1 mm = 0.8-1.7 % pitch.
  Each plug can travel about +-10 mm from nominal. Mark the final depth, then wrap/glue.
- Plug too loose -> one more wrap of PTFE tape; too tight -> sand plug sides with 240 grit.
- Overblowing (squeal) -> blow softer; breathy/no tone -> clear windway of strings with a
  1 mm card, check labium edge is straight and sharp (400-grit, edge stays >= 0.4 mm).

Hardware: PTFE plumber's tape (12 mm), optional CA/ABS glue to fix plugs once tuned.
Assembly: deburr windways (slide a 1 mm feeler/card through), wrap each plug with 1 turn of
PTFE tape, insert plugs (longest plug in Bb5 pipe: back-right; C5 = front-left, E5 = front-right,
G5 = back-left) until PLUG_PROTRUDE remains, tune, fix.
ABS is not food-safe — personal use, rinse after playing.

Assumptions
- Equal temperament A4 = 440 Hz. Mouth-correction coefficient 1.6 r_m (between 1.5 and 1.7);
  the 45 deg ramp volume above each bore is ignored - plug travel absorbs these errors.
- Model coordinates = print orientation (hand-held instrument, no "in use" resting pose).
- Quality "fine" (windway instrument).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,
    loads=[],                  # 5 bodies is intended: whistle body + 4 tuning plugs on one plate
    print_orientation=(0, 0, 0),  # mouthpiece up: windways = vertical walls, no supports inside
    supports="off",
    brim="auto",
)

# Acoustics
C_SOUND = 343_000.0  # mm/s
NOTES = [("C5", 523.25), ("E5", 659.26), ("G5", 783.99), ("Bb5", 932.33)]
MOUTH_K = 1.6         # mouth end correction factor x r_m (1.5..1.7)

# Pipe / fipple geometry
SQ_BORE = 16.0        # square bore side
WALL = 2.0            # side / back / divider walls
WW_H = 1.2            # windway height (gap, Y)
WW_W = 12.0           # windway & mouth width (X) = 0.75 bore
WW_LEN = 25.0         # windway length (Z)
WIN_L = 5.0           # window length / cut-up (Z)
EDGE = 0.6            # labium tip thickness
LAB_ANGLE = 18.0      # labium outer bevel, deg from vertical
BLOCK_LIP = 0.0         # ramp starts right at the windway exit (block edge chamfered, no flat ledge)
COVER = 1.6           # windway outer wall
T_FRONT = WW_H + COVER

# Plenum / mouthpiece
PLEN_H = 20.0
MP_IN = (14.0, 8.0)   # mouthpiece inner opening
MP_WALL = 2.0
MP_LEN = 14.0

# Plugs
STOP_MIN = 20.0       # plug engagement of the longest pipe at nominal
PLUG_PROTRUDE = 8.0
PLUG_GAP = 0.2        # per side, room for one wrap of PTFE tape
PLUG_SPACING = 22.0

S_P = SQ_BORE ** 2
S_M = WW_W * WIN_L
R_M = math.sqrt(S_M / math.pi)
L_M = T_FRONT / 2 + MOUTH_K * R_M   # mouth acoustic length (avg wall at mouth + end corr.)


def pipe_lengths():
    out = []
    for name, f in NOTES:
        k = 2 * math.pi * f / C_SOUND
        x = k * L_M * S_P / S_M
        out.append((name, f, C_SOUND / (4 * f), math.atan(1 / x) / k))
    return out


# pipe centres (x, side): side -1 = front (mouth faces -Y), +1 = back
PITCH = SQ_BORE + WALL
PIPES = [(-PITCH / 2, -1), (PITCH / 2, -1), (-PITCH / 2, 1), (PITCH / 2, 1)]
Y_IN = WALL / 2                      # bore inner edge (divider side)
Y_OUT = WALL / 2 + SQ_BORE           # bore mouth-side face
BODY_X = 2 * SQ_BORE + 3 * WALL
BODY_Y = 2 * (Y_OUT + T_FRONT)


def yz_prism(pts, x, width, side):
    """Prism from a YZ polygon (y given for the front side, mirrored for side=+1)."""
    pts = [(-side * y if side == 1 else y, z) for y, z in pts]
    return Pos(x, 0, 0) * extrude(Plane.YZ * Polygon(*pts, align=None), width / 2, both=True)


def build():
    lens = pipe_lengths()
    l_max = max(l for *_, l in lens)
    z_mc = l_max + STOP_MIN               # mouth centre height
    z_lab = z_mc - WIN_L / 2
    z_w = z_lab + WIN_L                   # windway exit
    z_wt = z_w + WW_LEN                   # windway top = plenum floor

    body = rounded_box(BODY_X, BODY_Y, z_wt, radius=2)
    # plenum outer + mouthpiece
    mp_out = (MP_IN[0] + 2 * MP_WALL, MP_IN[1] + 2 * MP_WALL)
    body += loft([Plane.XY.offset(z_wt) * RectangleRounded(BODY_X, BODY_Y, 2),
                  Plane.XY.offset(z_wt + PLEN_H) * RectangleRounded(*mp_out, 2)])
    body += Pos(0, 0, z_wt + PLEN_H) * extrude(RectangleRounded(*mp_out, 2), MP_LEN)

    # plenum cavity
    pl_x = PITCH + WW_W
    pl_y = 2 * (Y_OUT + WW_H)
    cav = loft([Plane.XY.offset(z_wt - 0.01) * Rectangle(pl_x, pl_y),
                Plane.XY.offset(z_wt + PLEN_H) * RectangleRounded(*MP_IN, 1.5)])
    cav += Pos(0, 0, z_wt + PLEN_H - 0.01) * extrude(RectangleRounded(*MP_IN, 1.5), MP_LEN + 1)
    body -= cav

    big = T_FRONT + 1
    for (x, side) in PIPES:
        s = side
        yb = s * (Y_IN + Y_OUT) / 2
        # bore, open at bottom
        body -= Pos(x, yb, -1) * Box(SQ_BORE, SQ_BORE, z_w + 1, align=ON_BED)
        # 45 deg ceiling ramp rising away from the mouth side
        ramp = SQ_BORE - BLOCK_LIP
        body -= yz_prism([(-Y_OUT + BLOCK_LIP, z_w - 0.01), (-Y_IN, z_w - 0.01),
                          (-Y_IN, z_w + ramp)], x, SQ_BORE, s)
        # windway slot (vertical walls)
        body -= Pos(x, s * (Y_OUT + WW_H / 2), z_w - 0.01) * Box(WW_W, WW_H, WW_LEN + 0.02,
                                                                align=ON_BED)
        # window
        body -= yz_prism([(-Y_OUT, z_lab), (-Y_OUT - big, z_lab),
                          (-Y_OUT - big, z_w), (-Y_OUT, z_w)], x, WW_W, s)
        # upper lip 45 deg
        body -= yz_prism([(-Y_OUT - WW_H, z_w - 0.01), (-Y_OUT - big, z_w - 0.01),
                          (-Y_OUT - big, z_w + big - WW_H)], x, WW_W, s)
        # labium bevel
        drop = (big - EDGE) / math.tan(math.radians(LAB_ANGLE))
        body -= yz_prism([(-Y_OUT - EDGE, z_lab + 0.01), (-Y_OUT - big, z_lab + 0.01),
                          (-Y_OUT - big, z_lab - drop)], x, WW_W, s)

    parts = [body]
    # tuning plugs, lying flat beside the body (+Y), order = NOTES = PIPES
    w = SQ_BORE - 2 * PLUG_GAP
    for i, (_, _, _, l) in enumerate(lens):
        plug_len = z_mc - l + PLUG_PROTRUDE
        plug = Box(plug_len, w, w, align=ON_BED)
        plug = chamfer(plug.edges().group_by(Axis.Z)[0], 0.4)
        parts.append(Pos(0, BODY_Y / 2 + 6 + w / 2 + i * PLUG_SPACING, 0) * plug)
    return parts


if __name__ == "__main__":
    z_mc = max(l for *_, l in pipe_lengths()) + STOP_MIN
    for n, f, q, l in pipe_lengths():
        print(f"{n} | {f} | {q:.1f} | {l:.1f} | plug {z_mc - l + PLUG_PROTRUDE:.1f}")
