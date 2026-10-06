"""kalimba-17: playable 17-key kalimba (C major, C4-E6), hollow Helmholtz box resonator.

Spec
- Box 144 (X) x 175 (Y) x 30 (Z) mm, ABS+, 3 parts printed on one plate:
  1. TRAY  - floor + walls (3 mm), internal transverse bridge rib with diamond windows,
             two M4 bolt columns with hex nut traps in the floor.
  2. TOP   - 3 mm soundboard that drops into a 1.5 x 3 mm rebate in the tray; carries the
             front saddle, back saddle (both trapezoid ribs, Ø3 rod groove on top), the
             Helmholtz sound hole and 17 engraved tine-tip index marks.
  3. BAR   - pressure bar 141 x 10 x 8 mm, clamps the tines between the saddles with 2x M4.
- Tines run along Y, tips toward the player (-Y). Lowest note in the middle, alternating
  right/left (C4 centre, D4 right, E4 left, ...), pitch 7.2 mm for 6 mm wide tines.
- Front saddle crest (with Ø3 rod) 7.5 mm above the soundboard = start of vibrating length.

Physics (computed in code, see tine_length() / helmholtz_hz())
- Clamped-free bar: f = 0.1615 * t / L^2 * sqrt(E/rho), spring steel E=200 GPa, rho=7850,
  TINE_T = 1.0 mm  ->  L_ideal = sqrt(0.1615 * t * sqrt(E/rho) / f).
- Real kalimba tines are not ideally clamped (saddle is a rounded pivot, pressure bar is
  compliant, soundboard flexes, tip is bent/rounded), so they are longer than ideal for the
  same pitch. Empirical correction K_EMP = 1.30 (calibrated: commercial 17-key C4 tine free
  length ~72-75 mm, E6 ~32-35 mm, the ideal formula gives 55.8 / 24.9 mm). Index marks use
  L_mark = K_EMP * L_ideal; both are listed below. Typical range 35-75 mm: OK.
- Helmholtz: f = c/(2 pi) * sqrt(A / (V * L_eff)), c = 343 m/s, L_eff = t + 1.7 r
  (flanged one side + unflanged inside, mid of 1.5..1.7 r range). Hole radius solved in code
  for HELM_TARGET = 247 Hz (B3, just below C4) with the net internal air volume
  (~0.55 L) -> sound hole Ø ~15.1 mm (r = 7.55 mm).

TUNING (TINE_T = 1.0 mm, free length = front saddle crest -> tine tip)
| note | target Hz | L ideal mm | L mark (x1.30) mm | x pos mm |
| C4 | 261.63 | 55.8 | 72.6 |   0.0 |
| D4 | 293.66 | 52.7 | 68.5 |  +7.2 |
| E4 | 329.63 | 49.7 | 64.6 |  -7.2 |
| F4 | 349.23 | 48.3 | 62.8 | +14.4 |
| G4 | 392.00 | 45.6 | 59.3 | -14.4 |
| A4 | 440.00 | 43.0 | 56.0 | +21.6 |
| B4 | 493.88 | 40.6 | 52.8 | -21.6 |
| C5 | 523.25 | 39.5 | 51.3 | +28.8 |
| D5 | 587.33 | 37.3 | 48.4 | -28.8 |
| E5 | 659.26 | 35.2 | 45.7 | +36.0 |
| F5 | 698.46 | 34.2 | 44.4 | -36.0 |
| G5 | 783.99 | 32.2 | 41.9 | +43.2 |
| A5 | 880.00 | 30.4 | 39.6 | -43.2 |
| B5 | 987.77 | 28.7 | 37.3 | +50.4 |
| C6 | 1046.50 | 27.9 | 36.3 | -50.4 |
| D6 | 1174.66 | 26.3 | 34.2 | +57.6 |
| E6 | 1318.51 | 24.9 | 32.3 | -57.6 |
| body (Helmholtz) | 247 | sound hole Ø 15.1 mm, V 0.55 L | | |

Fine-tuning after printing
1. Set every tine tip on its engraved index mark, tighten both M4 nuts evenly until the
   tines do not move when plucked hard (do not crush the bar: ~1 Nm).
2. With a tuner app: flat -> tap the tine toward the bridge (shorter), sharp -> pull it out.
   Loosen the bolts ~1/4 turn for big moves. 1 mm of length changes pitch ~2-4 % (~40 cents
   at C4, ~70 cents at E6), so work in 0.2-0.5 mm steps.
3. Re-check all notes after the final torque (clamping raises pitch slightly).
4. Buzz: make sure each tine sits on both rods; a dab of PVA/rubber under the back end
   kills sympathetic buzz.

Hardware to buy
- 17 spring-steel kalimba tines, 6 mm wide, ~1.0 mm thick (C-scale replacement key set,
  overall lengths ~57-98 mm: free length + 25 mm behind the front saddle).
- 2x M4x50 socket head screws, 2x M4 hex nuts, 2x M4 washers.
- 2x Ø3 mm steel rod 128 mm (saddle crests; drill rod or a cut nail/skewer of steel).
- ABS cement / acetone (or CA glue) for the soundboard.

Assembly
1. Press the 2 nuts into the floor traps (underside of TRAY).
2. Glue TOP into the tray rebate (ABS weld), saddles toward the back (+Y), weigh down 1 h.
3. Lay the two Ø3 rods into the saddle grooves (dab of CA).
4. Lay the tines across the rods in the alternating order, put BAR on top, insert the M4x50
   screws through BAR, TOP and the columns into the nuts, tighten, then tune.

Assumptions
- Tine thickness 1.0 mm (set TINE_T for other sets; marks move accordingly).
- Box closed except for one top sound hole (no back "wah" holes) to keep the Helmholtz
  calculation exact; drill 2x Ø10 in the back if vibrato holes are wanted (raises f_H).
- Parts are laid out side by side for one 300x320 plate (in-use orientation, flat).
- standing=False: hand-held / lies flat on a table, cannot tip.
"""

import math

from build123d import *

from cadlib import *

# ---------------- parameters ----------------
# physics
C_AIR = 343.0           # m/s at 20 C
E_STEEL = 200e9         # Pa
RHO_STEEL = 7850.0      # kg/m^3
TINE_T = 1.0            # mm tine thickness
TINE_W = 6.0            # mm tine width
K_EMP = 1.30            # empirical length correction (real vs ideal clamped cantilever)
HELM_TARGET = 247.0     # Hz, Helmholtz resonance (B3, just below C4)
HELM_END_K = 1.7        # end correction factor L_eff = t + k*r
NOTES = [("C4", 261.63), ("D4", 293.66), ("E4", 329.63), ("F4", 349.23), ("G4", 392.00),
         ("A4", 440.00), ("B4", 493.88), ("C5", 523.25), ("D5", 587.33), ("E5", 659.26),
         ("F5", 698.46), ("G5", 783.99), ("A5", 880.00), ("B5", 987.77), ("C6", 1046.50),
         ("D6", 1174.66), ("E6", 1318.51)]
TINE_PITCH = 7.2        # mm centre spacing

# box
BOX_W = 144.0           # X
BOX_L = 175.0           # Y
BOX_H = 30.0            # Z total (tray incl. flush soundboard)
CORNER_R = 6.0
WALL = 3.0
FLOOR = 3.0
TOP_T = 3.0             # soundboard thickness
REBATE = 1.5            # rebate width in the wall top
FIT_GAP = 0.2           # per side, soundboard in rebate

# bridge
SADDLE_LEN = 128.0      # along X
SADDLE_H = 6.0          # printed height above soundboard (rod groove centre)
SADDLE_BASE = 10.0      # trapezoid base width (rib)
SADDLE_TOP = 5.0
ROD_D = 3.0             # steel crest rod
SADDLE_GAP = 20.0       # front saddle -> back saddle
BACK_MARGIN = 11.0      # back saddle centre -> inner back wall
BOLT_X = 66.0           # +- X of the M4 bolts
COLUMN_R = 5.0
BOLT = "M4"
BOLT_D = 4.0
BAR_L = 141.0
BAR_W = 10.0
BAR_H = 8.0

# internal rib under the bridge
RIB_T = 3.0
RIB_WIN = 16.0          # diamond window diagonal

# marks
MARK_W = 0.8
MARK_L = 4.0
MARK_D = 0.6
HOLE_Y = -50.0          # sound hole centre

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="Guitar Core ABS+ 0.20mm @BBL H2C",
    standing=False,
    # tine clamp preload (~0.5 kgf per tine, 17 tines) carried by the two bolt columns
    loads=[dict(at=(-BOLT_X, 0, BOX_H + 16), grams=4250),
           dict(at=(BOLT_X, 0, BOX_H + 16), grams=4250)],
    # flat: saddle/bar loads are in compression; tine bending loads stay in steel.
    print_orientation=(0, 0, 0),
    # WARN accepted: the only "support" area (~0.6 cm2) is the two 7 mm hex nut-trap
    # ceilings in the tray floor - short bridges that print clean. 3 bodies = 3 parts.
    supports="off",
    brim="auto",
)

# ---------------- derived ----------------
Y_BACK = BOX_L / 2 - WALL - BACK_MARGIN          # back saddle
Y_FRONT = Y_BACK - SADDLE_GAP                    # front saddle (vibrating length start)
Y_BAR = (Y_BACK + Y_FRONT) / 2                   # pressure bar / bolts / rib


def tine_length(f_hz):
    """Ideal clamped-free length (mm) for frequency f."""
    t = TINE_T / 1000
    return math.sqrt(0.1615 * t * math.sqrt(E_STEEL / RHO_STEEL) / f_hz) * 1000


def tine_x(k):
    """Alternating layout, lowest in the middle."""
    return math.ceil(k / 2) * (1 if k % 2 else -1) * TINE_PITCH


def air_volume_m3():
    inner_h = BOX_H - FLOOR - TOP_T
    v = (BOX_W - 2 * WALL) * (BOX_L - 2 * WALL) * inner_h
    v -= (BOX_W - 2 * WALL) * RIB_T * inner_h * 0.6              # rib minus windows
    v -= 2 * math.pi * COLUMN_R**2 * inner_h * 0.6               # columns (partly in wall)
    return v * 1e-9


def helmholtz_hz(r_mm):
    r = r_mm / 1000
    a = math.pi * r * r
    l_eff = TOP_T / 1000 + HELM_END_K * r
    return C_AIR / (2 * math.pi) * math.sqrt(a / (air_volume_m3() * l_eff))


def sound_hole_r():
    lo, hi = 2.0, 40.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if helmholtz_hz(mid) > HELM_TARGET:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


HOLE_R = sound_hole_r()


def tray():
    body = rounded_box(BOX_W, BOX_L, BOX_H, radius=CORNER_R)
    cav = Pos(0, 0, FLOOR) * rounded_box(BOX_W - 2 * WALL, BOX_L - 2 * WALL, BOX_H,
                                         radius=CORNER_R - WALL, bottom_chamfer=0)
    reb = Pos(0, 0, BOX_H - TOP_T) * rounded_box(
        BOX_W - 2 * (WALL - REBATE), BOX_L - 2 * (WALL - REBATE), BOX_H,
        radius=CORNER_R - WALL + REBATE, bottom_chamfer=0)
    body = body - cav - reb
    inner_h = BOX_H - TOP_T - FLOOR
    # transverse bridge rib with diamond windows (45 deg overhangs)
    rib = Pos(0, Y_BAR, FLOOR) * Box(BOX_W - 2 * WALL, RIB_T, inner_h, align=ON_BED)
    win = Rot(0, 45, 0) * Box(RIB_WIN / math.sqrt(2), RIB_T + 2, RIB_WIN / math.sqrt(2))
    for x in (-44, -22, 0, 22, 44):
        rib = rib - Pos(x, Y_BAR, FLOOR + inner_h / 2) * win
    cols = [Pos(sx * BOLT_X, Y_BAR, FLOOR) * Cylinder(COLUMN_R, inner_h, align=ON_BED)
            for sx in (-1, 1)]
    body = body + rib + cols[0] + cols[1]
    for sx in (-1, 1):
        body = body - Pos(sx * BOLT_X, Y_BAR, BOX_H) * Cylinder(
            clearance(BOLT_D) / 2, BOX_H + 2, align=(Align.CENTER, Align.CENTER, Align.MAX))
        body = body - Pos(sx * BOLT_X, Y_BAR, 0) * Rot(180, 0, 0) * nut_trap(BOLT, 3.6)
    return body


def saddle(y):
    prof = Polygon((y - SADDLE_BASE / 2, 0), (y + SADDLE_BASE / 2, 0),
                   (y + SADDLE_TOP / 2, SADDLE_H), (y - SADDLE_TOP / 2, SADDLE_H), align=None)
    s = extrude(Plane.YZ * prof, SADDLE_LEN / 2, both=True)
    groove = Pos(0, y, SADDLE_H) * Rot(0, 90, 0) * Cylinder(ROD_D / 2 + 0.15, SADDLE_LEN + 2)
    return s - groove


def top():
    w = BOX_W - 2 * (WALL - REBATE) - 2 * FIT_GAP
    l = BOX_L - 2 * (WALL - REBATE) - 2 * FIT_GAP
    plate = rounded_box(w, l, TOP_T, radius=CORNER_R - WALL + REBATE - FIT_GAP)
    plate = plate + Pos(0, 0, TOP_T) * (saddle(Y_FRONT) + saddle(Y_BACK))
    plate = plate - Pos(0, HOLE_Y, TOP_T + 1) * Cylinder(HOLE_R, TOP_T + 3,
                                                         align=(Align.CENTER, Align.CENTER, Align.MAX))
    for sx in (-1, 1):
        plate = plate - Pos(sx * BOLT_X, Y_BAR, TOP_T + 1) * Cylinder(
            clearance(BOLT_D) / 2, TOP_T + 3, align=(Align.CENTER, Align.CENTER, Align.MAX))
    for k, (_, f) in enumerate(NOTES):
        y_tip = Y_FRONT - K_EMP * tine_length(f)
        plate = plate - Pos(tine_x(k), y_tip, TOP_T) * Rot(0, 0, 90) * slot(MARK_L, MARK_W, MARK_D)
    return plate


def bar():
    b = Box(BAR_L, BAR_W, BAR_H, align=ON_BED)
    b = chamfer(b.edges().group_by(Axis.Z)[-1], 1.0)
    for sx in (-1, 1):
        b = b - Pos(sx * BOLT_X, 0, BAR_H + 1) * Cylinder(
            clearance(BOLT_D) / 2, BAR_H + 3, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return b


def build():
    gap = 3.0
    t = Pos(-(BOX_W / 2 + gap / 2), 0, 0) * tray()
    p = Pos(BOX_W / 2 - WALL + REBATE + gap / 2, 0, 0) * top()
    b = Pos(-(BOX_W / 2 + gap / 2), -(BOX_L / 2 + gap + BAR_W / 2), 0) * bar()
    return [t, p, b]
