"""lyre-10: 10-string lyre harp, C major C4-E5, ~40 kg total string tension.

Spec
- Diatonic C4 D4 E4 F4 G4 A4 B4 C5 D5 E5, parallel strings at 15 mm pitch, nylon monofilament.
- Hollow soundbox 270 x 200 x 70 mm (shell + 4 mm soundboard), two bolted arms, slanted yoke
  with 10 zither-pin holes, integral tail block with string anchor holes, floating bridge.
- Vibrating length (floating bridge saddle -> yoke nut ridge) runs linearly 370 mm (C4) ->
  270 mm (E5); per-string target tension tapers 44 N (bass) -> 34.5 N (treble).
- Overall ~270 wide x 502 tall x 84 deep (tail block); arms 302 (bass) / 135 (treble) long.
- Soundbox is a Helmholtz resonator tuned to G3 (below C4): the cavity volume is measured
  from the CAD solid and the soundhole radius is solved from f = c/2pi*sqrt(A/(V*L_eff)),
  L_eff = t + 1.7 r (flanged both sides).
- Strength: string load runs along X/Y layers (print_orientation rx=90 lays every part flat,
  so the string axis Z(in use) lies in the print plane). Arms sit on solid corner posts in
  compression; bolts only locate. Yoke bending ~11 N*m -> ~2 MPa in a 26 x 46 section.

Parts / plates - the lyre cannot fit one 300x320 plate, so PLATE selects what build() returns
(the checker slices a single plate; out/lyre-10-plate<N>.3mf holds each slice, PLATE=0 = all):
  plate 1: shell with stubs, corner posts and tail block (270 x 270)
  plate 2: soundboard (exported flipped: outer face on the bed, lip/braces up) + bridge +
           treble (right) arm laid along X
  plate 3: yoke + bass (left) arm (292 x 302)
  Slice (Guitar Core ABS+): plate1 16h46m 502 g, plate2 6h44m 191 g, plate3 9h00m 240 g
  -> 32h30m, 933 g total. All parts print flat with rx=90. Several bodies per plate is intended (mesh WARN).
  supports=off: the only flagged areas are <=9 mm bridges over the bed-face nut traps and
  dowel holes, which bridge cleanly (support WARN accepted).

TUNING (rho_nylon 1140 kg/m^3, T = (2 L f)^2 * rho * pi d^2 / 4)
  note | target Hz | vib. length mm | nylon gauge mm | tension N (kgf)
  C4   | 261.63    | 370.0          | 1.15           | 44.4 (4.52)
  D4   | 293.66    | 358.9          | 1.05           | 43.9 (4.47)
  E4   | 329.63    | 347.8          | 0.95           | 42.5 (4.33)
  F4   | 349.23    | 336.7          | 0.90           | 40.1 (4.09)
  G4   | 392.00    | 325.6          | 0.85           | 42.1 (4.30)
  A4   | 440.00    | 314.4          | 0.75           | 38.6 (3.93)
  B4   | 493.88    | 303.3          | 0.70           | 39.4 (4.01)
  C5   | 523.25    | 292.2          | 0.65           | 35.4 (3.61)
  D5   | 587.33    | 281.1          | 0.60           | 35.1 (3.58)
  E5   | 659.26    | 270.0          | 0.55           | 34.3 (3.50)
  total 396 N = 40.3 kgf (gauges rounded to 0.05 mm; run `python model.py` to reprint).
  Soundbox Helmholtz | G3 196.0 Hz | cavity V = 2.857 L (measured from CAD), board t = 4 mm,
  L_eff = t + 1.7 r -> soundhole Ø 44.1 mm (solved by bisection in helmholtz_radius()).

Fine-tune after printing
- Strings: tune with the wrench to a tuner; nylon stretches for ~3 days, retune often.
- Intonation: the bridge floats - slide it along Z (toward tail = longer = lower) so all
  strings sit within a few Hz of target at equal pin turns; mark and optionally glue it.
- Body resonance: tap the box near the hole / sweep with a tone app. Too high -> narrow the
  hole with a tape ring (smaller A lowers f); too low -> ream wider (f ~ r^0.5..1).
- Buzz: file a shallow V notch (0.5 mm) for each string in the bridge saddle and nut ridge.

Hardware to buy
- 10 x zither (harp) pins Ø5 x 47-50 mm (standard 7 mm-pitch "zither pin"), + T-wrench.
- 10 nylon monofilament / lyre strings: gauges per table (or a 10-string C4-E5 lyre set),
  plus 10 small beads (4 mm) or knots as tail anchors.
- 4 x M5 x 45 socket head (arm -> stub), 4 x M5 x 45 socket head (yoke -> arm), 8 x M5 nuts.
- 4 x Ø5 x 20 mm steel dowel pins (alignment, one per joint).
- ABS cement (ABS dissolved in acetone) or 2-part epoxy for soundboard-to-shell seam.

Assembly
1. Glue the soundboard onto the shell rim (lip inside the walls), clamp 12 h.
2. Press dowel pins into the stubs, fit arms, insert M5 nuts into the back-face hex traps,
   bolt M5 x 45 from the arm front. Arms bear on the box top (compression).
3. Pin + bolt the yoke feet onto the arm fronts the same way (nuts in arm back traps).
4. Screw zither pins into the yoke from the front (threaded pin cuts its own thread in the
   4.7 mm pilot), leaving ~12 mm out. Do not drill through again - ABS needs the grip.
5. Thread each string up through its tail hole (bead/knot in the bottom counterbore), over the
   bridge saddle and nut ridge, into the pin's eye, wind 3 turns; tune gradually, all strings
   a little at a time, so the frame loads evenly.

Assumptions
- c = 343 m/s (20 °C). Zither pin Ø5 mm -> printed pilot 4.7 mm finished (ABS grips harder
  than hardwood's 4.8 mm drill). Strings tie to beads; no fine tuners.
- Total string tension target 40 kgf; rounding gauges gives ~41 kgf (within 5 %).
- Not free-standing (played on the lap / held), so no tip-over audit; META loads put the
  full string tension on the yoke for the record.
"""

import math

from build123d import *

from cadlib import *

# ---------------------------------------------------------------- physics constants
C_AIR = 343.0            # m/s at 20 °C
RHO_NYLON = 1140.0       # kg/m^3
G = 9.81
NOTES = [("C4", 261.63), ("D4", 293.66), ("E4", 329.63), ("F4", 349.23), ("G4", 392.00),
         ("A4", 440.00), ("B4", 493.88), ("C5", 523.25), ("D5", 587.33), ("E5", 659.26)]
L_BASS = 370.0           # vibrating length of C4 [mm]
L_TREBLE = 270.0         # vibrating length of E5 [mm]
T_BASS = 44.0            # target tension C4 [N]
T_TREBLE = 34.5          # target tension E5 [N]
GAUGE_STEP = 0.05        # available nylon gauge step [mm]
HELMHOLTZ_F = 196.0      # soundbox target, G3 [Hz]
END_CORR = 1.7           # L_eff = t + END_CORR * r

# ---------------------------------------------------------------- geometry
STRING_PITCH = 15.0
BOX_W = 270.0            # X
BOX_H = 200.0            # Z
SHELL_D = 66.0           # Y depth of the shell (back at Y=0)
WALL = 3.0
BOARD_T = 4.0            # soundboard thickness (Helmholtz neck length)
Y_BOARD = SHELL_D + BOARD_T          # soundboard outer face
BRIDGE_H = 12.0          # string height over the board at the bridge
Y_STRING = Y_BOARD + BRIDGE_H        # string plane at the bridge
Z_BRIDGE = 52.0          # bridge saddle height
TAIL_H = 28.0            # tail block height (Z)
TAIL_HALF = 85.0         # tail block half width (X)
TAIL_FRONT = 84.0        # tail block front face (Y)
TAIL_HOLE_Y = 76.0       # string exit Y at the tail
TAIL_HOLE_D = 2.0
KNOT_D, KNOT_DEPTH = 6.0, 6.0

ARM_X = 112.0            # arm centre line |X|
ARM_W = 30.0             # arm width (X)
Y_STUB = (0.0, 23.0)     # stub (shell)  Y range
Y_ARM = (23.0, 49.0)     # arms Y range
Y_YOKE = (49.0, 75.0)    # yoke Y range
STUB_TOP = BOX_H + 70.0
POST_BOT = BOX_H - 50.0  # solid corner post inside the box under each arm
RIDGE_H = 5.0            # nut ridge proud of the yoke front -> string at Y=80
RIDGE_W = 4.0
YOKE_BELOW = 6.0         # yoke material below the contact line
YOKE_ABOVE = 36.0        # yoke material above the contact line
PIN_ABOVE = 14.0         # zither pin centre above the contact line
ZITHER_PILOT = 4.7       # finished pilot hole for Ø5 zither pins
FOOT_DROP = 45.0         # yoke foot extends this far below the yoke at each arm
GUSSET = 25.0
FOOT_MIN = 60.0         # minimum yoke-foot height on each arm

PLATE = 1                # which print plate build() returns: 1, 2, 3 (0 = all, review only)
GAP = 8.0                # spacing between parts on a plate

BOLT = "M5"
HEAD_CB_D, HEAD_CB_DEPTH = 9.5, 7.5
PIN_D, PIN_DEPTH = 5.0, 11.0          # Ø5 x 20 dowel, 10 mm each side (+1 clearance)

BRIDGE_LEN = 160.0
BRIDGE_BASE, BRIDGE_TOP = 14.0, 3.0

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="Guitar Core ABS+ 0.20mm @BBL H2C",
    standing=False,  # held on the lap; not free-standing
    loads=[dict(at=(0.0, 77.0, 420.0), grams=41000)],  # total string tension on the yoke
    print_orientation=(90, 0, 0),  # every part flat: string axis (Z in use) along layers
    supports="off",  # only flagged areas are <=9 mm bridges over nut traps / dowel holes on the bed face
    brim="on",  # large flat ABS parts: brim against warping
)


# ---------------------------------------------------------------- physics
def string_x(i):
    return -(len(NOTES) - 1) / 2 * STRING_PITCH + i * STRING_PITCH


def string_table():
    """[(note, f, L_mm, d_mm, T_N)] with gauges rounded to GAUGE_STEP."""
    rows = []
    n = len(NOTES)
    for i, (name, f) in enumerate(NOTES):
        u = i / (n - 1)
        L = L_BASS + (L_TREBLE - L_BASS) * u
        t_target = T_BASS + (T_TREBLE - T_BASS) * u
        v2 = (2 * L / 1000 * f) ** 2
        d_ideal = math.sqrt(4 * t_target / (math.pi * RHO_NYLON * v2)) * 1000
        d = round(d_ideal / GAUGE_STEP) * GAUGE_STEP
        T = v2 * RHO_NYLON * math.pi * (d / 1000) ** 2 / 4
        rows.append((name, f, L, d, T))
    return rows


def contact_z(x):
    """Z of the nut-ridge contact line (linear in x through bass and treble strings)."""
    x0, x1 = string_x(0), string_x(len(NOTES) - 1)
    return Z_BRIDGE + L_BASS + (L_TREBLE - L_BASS) * (x - x0) / (x1 - x0)


def helmholtz_radius(volume_mm3):
    """Soundhole radius [mm] for HELMHOLTZ_F with neck = BOARD_T (bisection)."""
    V, t = volume_mm3 * 1e-9, BOARD_T / 1000
    k2 = (2 * math.pi * HELMHOLTZ_F / C_AIR) ** 2
    lo, hi = 0.002, 0.08
    for _ in range(60):
        r = (lo + hi) / 2
        if math.pi * r * r / (t + END_CORR * r) < k2 * V:
            lo = r
        else:
            hi = r
    return r * 1000


def helmholtz_f(volume_mm3, r_mm):
    V, r, t = volume_mm3 * 1e-9, r_mm / 1000, BOARD_T / 1000
    return C_AIR / (2 * math.pi) * math.sqrt(math.pi * r * r / (V * (t + END_CORR * r)))


# ---------------------------------------------------------------- helpers
def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def cut_minus_y(x, y_face, z, cutter):
    """Place a cadlib cutter (points -Z from z=0) on a +Y facing face, cutting toward -Y."""
    return Pos(x, y_face, z) * Rot(-90, 0, 0) * cutter


def cut_plus_y(x, y_face, z, cutter):
    """Cutter on a -Y facing face (back), cutting toward +Y."""
    return Pos(x, y_face, z) * Rot(90, 0, 0) * cutter


def through_y(x, z, d, y0, y1):
    return Pos(x, (y0 + y1) / 2, z) * Rot(90, 0, 0) * Cylinder(d / 2, y1 - y0 + 2)


def joint_cutters(x, zs, y_front, y_back, pin_z):
    """Bolt (head counterbore at y_front) + hex nut trap at y_back + dowel holes at the face."""
    cuts = []
    m = METRIC[BOLT]
    for z in zs:
        cuts.append(through_y(x, z, clearance(5.0, "loose"), y_back - 1, y_front + 1))
        cuts.append(cut_minus_y(x, y_front, z, Cylinder(HEAD_CB_D / 2, HEAD_CB_DEPTH,
                                                        align=(Align.CENTER, Align.CENTER, Align.MAX))))
        cuts.append(cut_plus_y(x, y_back, z, nut_trap(BOLT, depth=4.5)))
    return cuts


# ---------------------------------------------------------------- parts
def shell():
    x_in = BOX_W / 2 - WALL
    body = box(-BOX_W / 2, BOX_W / 2, 0, SHELL_D, 0, BOX_H)
    body -= box(-x_in, x_in, WALL, SHELL_D + 1, WALL, BOX_H - WALL)
    # corner posts (arms bear on these) + stubs above the box
    for s in (-1, 1):
        x0, x1 = s * ARM_X - ARM_W / 2, s * ARM_X + ARM_W / 2
        body += box(x0, x1, 0, SHELL_D - 6, POST_BOT, BOX_H)
        body += box(x0, x1, Y_STUB[0], Y_STUB[1], BOX_H - 1, STUB_TOP)
    # tail block, 45° underside toward the back (prints without support)
    prof = Polygon((12, 0), (TAIL_FRONT, 0), (TAIL_FRONT, TAIL_H), (40, TAIL_H), align=None)
    tail = extrude(Plane.YZ.offset(-TAIL_HALF) * prof, 2 * TAIL_HALF)
    body += tail
    # tail ribs tying the anchor block to the back wall
    for i in range(-2, 3):
        rib_p = Polygon((WALL - 1, TAIL_H - 1), (42, TAIL_H - 1), (WALL - 1, TAIL_H + 45), align=None)
        body += extrude(Plane.YZ.offset(i * 40 - 2) * rib_p, 4)
    # back stiffening ribs (inside, along Z)
    for x in (-60, 60):
        body += box(x - 2, x + 2, WALL - 1, WALL + 8, TAIL_H, BOX_H - WALL + 1)
    # string anchor holes (vertical in use = horizontal in print -> teardrop, tip toward +Y)
    for i in range(len(NOTES)):
        x = string_x(i)
        body -= Pos(x, TAIL_HOLE_Y, TAIL_H / 2) * Rot(-90, 0, 0) * teardrop_hole(
            TAIL_HOLE_D + 0.4, TAIL_H + 4, along="Y")
        body -= Pos(x, TAIL_HOLE_Y, 0) * Rot(-90, 0, 0) * teardrop_hole(
            KNOT_D, 2 * KNOT_DEPTH, along="Y")
    # arm joints: bolts from the arm front, nut traps in the stub back (bed face)
    for s in (-1, 1):
        for c in joint_cutters(s * ARM_X, (BOX_H + 18, BOX_H + 52), Y_ARM[1], Y_STUB[0], None):
            body -= c
        body -= through_y(s * ARM_X, BOX_H + 35, PIN_D + 0.1, Y_STUB[1] - PIN_DEPTH, Y_STUB[1] + 1)
    # elephant-foot chamfer on the print bed face (back, Y=0)
    try:
        body = chamfer(body.edges().group_by(Axis.Y)[0], 0.4)
    except Exception:
        pass
    return body


def soundboard_parts():
    """Soundboard (in-use pose) and its internal lip/braces, plus the cavity volume."""
    x_in = BOX_W / 2 - WALL
    board = box(-BOX_W / 2, BOX_W / 2, SHELL_D, Y_BOARD, 0, BOX_H)
    board -= box(-TAIL_HALF - 0.3, TAIL_HALF + 0.3, SHELL_D - 1, Y_BOARD + 1, -1, TAIL_H + 0.3)
    # posts reach Y = SHELL_D-6: lip/braces stay clear of them
    c = 0.3
    lip_y = (SHELL_D - 4, SHELL_D)
    inner = []
    inner.append(box(-x_in + c, -x_in + c + 2, *lip_y, WALL + c, POST_BOT - 2))
    inner.append(box(x_in - c - 2, x_in - c, *lip_y, WALL + c, POST_BOT - 2))
    inner.append(box(-ARM_X + ARM_W / 2 + 2, ARM_X - ARM_W / 2 - 2, *lip_y,
                     BOX_H - WALL - c - 2, BOX_H - WALL - c))
    # braces: one under the bridge, one near the top (clear of the soundhole)
    inner.append(box(-x_in + 3, x_in - 3, SHELL_D - 6, SHELL_D, Z_BRIDGE - 2.5, Z_BRIDGE + 2.5))
    inner.append(box(-ARM_X + ARM_W / 2 + 4, ARM_X - ARM_W / 2 - 4, SHELL_D - 6, SHELL_D,
                     BOX_H - 30, BOX_H - 25))
    for p in inner:
        board += p
    return board


def cavity_volume(sh, board):
    x_in = BOX_W / 2 - WALL
    cav = box(-x_in, x_in, WALL, SHELL_D, WALL, BOX_H - WALL) - sh - board
    return cav.volume


def bridge():
    prof = Polygon((Z_BRIDGE - BRIDGE_BASE / 2, Y_BOARD), (Z_BRIDGE + BRIDGE_BASE / 2, Y_BOARD),
                   (Z_BRIDGE + BRIDGE_TOP / 2, Y_STRING), (Z_BRIDGE - BRIDGE_TOP / 2, Y_STRING),
                   align=None)
    # Plane.YZ: local x = +Y, local y = +Z -> swap to (y, z)
    prof = Polygon(*[(p[1], p[0]) for p in [(Z_BRIDGE - BRIDGE_BASE / 2, Y_BOARD),
                                             (Z_BRIDGE + BRIDGE_BASE / 2, Y_BOARD),
                                             (Z_BRIDGE + BRIDGE_TOP / 2, Y_STRING),
                                             (Z_BRIDGE - BRIDGE_TOP / 2, Y_STRING)]], align=None)
    return extrude(Plane.YZ.offset(-BRIDGE_LEN / 2) * prof, BRIDGE_LEN)


def yoke_outline_z(x):
    return contact_z(x) - YOKE_BELOW, contact_z(x) + YOKE_ABOVE


def yoke():
    xl, xr = -ARM_X - ARM_W / 2, ARM_X + ARM_W / 2
    lo_l, hi_l = yoke_outline_z(xl)
    lo_r, hi_r = yoke_outline_z(xr)
    # bar + feet (feet drop along the arm fronts), profile in XZ
    xa, xb = -ARM_X + ARM_W / 2, ARM_X - ARM_W / 2
    lower = lambda x: yoke_outline_z(x)[0]
    upper = lambda x: yoke_outline_z(x)[1]
    foot_l = max(min(lower(xa), lo_l) - FOOT_DROP, STUB_TOP + 5)
    foot_r = max(min(lower(xb), lo_r) - FOOT_DROP, STUB_TOP + 5)
    top_l = max(hi_l, foot_l + FOOT_MIN)
    top_r = max(hi_r, foot_r + FOOT_MIN)
    pts = [(xl, foot_l), (xa, foot_l), (xa, max(lower(xa) - GUSSET, foot_l)),
           (xa + GUSSET, lower(xa + GUSSET)), (xb - GUSSET, lower(xb - GUSSET)),
           (xb, max(lower(xb) - GUSSET, foot_r)), (xb, foot_r), (xr, foot_r),
           (xr, top_r), (xb, top_r), (xb, upper(xb)), (xa, upper(xa)), (xa, top_l), (xl, top_l)]
    clean = []
    for q in pts:
        if not clean or math.dist(q, clean[-1]) > 1e-3:
            clean.append(q)
    pts = [q for i, q in enumerate(clean)
           if not (0 < i < len(clean) - 1 and abs((clean[i - 1][0] - q[0]) * (clean[i + 1][1] - q[1])
                                                   - (clean[i - 1][1] - q[1]) * (clean[i + 1][0] - q[0])) < 1e-6)]
    hi_l, hi_r = top_l, top_r
    # Plane.XZ: local x = X, local y = Z, normal -Y -> extrude toward -Y from y=Y_YOKE[1]
    yk = extrude(Plane.XZ.offset(-Y_YOKE[1]) * Polygon(*pts, align=None), Y_YOKE[1] - Y_YOKE[0])
    # nut ridge on the front face along the contact line
    x0, x1 = string_x(0) - 10, string_x(len(NOTES) - 1) + 10
    ang = math.degrees(math.atan2(contact_z(x1) - contact_z(x0), x1 - x0))
    length = math.hypot(x1 - x0, contact_z(x1) - contact_z(x0))
    xm = (x0 + x1) / 2
    ridge = Pos(xm, Y_YOKE[1] + RIDGE_H / 2 - 0.5, contact_z(xm)) * Rot(0, -ang, 0) * Box(
        length, RIDGE_H + 1, RIDGE_W)
    yk += ridge
    # zither pin pilots (through, along Y = vertical in print)
    for i in range(len(NOTES)):
        x = string_x(i)
        yk -= through_y(x, contact_z(x) + PIN_ABOVE, hole_d(ZITHER_PILOT), Y_YOKE[0], Y_YOKE[1] + RIDGE_H)
    # joints to the arms
    for s, top in ((-1, foot_l), (1, foot_r)):
        z1, z2 = top + 12, top + 12 + 28
        for c in joint_cutters(s * ARM_X, (z1, z2), Y_YOKE[1], Y_ARM[0], None):
            yk -= c
        yk -= through_y(s * ARM_X, (z1 + z2) / 2, PIN_D + 0.1, Y_YOKE[0] - 1, Y_YOKE[0] + PIN_DEPTH)
    return yk, foot_l, foot_r, hi_l, hi_r


def arm(side, foot_z, top_z):
    x0, x1 = side * ARM_X - ARM_W / 2, side * ARM_X + ARM_W / 2
    a = box(x0, x1, *Y_ARM, BOX_H, top_z)
    x = side * ARM_X
    # lower joint: head counterbores on arm front; dowel into stub (arm side of the pin)
    for z in (BOX_H + 18, BOX_H + 52):
        a -= through_y(x, z, clearance(5.0, "loose"), Y_ARM[0] - 1, Y_ARM[1] + 1)
        a -= cut_minus_y(x, Y_ARM[1], z, Cylinder(HEAD_CB_D / 2, HEAD_CB_DEPTH,
                                                  align=(Align.CENTER, Align.CENTER, Align.MAX)))
    a -= through_y(x, BOX_H + 35, PIN_D + 0.1, Y_ARM[0] - 1, Y_ARM[0] + PIN_DEPTH)
    # upper joint: nut traps in the arm back, dowel hole in the arm front
    z1, z2 = foot_z + 12, foot_z + 40
    for z in (z1, z2):
        a -= through_y(x, z, clearance(5.0, "loose"), Y_ARM[0] - 1, Y_ARM[1] + 1)
        a -= cut_plus_y(x, Y_ARM[0], z, nut_trap(BOLT, depth=4.5))
    a -= through_y(x, (z1 + z2) / 2, PIN_D + 0.1, Y_ARM[1] - PIN_DEPTH, Y_ARM[1] + 1)
    return a


def build():
    sh = shell()
    board = soundboard_parts()
    vol = cavity_volume(sh, board)
    r = helmholtz_radius(vol)
    board -= Pos(0, Y_BOARD, 135) * Rot(90, 0, 0) * Cylinder(r, 2 * BOARD_T + 20)
    yk, foot_l, foot_r, hi_l, hi_r = yoke()
    arm_l = arm(-1, foot_l, hi_l)
    arm_r = arm(1, foot_r, hi_r)
    br = bridge()
    # soundboard printed outer face down: rotate 180° about Z (in-use pose = un-rotate)
    board_print = Rot(0, 0, 180) * board
    # print plates (model X/Z = print X/Y after rx=90); each part dropped to Y=0 (= bed)
    arm_r_flat = Rot(0, 90, 0) * arm_r          # lay the short arm along X
    plates = {
        1: [(sh, 0, 0)],
        2: [(board_print, 0, 0), (br, 0, 200 + GAP), (arm_r_flat, 0, 200 + 14 + 2 * GAP)],
        3: [(yk, 0, 0), (arm_l, 254 + GAP, 0)],
    }
    chosen = [q for k in sorted(plates) if PLATE in (0, k) for q in plates[k]]
    out = []
    for i, (p, x, z) in enumerate(chosen):
        bb = p.bounding_box()
        dx = x - bb.min.X + (i * 400 if PLATE == 0 else 0)
        out.append(Pos(dx, -bb.min.Y, z - bb.min.Z) * p)
    return out


if __name__ == "__main__":
    tot = 0
    for name, f, L, d, T in string_table():
        tot += T
        print(f"{name} | {f:.2f} | {L:.1f} | {d:.2f} | {T:.1f} ({T / G:.2f})")
    print(f"total {tot:.0f} N = {tot / G:.1f} kgf")
    sh = shell()
    b = soundboard_parts()
    v = cavity_volume(sh, b)
    r = helmholtz_radius(v)
    print(f"V={v / 1e6:.3f} L  r={r:.1f} d={2 * r:.1f} f={helmholtz_f(v, r):.1f}")
    yk, fl, fr, hl, hr = yoke()
    print("feet", fl, fr, "tops", hl, hr, "yoke bbox", yk.bounding_box())
    print("arm L len", hl - BOX_H, "arm R len", hr - BOX_H)
