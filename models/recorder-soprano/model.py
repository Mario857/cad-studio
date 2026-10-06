"""recorder-soprano: playable 3-piece soprano (descant) recorder in C5, baroque fingering.

Spec
- Range C5 (523.25 Hz) .. D7, A4 = 440 Hz equal temperament, baroque (English) fingering:
  thumb hole + 7 front holes, holes 6 and 7 are double holes (C#5 / D#5 by half-holing).
- 3 parts with press-fit tenons: head (beak, windway, window, labium), body (thumb + holes 1-6),
  foot (double hole 7). Head bore cylinder 13.0 mm, body/foot bore tapers 0.012 mm/mm toward the foot
  (soprano-like "narrowing" bore, simplified to one cone).
- Fipple: windway 9.0 x 1.2 mm, 25 mm long, window 9 x 4 mm, labium wedge 18 deg, tip 0.6 mm.
- Head OD 23, body/foot OD 20. Overall length ~ 323 mm (head 125.8, body 143.3, foot 71.7 incl. tenons).
- Acoustic design is done in build(): a lossless transfer-matrix (TMM) model of the stepped bore
  (1-2 mm cylinders), open tone holes as shunt inertances (t_e = t + 0.75 d, Benade/Nederveen),
  closed holes as shunt compliances (V = S_h t), foot radiation end correction 0.6133 a (unflanged),
  window as series inertance M = rho * L_w / S_w with L_w = t_edge + 1.7 r_eq (Helmholtz neck formula,
  r_eq = sqrt(S_w/pi)). The note sounds where Im(Z_window + Z_bore) = 0 (impedance minimum seen by the
  jet). Foot length is solved for C5, then each hole position is solved by bisection (bottom -> top),
  the small hole of each double pair is sized for its semitone. c = 343 m/s (20 C), rho = 1.204.
  Run `python models/recorder-soprano/model.py` to print the live table.

Assumptions
- Simplified to one cone instead of a real recorder's segmented bore; no hole undercutting.
- Window correction formula is an estimate (+-2 %) -> head joint is designed pulled out 2.0 mm, foot is
  printed FOOT_TRIM = 3 mm long and holes are placed HOLE_FLAT_CENTS = 12 cents flat so every error
  can be corrected by removing material (sanding foot / enlarging holes / pushing head in).
- Holes are teardrops (point up when printed) so they print without supports; area ~ +4 %.
- Parts are 3 separate bodies on one plate (intended). Print upright (in-use orientation): windway, window side walls and bore are vertical walls, labium
  ramp faces up, block ceiling is a 45 deg slope; no supports anywhere. WARN for the thin labium tip
  (0.6 mm) is intended: it is the sounding edge.
- ABS is not food-safe — personal use, rinse after playing.

TUNING (A4 = 440, computed by the TMM model, s = distance below the labium edge, mm; diameters
before teardrop; "flat" = designed 12 cents low on purpose so holes are enlarged to pitch)
| note | fingering (0=thumb) | target Hz | computed dimension |
|------|---------------------|-----------|--------------------|
| C5  | 0 1234567            | 523.25  | bore end s = 290.8 (+3 trim -> printed 293.8)      |
| C#5 | 0 123456 7s          | 554.37  | hole 7 small d = 2.6                                |
| D5  | 0 123456             | 587.33  | hole 7 pair s = 240.5, big d 4.6 (x -2.7/+2.7)     |
| D#5 | 0 12345 6s           | 622.25  | hole 6 small d = 2.8                                |
| E5  | 0 12345              | 659.26  | hole 6 pair s = 210.3, big d 4.6                   |
| F5  | 0 1234 _ 67 (fork)   | 698.46  | hole 5 s = 191.9, d 6.4                             |
| F#5 | 0 123 _ 56 _ (check) | 739.99  | model 734.1 Hz (-14 c, as designed flat)            |
| G5  | 0 123                | 783.99  | hole 4 s = 171.0, d 5.0                             |
| A5  | 0 12                 | 880.00  | hole 3 s = 149.7, d 6.0                             |
| B5  | 0 1                  | 987.77  | hole 2 s = 129.2, d 5.8                             |
| C6  | 0 _ 2 (fork)         | 1046.50 | hole 1 s = 112.5, d 5.2                             |
| C#6 | _ 12                 | 1108.73 | thumb s = 104.3, d 6.0                              |
All holes solve to exactly -12.0 cents (intended). Joints: head/body shoulder s = 98.8, body/foot s = 232.1.
Window: S_w = 36 mm2, L_w = 6.4 mm, equivalent end correction ~ 23 mm. Head socket design pull 2.0 mm.

Fine-tuning after printing (tuner, warm instrument, medium breath)
1. Overall pitch: push head in (sharpens, ~ 6 cents/mm) or pull out (flattens).
2. Low C5: sand the foot end square until C5 is in tune (1 mm ~ 7 cents sharper).
3. Each tone hole is ~12 cents flat by design: enlarge it with a 0.5 mm-step drill / round needle
   file, mostly on its lower edge (undercut toward the foot) until in tune; check the fork notes after.
4. Second octave cracks badly -> thumb hole slightly larger; airy tone -> deburr windway exit and keep
   the labium tip straight and sharp (fine sanding sponge, do not round it).

Hardware: none required. Optional: PTFE thread-seal tape (12 mm) for loose tenons, cork grease.

Assembly: 1. Remove brim, deburr windway with a 1 mm card. 2. Test-fit tenons; if too tight sand the
tenon with 400 grit, if loose wrap 1 turn PTFE tape. 3. Push foot onto body, rotate hole 7 pair to suit
the right little finger. 4. Push head onto body leaving ~2 mm gap at the shoulder, align window with
the finger holes. 5. Tune as above.
"""

import math
from functools import lru_cache

import numpy as np
from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",            # windway + labium
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # upright: windway walls vertical, labium ramp faces up
    supports="off",
    brim="on",                 # tall slender parts: "wobbly" WARN accepted, brim + 20 mm footprint (no load while printing)
)

# ---------------- acoustic targets ----------------
A4 = 440.0
C_SOUND = 343.0            # m/s at 20 C
RHO = 1.204                # kg/m3
NOTE_SEMI = dict(C5=3, Cs5=4, D5=5, Ds5=6, E5=7, F5=8, Fs5=9, G5=10, A5=12, B5=14, C6=15, Cs6=16)
HOLE_FLAT_CENTS = 12.0     # holes placed flat; enlarge to tune
FOOT_TRIM = 3.0            # mm printed extra at the foot (sand to tune C5)
PULL = 2.0                 # head pulled out at nominal pitch (mm)

# ---------------- bore / body ----------------
BORE_HEAD = 13.0           # cylindrical head bore
TAPER_START = 55.0         # s (below labium) where the cone starts
TAPER = 0.012              # diameter loss per mm toward foot
HEAD_OD = 23.0
BODY_OD = 20.0
TENON_WALL = 2.0
TENON_L = 10.0
TENON_FIT = "press"
SOCKET_EXTRA = 1.0         # socket deeper than tenon (head can also be pushed in fully)

# ---------------- fipple ----------------
WW_W = 9.0                 # windway width (0.7 x bore)
WW_H = 1.2                 # windway height
WW_L = 25.0                # windway length
WIN_L = 4.0                # window length (labium to block)
EDGE_T = 0.6               # labium tip thickness
LAB_ANGLE = 18.0           # labium wedge angle (deg)
EDGE_Y = 4.6               # labium edge plane (from axis, toward window); chord >= WW_W
LAB_FILL_L = 12.0          # flat-bore length below the labium
BEAK_L = 22.0

# ---------------- tone holes (diameters chosen, positions solved) ----------------
D_THUMB, D1, D2, D3, D4, D5 = 6.0, 5.2, 5.8, 6.0, 5.0, 6.4
D6_BIG, D7_BIG = 4.6, 4.6
PAIR_SEP = 5.4             # centre distance of double holes (across X)
HOLE_MARGIN = 1.5          # min wall between hole edge and a joint

GAP = 35.0                 # part spacing on the plate (X)


def f_note(name):
    return A4 * 2 ** (NOTE_SEMI[name] / 12)


def bore_d(s):
    """Bore diameter (mm) at s mm below the labium edge."""
    return BORE_HEAD - TAPER * max(0.0, s - TAPER_START)


def wall_t(s, x_off=0.0):
    ro, rb = BODY_OD / 2, bore_d(s) / 2
    return math.sqrt(ro**2 - x_off**2) - math.sqrt(max(rb**2 - x_off**2, 0.01))


def window_inertance():
    s_w = WW_W * WIN_L
    l_w = EDGE_T + 1.7 * math.sqrt(s_w / math.pi)
    return RHO * (l_w * 1e-3) / (s_w * 1e-6), l_w, s_w


def sounding_freq(L, holes, target):
    """holes: list of (s_mm, d_mm, t_mm, is_open). Returns frequency closest to target (Hz)."""
    f = np.linspace(0.7 * target, 1.4 * target, 500)
    w = 2 * np.pi * f
    k = w / C_SOUND
    pts = sorted(set([float(x) for x in np.arange(0.0, L, 2.0)] + [h[0] for h in holes] + [L]))
    hole_at = {}
    for h in holes:
        hole_at.setdefault(h[0], []).append(h)
    a_end = bore_d(L) / 2e3
    z0 = RHO * C_SOUND / (math.pi * a_end**2)
    Z = 1j * z0 * np.tan(k * 0.6133 * a_end)
    for i in range(len(pts) - 1, 0, -1):
        s_lo, s_hi = pts[i - 1], pts[i]
        for (_, d, t, op) in hole_at.get(s_hi, []):
            sh = math.pi * (d / 2e3) ** 2
            if op:
                zh = 1j * w * RHO * ((t + 0.75 * d) * 1e-3) / sh
            else:
                zh = 1.0 / (1j * w * sh * t * 1e-3 / (RHO * C_SOUND**2))
            Z = 1.0 / (1.0 / Z + 1.0 / zh)
        a = bore_d((s_lo + s_hi) / 2) / 2e3
        z0 = RHO * C_SOUND / (math.pi * a**2)
        tn = np.tan(k * (s_hi - s_lo) * 1e-3)
        Z = z0 * (Z + 1j * z0 * tn) / (z0 + 1j * Z * tn)
    m_w = window_inertance()[0]
    X = w * m_w + Z.imag
    idx = np.where((X[:-1] < 0) & (X[1:] > 0))[0]
    if len(idx) == 0:
        return float("nan")
    cands = [f[i] - X[i] * (f[i + 1] - f[i]) / (X[i + 1] - X[i]) for i in idx]
    return float(min(cands, key=lambda c: abs(c - target)))


# hole ids -> (diameter, x offset, side)
def _hole_list(H, L, open_ids):
    out = []
    for hid, (s, d, x) in H.items():
        out.append((s, d, wall_t(s, x), hid in open_ids))
    return out


LOW = ("6b", "6s", "7b", "7s")
FINGERINGS = {
    "C5": (), "Cs5": ("7s",), "D5": ("7b", "7s"), "Ds5": ("6s", "7b", "7s"), "E5": LOW, "F5": ("5",),
    "Fs5": ("4", "7b", "7s"), "G5": ("4", "5") + LOW, "A5": ("3", "4", "5") + LOW,
    "B5": ("2", "3", "4", "5") + LOW, "C6": ("1", "3", "4", "5") + LOW,
    "Cs6": ("T", "3", "4", "5") + LOW,
}


def _bisect(fun, lo, hi, n=28):
    """fun increasing in x; find x with fun(x)=0."""
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        if fun(mid) > 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


@lru_cache(maxsize=1)
def design():
    flat = 2 ** (-HOLE_FLAT_CENTS / 1200)
    H = {}  # id -> [s, d, x_off]
    L = 300.0
    d6s, d7s = 3.0, 3.2
    for _ in range(3):
        L = _bisect(lambda Lx: f_note("C5") - sounding_freq(Lx, _hole_list(H, Lx, ()), f_note("C5")),
                    200, 320, 24)

        def solve_pos(ids, diams, xs, note, lo, hi):
            def g(s):
                for i, d, x in zip(ids, diams, xs):
                    H[i] = [s, d, x]
                return f_note(note) * flat - sounding_freq(L, _hole_list(H, L, FINGERINGS[note]),
                                                           f_note(note))
            s = _bisect(g, lo, hi, 24)
            g(s)
            return s

        def solve_small(hid, note):
            def g(d):
                H[hid][1] = d
                return sounding_freq(L, _hole_list(H, L, FINGERINGS[note]), f_note(note)) - f_note(note) * flat
            return _bisect(g, 1.6, 4.6, 18)

        xo = PAIR_SEP / 2
        for _ in range(2):
            s7 = solve_pos(("7b", "7s"), (D7_BIG, d7s), (-xo, xo), "D5", 150, L - 6)
            d7s = solve_small("7s", "Cs5")
        for _ in range(2):
            s6 = solve_pos(("6b", "6s"), (D6_BIG, d6s), (-xo, xo), "E5", 120, s7 - 8)
            d6s = solve_small("6s", "Ds5")
        s5 = solve_pos(("5",), (D5,), (0,), "F5", 100, s6 - 6)
        s4 = solve_pos(("4",), (D4,), (0,), "G5", 80, s5 - 6)
        s3 = solve_pos(("3",), (D3,), (0,), "A5", 60, s4 - 6)
        s2 = solve_pos(("2",), (D2,), (0,), "B5", 45, s3 - 6)
        s1 = solve_pos(("1",), (D1,), (0,), "C6", 35, s2 - 6)
        solve_pos(("T",), (D_THUMB,), (0,), "Cs6", 30, s1 + 10)
    return L, {k: tuple(v) for k, v in H.items()}


def tuning_table():
    L, H = design()
    rows = []
    for n in FINGERINGS:
        f = sounding_freq(L + FOOT_TRIM, _hole_list(H, L, FINGERINGS[n]), f_note(n))
        f0 = sounding_freq(L, _hole_list(H, L, FINGERINGS[n]), f_note(n))
        rows.append((n, f_note(n), f0, 1200 * math.log2(f0 / f_note(n)), f))
    return L, H, rows


# ---------------- geometry ----------------
def _bore_pts(s_lo, s_hi, z_of):
    """(r, z) points of the bore from s_hi (lower) up to s_lo (upper), incl. the taper break."""
    ss = [s_hi] + ([TAPER_START] if s_lo < TAPER_START < s_hi else []) + [s_lo]
    return [(bore_d(s) / 2, z_of(s)) for s in ss]


def _rev(pts):
    return revolve(Plane.XZ * Polygon(*pts, align=None), Axis.Z, 360)


def _yz_prism(pts, x_half):
    """Polygon given as (y, z) points, extruded symmetric in X."""
    return extrude(Plane.YZ * Polygon(*pts, align=None), x_half, both=True)


def build():
    L, H = design()
    s_end = L + FOOT_TRIM
    z_lab = s_end                              # assembled (head pulled PULL) coords, foot end z=0
    zs = lambda s: z_lab - s
    rb = lambda s: bore_d(s) / 2
    xo = PAIR_SEP / 2
    r6 = max(H["6b"][1], H["6s"][1]) / 2
    r7 = max(H["7b"][1], H["7s"][1]) / 2

    # ---- joints ----
    s_joint = H["T"][0] - H["T"][1] / 2 - HOLE_MARGIN - 1.0      # body shoulder (head/body)
    sock_cone_f = 2.5
    lo = H["6b"][0] + r6 + HOLE_MARGIN + TENON_L + SOCKET_EXTRA + sock_cone_f
    hi = H["7b"][0] - r7 - HOLE_MARGIN
    assert lo <= hi, f"no room for foot joint between holes 6/7: {lo:.1f} > {hi:.1f}"
    s_jf = 0.5 * (lo + hi)                                         # foot shoulder / body bottom
    z_joint, z_jf = zs(s_joint), zs(s_jf)

    # ---- head ----
    ro_h = HEAD_OD / 2
    r_ten_h = bore_d(s_joint) / 2 + TENON_WALL
    r_sock_h = clearance(2 * r_ten_h, TENON_FIT) / 2
    z_hb = z_joint + PULL
    z_wtop = z_lab + WIN_L
    z_top = z_wtop + WW_L
    head = _rev([(0, z_hb), (ro_h - 0.4, z_hb), (ro_h, z_hb + 0.4), (ro_h, z_top), (0, z_top)])
    rbh = BORE_HEAD / 2
    zsock = z_hb + TENON_L + SOCKET_EXTRA + PULL
    s_ch = z_lab - zsock - (r_sock_h - rbh)
    bore = _rev([(0, z_hb - 1), (r_sock_h, z_hb - 1), (r_sock_h, zsock)]
                + _bore_pts(-WIN_L - 15, s_ch, zs) + [(0, z_wtop + 15)])
    ww_lo = EDGE_Y - WW_H / 2
    ww_hi = EDGE_Y + WW_H / 2
    # block ceiling: 45 deg slope rising away from the windway floor
    block = _yz_prism([(ww_lo, z_wtop), (rbh + 2, z_wtop), (rbh + 2, z_wtop + 20),
                       (-rbh - 2, z_wtop + 20), (-rbh - 2, z_wtop + ww_lo + rbh + 2)], rbh + 2)
    head = head - (bore - block)
    # labium flat (fills the bore segment y > EDGE_Y below the edge, 45 deg underside)
    yf = rbh + 0.5
    fill = _yz_prism([(EDGE_Y, z_lab), (yf, z_lab), (yf, z_lab - LAB_FILL_L - (yf - EDGE_Y)),
                      (EDGE_Y, z_lab - LAB_FILL_L)], rbh + 0.5)
    head = head + (fill & Pos(0, 0, z_lab - 40) * Cylinder(rbh + 0.3, 41, align=ON_BED))
    # window, labium ramp, windway, beak
    window = Pos(0, (ww_lo + ro_h + 1) / 2, (z_lab + z_wtop) / 2) * Box(WW_W, ro_h + 1 - ww_lo, WIN_L)
    ty = ro_h + 1 - (EDGE_Y + EDGE_T)
    ramp = _yz_prism([(EDGE_Y + EDGE_T, z_lab + 0.5), (EDGE_Y + EDGE_T, z_lab),
                      (ro_h + 1, z_lab - ty / math.tan(math.radians(LAB_ANGLE))),
                      (ro_h + 1, z_lab + 0.5)], WW_W / 2)
    windway = Pos(0, EDGE_Y, (z_wtop + z_top + 1) / 2 - 0.05) * Box(WW_W, WW_H, z_top + 1 - z_wtop + 0.1)
    y_bk = ww_lo - 2.0
    beak = _yz_prism([(-ro_h - 1, z_top - BEAK_L), (y_bk, z_top), (y_bk, z_top + 1),
                      (-ro_h - 1, z_top + 1)], ro_h + 1)
    # 45 deg chamfer above the window (outer part of the windway roof) -> no flat ceiling
    yc = ww_hi + 0.8
    upper = _yz_prism([(yc, z_wtop - 0.01), (ro_h + 1, z_wtop - 0.01), (ro_h + 1, z_wtop + ro_h + 1 - yc)],
                      WW_W / 2)
    head = head - window - ramp - windway - beak - upper

    # ---- body ----
    ro = BODY_OD / 2
    r_ten_f = rb(s_jf) + TENON_WALL
    r_sock_f = clearance(2 * r_ten_f, TENON_FIT) / 2
    z_btop = z_joint + TENON_L
    body = _rev([(0, z_jf), (ro - 0.4, z_jf), (ro, z_jf + 0.4), (ro, z_joint),
                 (r_ten_h, z_joint), (r_ten_h, z_btop - 0.5), (r_ten_h - 0.5, z_btop), (0, z_btop)])
    zfs = z_jf + TENON_L + SOCKET_EXTRA
    s_c = s_jf - TENON_L - SOCKET_EXTRA - (r_sock_f - rb(s_jf))
    body_bore = _rev([(0, z_jf - 1), (r_sock_f, z_jf - 1), (r_sock_f, zfs)]
                     + _bore_pts(s_joint - TENON_L - 1, s_c, zs) + [(0, z_btop + 1)])
    body = body - body_bore

    # ---- foot ----
    z_ftop = z_jf + TENON_L
    foot = _rev([(0, 0), (ro - 0.4, 0), (ro, 0.4), (ro, z_jf), (r_ten_f, z_jf),
                 (r_ten_f, z_ftop - 0.5), (r_ten_f - 0.5, z_ftop), (0, z_ftop)])
    foot = foot - _rev([(0, -1)] + _bore_pts(s_jf - TENON_L - 1, s_end + 1, zs) + [(0, z_ftop + 1)])

    # ---- tone holes (teardrops, through one wall only) ----
    def hole(hid, side=1):
        s, d, x = H[hid]
        ln = ro + 2
        return Pos(x, side * ln / 2, zs(s)) * teardrop_hole(d, ln, along="Y")

    for hid in ("T",):
        body = body - hole(hid, -1)
    for hid in ("1", "2", "3", "4", "5", "6b", "6s"):
        body = body - hole(hid)
    for hid in ("7b", "7s"):
        foot = foot - hole(hid)

    # ---- lay out on the plate: each part upright on z=0 ----
    head = Pos(-GAP, 0, -z_hb) * head
    body = Pos(0, 0, -z_jf) * body
    foot = Pos(GAP, 0, 0) * foot
    return [head, body, foot]


if __name__ == "__main__":
    L, H, rows = tuning_table()
    print(f"labium->foot L = {L:.1f} mm (+{FOOT_TRIM} trim); window M: {window_inertance()[1:]}")
    for k, v in sorted(H.items(), key=lambda kv: kv[1][0]):
        print(f"hole {k:3s} s={v[0]:6.1f} d={v[1]:.2f} x={v[2]:+.1f} t={wall_t(v[0], v[2]):.2f}")
    for n, ft, f0, c, ftr in rows:
        print(f"{n:4s} target {ft:7.2f}  model {f0:7.2f} ({c:+5.1f} c)  as printed(+trim) {ftr:7.2f}")
