"""tin-whistle-d: playable D5 tin whistle (6 holes, D major, 2 octaves), 2 parts with tuning slide.

Spec
- Key D5 (587.33 Hz, A4 = 440, equal temperament). Six finger holes on top, D major scale
  D5 E F# G A B C#6; second octave (D6..B6) by overblowing (cylindrical open pipe -> all harmonics).
- Cylindrical bore BORE = 13 mm, wall 2.5 mm (OD 18). Fipple: windway WINDWAY_H x WINDWAY_W =
  1.2 x 8 mm, 25 mm long; window 8 x 4.5 mm; labium edge 0.5 mm thick, 18 deg wedge.
- Head (mouthpiece + window + socket) and body (tube + finger holes). Body top end is the spigot:
  it slides SLIDE_MIN..SLIDE_MIN+SLIDE_TRAVEL (15..25 mm) into the head socket = 10 mm tuning slide
  (about +-30 cents around the nominal 20 mm insertion). Socket ID = clearance(18, "snug").
- Both parts print upright (axis vertical, mouthpiece up): windway and window are formed by vertical
  walls, no support anywhere near the airway; window roof and block underside are 45 deg ramps.

Acoustics (all computed in this file from the UPPER_CASE targets, c = 343 m/s at 20 C)
- Bore model: lossless plane-wave transmission line (Benade / Nederveen tone-hole lattice):
    pipe segment  X' = (X + Zc tan kL) / (Zc - X tan kL)
    open hole     shunt inertance, X_h = Zc (S/S_h) k t_e,  t_e = t_wall + 1.5 r_h   (Benade)
    closed hole   shunt compliance of the hole volume S_h t_wall
    open foot     end correction 0.61 r (unflanged, Levine-Schwinger)
    mouth         end correction d_m = (S/S_w)(t_w + 0.8 d_w), window area S_w, d_w = equivalent diam.
  A note sounds where the reactance at the virtual mouth end crosses zero (half-wave resonance).
  Labium-to-foot length and each hole position are found by bisection so each fingering hits its
  target exactly (closed-hole volumes included, solved iteratively).

TUNING (labium -> point, nominal slide insertion 20 mm; values regenerate on every build, see
TUNING_TABLE printed by `python model.py`)
  note | target Hz | computed
  D5   |  587.33   | labium -> foot 257.7 mm (body 232.7 mm, head 74.5 mm)
  E5   |  659.26   | hole 6 (lowest) 211.4 mm from labium, d 6.5
  F#5  |  739.99   | hole 5 187.7 mm, d 8.0
  G5   |  783.99   | hole 4 170.2 mm, d 4.5
  A5   |  880.00   | hole 3 151.4 mm, d 7.5
  B5   |  987.77   | hole 2 131.0 mm, d 7.5
  C#6  | 1108.73   | hole 1 (top) 110.4 mm, d 6.5
  D6.. | 2x above  | overblow (D6 often with hole 1 open: o x x x x x)
  Tone holes print as 45 deg teardrops (tip up) with the same area as the listed circle.
  Mouth end correction 27.3 mm, foot correction 4.0 mm, half-wave c/2f = 292.0 mm.

Fine-tune after printing
1. Play D5 (all closed) against a tuner; slide the body in (sharpen) / out (flatten). Mark it.
2. Then each note bottom-up: a sharp note -> partly cover its hole edge with tape / a bead of wax on
   the lower edge; a flat note -> enlarge that hole with a 0.5 mm step drill / round file on the
   upper (labium-side) edge. Re-check D after every change. 0.5 mm of diameter ~ 10-15 cents.
3. Weak low D / squeaky: clear the windway with a card; deburr the labium edge with a blade (keep
   it straight, ~0.5 mm); the jet must hit the edge centre (edge on the windway centre line).

Hardware: none required. Optional: PTFE plumber's tape (1 wrap) on the spigot if the slide is loose,
or silicone grease if it is tight.

Assembly: deburr hole edges and the spigot end; push the body (end without holes nearest top) into
the head socket to ~20 mm (the socket is 25 mm deep); tune as above.

Assumptions: A4 = 440 Hz, 20 C; AzureFilm ABS+ shrink ~0.5 % is absorbed by the tuning slide;
in-use orientation is modelled vertical (mouthpiece up, holes facing +Y); both parts are laid
side by side upright on one plate. ABS is not food-safe — personal use, rinse after playing.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",               # windway + labium need 0.12 mm layers
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # upright: windway walls vertical, no support in the airway
    supports="off",               # all ceilings are 45 deg ramps; bore/windway must stay clean
    brim="on",                    # tall slim tubes (body 233 mm x 18 mm) need bed grip.
    # WARN accepted: "wobbly on bed (6 deg)" is the 233 mm body tube standing on its 18 mm end; it
    # must print upright for a round, seam-free bore; brim on keeps it down. 2 bodies = head + body.
)

# --- Musical targets -----------------------------------------------------------------------
C_SOUND = 343.0e3                 # mm/s at 20 C
A4 = 440.0
NOTES = ["D5", "E5", "F#5", "G5", "A5", "B5", "C#6"]
SEMITONES = [5, 7, 9, 10, 12, 14, 16]   # from A4
HOLE_D = [6.5, 8.0, 4.5, 7.5, 7.5, 6.5]  # tone-hole diameters, hole 6 (lowest) .. hole 1 (top)

# --- Bore / fipple ---------------------------------------------------------------------------
BORE = 13.0
WALL = 2.5
OD = BORE + 2 * WALL
WINDWAY_H = 1.2
WINDWAY_W = 8.0
WINDWAY_L = 25.0
WINDOW_L = 4.5
WINDOW_T_EFF = 2.0                # effective window depth for the mouth correction
LABIUM_T = 0.5                    # edge thickness
LABIUM_ANGLE = 18.0               # deg, wedge ramp from axis
FLAT_L = 10.0                     # flat inner wall below the labium (straight edge)

# --- Tuning slide joint --------------------------------------------------------------------
SOCKET_D = clearance(OD, "snug")
SOCKET_DEPTH = 25.0
SLIDE_TRAVEL = 10.0
SLIDE_MIN = SOCKET_DEPTH - SLIDE_TRAVEL
SLIDE_NOMINAL = SLIDE_MIN + SLIDE_TRAVEL / 2   # insertion the holes are computed for
HEAD_OD = SOCKET_D + 2 * WALL
Z_LAB = 45.0                      # labium edge height in head coordinates
PLATE_GAP = 10.0

R = BORE / 2
S = math.pi * R**2
Y_E = R - 1.5                     # jet / edge line (flat chord inside the round bore)


def freq(note_idx):
    return A4 * 2 ** (SEMITONES[note_idx] / 12)


def mouth_corr():
    sw = WINDOW_L * WINDWAY_W
    dw = 2 * math.sqrt(sw / math.pi)
    return (S / sw) * (WINDOW_T_EFF + 0.8 * dw)


def _x_mouth(f, length, holes, n_open):
    """Normalized reactance at the virtual mouth end. holes = [(pos_from_labium, d)], lowest first;
    the n_open lowest holes are open."""
    k = 2 * math.pi * f / C_SOUND
    x = math.tan(k * 0.61 * R)            # open foot
    pos = length
    for i, (hp, hd) in enumerate(holes):
        if hp >= pos:
            continue
        L = pos - hp
        t = math.tan(k * L)
        x = (x + t) / (1 - x * t) if abs(1 - x * t) > 1e-12 else 1e12
        sh = math.pi * (hd / 2) ** 2
        if i < n_open:
            xh = (S / sh) * k * (WALL + 0.75 * hd)
            x = 1 / (1 / x + 1 / xh) if x != 0 else 0.0
        else:
            y = k * sh * WALL / S
            inv = (1 / x if x != 0 else 1e12) - y
            x = 1 / inv if inv != 0 else 1e12
        pos = hp
    L = pos + mouth_corr()
    t = math.tan(k * L)
    return (x + t) / (1 - x * t) if abs(1 - x * t) > 1e-12 else 1e12


def resonance(length, holes, n_open, f_lo=250.0, f_hi=1600.0):
    """Lowest f where reactance crosses 0 from - to + (half-wave resonance)."""
    n = 2000
    prev = _x_mouth(f_lo, length, holes, n_open)
    for i in range(1, n + 1):
        f = f_lo + (f_hi - f_lo) * i / n
        cur = _x_mouth(f, length, holes, n_open)
        if prev < 0 <= cur and abs(cur) < 5 and abs(prev) < 5:
            a, b = f - (f_hi - f_lo) / n, f
            for _ in range(50):
                m = (a + b) / 2
                if _x_mouth(m, length, holes, n_open) < 0:
                    a = m
                else:
                    b = m
            return (a + b) / 2
        prev = cur
    raise ValueError("no resonance")


def solve():
    """Bisect labium->foot length and hole positions (from labium), iterated for closed holes."""
    holes = [(-1.0, d) for d in HOLE_D]   # -1 = not placed yet (ignored)
    length = C_SOUND / (2 * freq(0))
    for _ in range(4):
        lo, hi = 150.0, 330.0
        for _ in range(50):
            m = (lo + hi) / 2
            if resonance(m, holes, 0) > freq(0):
                lo = m
            else:
                hi = m
        length = (lo + hi) / 2
        for i in range(len(HOLE_D)):
            lo = 30.0
            hi = holes[i - 1][0] - 3 if i > 0 else length - 3
            for _ in range(50):
                m = (lo + hi) / 2
                trial = list(holes)
                trial[i] = (m, HOLE_D[i])
                if resonance(length, trial, i + 1) > freq(i + 1):
                    lo = m
                else:
                    hi = m
            holes[i] = ((lo + hi) / 2, HOLE_D[i])
    return length, holes


LENGTH, HOLES = solve()
BODY_L = LENGTH - (Z_LAB - SLIDE_NOMINAL)


def tuning_table():
    rows = [f"D5 | {freq(0):.2f} | labium->foot {LENGTH:.1f} mm (body {BODY_L:.1f})"]
    for i, (p, d) in enumerate(HOLES):
        rows.append(f"{NOTES[i + 1]} | {freq(i + 1):.2f} | hole {6 - i} at {p:.1f} mm, d {d}")
    rows.append(f"mouth corr {mouth_corr():.1f} mm, foot corr {0.61 * R:.1f}, c/2f {C_SOUND / 2 / freq(0):.1f}")
    return "\n".join(rows)


def _yz_prism(pts, half_w):
    return extrude(Plane.YZ * Polygon(*pts, align=None), half_w, both=True)


def build_head():
    z_top = Z_LAB + WINDOW_L
    top = z_top + WINDWAY_L
    ro, rh = OD / 2, HEAD_OD / 2
    zs = SOCKET_DEPTH + 3.0
    outer = revolve(Plane.XZ * Polygon((0, 0), (rh - 0.4, 0), (rh, 0.4), (rh, zs),
                                       (ro, zs + rh - ro), (ro, top), (0, top), align=None), Axis.Z, 360)
    rs = SOCKET_D / 2
    bore = revolve(Plane.XZ * Polygon((0, -1), (rs, -1), (rs, SOCKET_DEPTH), (R, SOCKET_DEPTH + rs - R),
                                      (R, z_top), (0, z_top), align=None), Axis.Z, 360)
    # flat chord below/at the window (straight labium edge), tapered 45 deg at its bottom
    y_f = Y_E - LABIUM_T / 2
    zf = Z_LAB - FLAT_L
    fill = _yz_prism([(y_f, z_top + 1), (R + 1, z_top + 1), (R + 1, zf - (R + 1 - y_f)), (y_f, zf)], R + 1)
    # block underside as a 45 deg ramp (no flat ceiling over the bore)
    y_w = Y_E - WINDWAY_H / 2
    slant = _yz_prism([(y_w, z_top), (-R - 1, z_top - (y_w + R + 1)), (-R - 1, z_top + 1), (y_w, z_top + 1)], R + 1)
    bore = bore - fill - slant
    part = outer - bore
    # windway + window + labium ramp + 45 deg window roof as ONE prism (no coplanar faces)
    hw = WINDWAY_W / 2
    y_l = Y_E + LABIUM_T / 2
    y_r = Y_E + WINDWAY_H / 2
    run = (rh + 1 - y_l) / math.tan(math.radians(LABIUM_ANGLE))
    airway = _yz_prism([(y_w, top + 1), (y_w, Z_LAB), (y_l, Z_LAB), (rh + 1, Z_LAB - run),
                        (rh + 1, z_top + rh + 1 - y_r), (y_r, z_top), (y_r, top + 1)], hw)
    y_b = y_w - 1.6
    beak = _yz_prism([(y_b, top + 1), (y_b, top), (-rh - 1, top - 1.5 * (y_b + rh + 1)), (-rh - 1, top + 1)], rh + 1)
    return part - airway - beak


def build_body():
    ro = OD / 2
    tube = revolve(Plane.XZ * Polygon((R, 0), (ro - 0.4, 0), (ro, 0.4), (ro, BODY_L), (R, BODY_L),
                                      align=None), Axis.Z, 360)
    z_lab = BODY_L + (Z_LAB - SLIDE_NOMINAL)   # labium height when assembled at nominal slide
    for p, d in HOLES:
        # teardrop (45 deg tip up) so the hole roof prints without support; printed diameter is
        # reduced so the teardrop area equals the acoustic circle area (+0.215 r^2 tip)
        dp = d / math.sqrt(1 + (1 - math.pi / 4) / math.pi)
        tube -= Pos(0, R + WALL / 2 + 1, z_lab - p) * teardrop_hole(dp, WALL + 5, along="Y")
    return tube


def build():
    head = Pos(-(HEAD_OD / 2 + PLATE_GAP / 2), 0, 0) * build_head()
    body = Pos(OD / 2 + PLATE_GAP / 2, 0, 0) * build_body()
    return [head, body]


if __name__ == "__main__":
    print(tuning_table())
