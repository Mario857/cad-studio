"""soprano-ukulele: playable soprano ukulele, scale 346 mm, GCEA (re-entrant), bolt-on neck.

Spec
- Overall ~555 mm (headstock tip to tail). Body 240 x 164 x 58 mm (figure-8: lower bout
  R82, upper bout R66, waist rounded R40, 45-deg-tangent flat tail so it stands on end).
  12 printed frets, Helmholtz-tuned teardrop sound hole.
- Parts, all on ONE 300x320 plate (build() returns them already laid out):
  BODY    closed hollow body (3 mm top/back/sides, integral soundboard), printed standing
          on its flat tail. Neck block (60 mm) with a gable (45 deg) underside, tenon
          pocket, 2 counterbored M5 holes from the back (teardrop), 2 triangular top braces,
          bridge pad with 2 M4 heat-set inserts, 2 triangular back ribs.
  NECK    neck + flat stepped headstock + nut + 12 raised frets + 50 mm tenon, lies flat on
          its back; 6.4 mm square truss channel (open at the tenon end); 2 M5 heat-set
          inserts in the tenon underside.
  BRIDGE  tie-bar bridge, saddle slot 3.2 mm, 4 tie holes Ø2 (teardrop), 2 M4 bolts.
  SADDLE  printed 3 mm saddle (or a bone/Tusq blank).
- Strength: string tension (~14 kgf) runs along the layers in NECK, BRIDGE and SADDLE (flat).
  The BODY only carries it as compression between bridge and neck block (= across layers,
  which ABS takes fine); the bridge load goes into a thick pad through 2 bolts.

Physics (computed in code)
- Frets: d_n = S * (1 - 2^(-n/12)), S = 346 mm. Saddle crest at S + SADDLE_COMP (1.8 mm).
- Strings: T = mu * (2 S f)^2, mu = rho * pi d^2 / 4, Nylgut/nylon rho = 1300 kg/m^3.
- Helmholtz: f = c/(2 pi) sqrt(A / (V L_eff)), c = 343 m/s, L_eff = t + 1.7 r_eq,
  V = net cavity volume measured from the CAD cavity solid; teardrop hole area
  A = (pi + 1 - pi/4) r^2; r solved for HELM_TARGET = 280 Hz (typical soprano air mode,
  between C#4 and D4 - supports the low C and E strings).
- Action: frets 1.0 mm, nut 0.5 mm above fret tops, 2.8 mm at the 12th fret -> saddle crest
  from the straight string line (SADDLE_CREST_Z ~14.1 mm above the top).

TUNING (scale 346 mm, Nylgut-type strings, rho 1300 kg/m^3)
| string | target Hz | gauge mm | mu g/m | tension N (kgf) | vibrating length mm |
| G4 (re-entrant) | 392.00 | 0.68 | 0.472 | 34.7 (3.54) | 347.8 (346 + 1.8) |
| C4 | 261.63 | 1.03 | 1.083 | 35.5 (3.62) | 347.8 |
| E4 | 329.63 | 0.79 | 0.637 | 33.2 (3.38) | 347.8 |
| A4 | 440.00 | 0.61 | 0.380 | 35.2 (3.59) | 347.8 |
| total | | | | 138.6 (14.1 kgf) | |
| body air (Helmholtz) | 280 | V 1.13 L | teardrop hole r 17.1 mm (Ø34.2 + 45° point) | | |
Frets from nut (mm): 1 19.42, 2 37.75, 3 55.05, 4 71.38, 5 86.79, 6 101.34,
7 115.07, 8 128.03, 9 140.27, 10 151.81, 11 162.71, 12 173.00.

Fine-tuning after printing
1. Nut: file each notch (needle file / folded sandpaper) until a string fretted at the 3rd
   fret just clears the 1st fret (~0.1 mm). Start notches are only 0.5 mm deep.
2. Action: string-bottom to 12th fret top 2.8 (G/C) / 2.5 (E/A) mm. Sand the saddle bottom
   flat to lower (0.5 mm at the saddle = 0.25 mm at the 12th fret).
3. Intonation: compare 12th-fret harmonic vs fretted note. Fretted sharp -> move the crest
   back (sand the front face of the saddle top), flat -> forward (sand the back face).
4. Fret buzz: level the printed frets with a sanding beam (400 grit) and re-crown, or glue
   2 mm fret wire on top. Truss rod in place reduces neck relief.
5. New Nylgut strings stretch for ~2 days: retune often.

Hardware to buy
- 1 set soprano ukulele strings GCEA (Aquila Nylgut 4U or similar, or fluorocarbon).
- 4 ukulele tuners for 9.5-10 mm holes, headstock 13 mm (friction pegs e.g. Grover 2B,
  or planetary Gotoh UPT; ream holes to 10.0 mm if needed).
- 2x M5 heat-set inserts (OD ~6.4, 8-10 long) + 2x M5x25 socket head + 2 washers.
- 2x M4 heat-set inserts + 2x M4x10 socket/button head (bridge).
- Optional truss rod: 6x6 mm steel square bar or Ø6 carbon rod, 205 mm long.

Assembly
1. Melt the M5 inserts into the tenon underside and the M4 inserts into the bridge pad
   holes on the top of the body (soldering iron, ~230 C, keep them square).
2. Slide the truss rod into the tenon channel (dab of epoxy).
3. Drop the NECK tenon into the body pocket, bolt from the back with 2x M5x25.
4. Bolt the BRIDGE onto the top with 2x M4x10 (tie block toward the tail).
5. Push the SADDLE into the slot, install the tuners, string up: thread the string through
   the bridge hole from the saddle side, loop it back over itself twice, then wind onto
   the peg.

Assumptions
- Flat headstock 13 mm thick, stepped 9 mm below the fretboard with a 45 deg ramp:
  ~12 deg break angle to the near pegs, ~6 deg to the far pegs (add a string tree if the
  far strings rattle in the nut).
- Neck joins the body at the 12th fret (+5 mm), fretboard 8 mm above the top.
- Printed ABS frets (like moulded polycarbonate ukes); fret wire is an optional upgrade.
- String gauges chosen for ~3.5 kgf per string (close to Aquila Nylgut soprano).
- Parts are laid out for printing (neck flat, body rotated onto its tail); in-use
  geometry is built in body coordinates (nut at y=0, strings along -Y, top at z=BODY_H).
"""

import math

from build123d import *

from cadlib import *

# ---------------- physics ----------------
C_AIR = 343.0
SCALE = 346.0
SADDLE_COMP = 1.8
N_FRETS = 12
STRING_RHO = 1300.0
STRINGS = [("G4", 392.00, 0.68), ("C4", 261.63, 1.03), ("E4", 329.63, 0.79), ("A4", 440.00, 0.61)]
HELM_TARGET = 280.0
HELM_END_K = 1.7

# ---------------- neck ----------------
NUT_W = 35.0
JOINT_W = 42.0            # neck width at body joint / tenon width
NECK_H = 22.0             # back -> fretboard surface
NECK_CHAMFER = 7.0        # back chamfers (run), rise = 1.25x (steeper than 45 deg)
JOINT_OFFSET = 5.0        # body edge past the 12th fret
TENON_L = 50.0
HEAD_L = 82.0
HEAD_W = 54.0
HEAD_T = 13.0
NUT_L = 5.0
FRET_H = 1.0
FRET_W = 2.0
NUT_ABOVE_FRET = 0.5
ACTION_12 = 2.8
NOTCH_W = 1.2
STR_SPACING_NUT = 9.0
STR_SPACING_BRIDGE = 11.0
PEG_D = 9.7
PEG_POS = [(-14.0, 32.0), (-14.0, 62.0), (14.0, 32.0), (14.0, 62.0)]   # (x, y past nut)
TRUSS = 6.4
TRUSS_Z = 5.0
TRUSS_STOP = 20.0         # channel stops this far before the nut
NECK_BOLT_X = 12.0
DOT_D = 4.0

# ---------------- body ----------------
BODY_H = 58.0
R_LOWER = 82.0
R_UPPER = 66.0
BOUT_DIST = 92.0
WAIST_R = 40.0
WALL = 3.0                # sides
BACK_T = 3.0
TOP_T = 3.0               # integral soundboard
BLOCK_L = 60.0
FB_ABOVE_TOP = 8.0
POCKET_GAP = 0.25
M5_CLEAR = 5.5
CBORE_D = 10.0
CBORE_H = 33.0            # from the back -> 11 mm grip, M5x25 into a 10 mm insert
BRACE_H = 6.0             # triangular braces (45 deg face toward the tail)
BACK_RIB_H = 5.0
PAD_T = 8.0               # bridge pad under the top (insert boss)

# ---------------- bridge ----------------
BRIDGE_W = 86.0
BRIDGE_FRONT = 6.0        # ahead of the saddle (toward the neck)
BRIDGE_BACK = 17.0
BRIDGE_BASE_H = 4.0
BRIDGE_H = 10.0
SADDLE_T = 3.0
SADDLE_SLOT = 3.2
SADDLE_SLOT_D = 5.0
SADDLE_LEN = 60.0
TIE_H = 8.5
TIE_HOLE_D = 2.0
TIE_HOLE_Z = 5.5
BRIDGE_BOLT_X = 38.5
BRIDGE_BOLT_Y = -5.5      # bridge-local (saddle crest at y=0)
GAP = 6.0                 # between parts on the plate

# ---------------- derived ----------------
FRETS = [SCALE * (1 - 2 ** (-n / 12)) for n in range(1, N_FRETS + 1)]
Y_JOINT = -(FRETS[11] + JOINT_OFFSET)          # body top end (nut at y=0)
Y_TENON_END = Y_JOINT - TENON_L
Y_UPPER_C = Y_JOINT - R_UPPER
Y_LOWER_C = Y_UPPER_C - BOUT_DIST
Y_TAIL = Y_LOWER_C - R_LOWER
Y_BLOCK_END = Y_JOINT - BLOCK_L
Y_SADDLE = -(SCALE + SADDLE_COMP)
NUT_Z = FRET_H + NUT_ABOVE_FRET                  # string above fretboard at the nut
STR_12 = FRET_H + ACTION_12
STR_SADDLE = NUT_Z + (STR_12 - NUT_Z) * (SCALE + SADDLE_COMP) / (SCALE / 2)
SADDLE_CREST_Z = FB_ABOVE_TOP + STR_SADDLE       # above the soundboard
SADDLE_H = SADDLE_CREST_Z - (BRIDGE_H - SADDLE_SLOT_D)
Z_NECK_BACK = BODY_H + FB_ABOVE_TOP - NECK_H     # in body coordinates
Y_NECK_BOLT = (Y_JOINT + Y_TENON_END) / 2
HOLE_Y = Y_BLOCK_END - 50.0                      # sound hole centre
Z_IN_LO, Z_IN_HI = BACK_T, BODY_H - TOP_T        # cavity z range


def string_tension_n(f, d_mm):
    mu = STRING_RHO * math.pi * (d_mm / 1000) ** 2 / 4
    return mu * (2 * SCALE / 1000 * f) ** 2


TOTAL_TENSION_G = sum(string_tension_n(f, d) for _, f, d in STRINGS) / 9.80665 * 1000


def outline():
    s = Pos(0, Y_UPPER_C) * Circle(R_UPPER) + Pos(0, Y_LOWER_C) * Circle(R_LOWER)
    k = R_LOWER / math.sqrt(2)
    tail_flat = R_LOWER * math.sqrt(2) - R_LOWER     # 45-deg tangents -> flat tail
    s = s + Polygon((-(k - (R_LOWER - k)), Y_TAIL), (k - (R_LOWER - k), Y_TAIL),
                    (k, Y_LOWER_C - k), (-k, Y_LOWER_C - k), align=None)
    del tail_flat
    return offset(offset(s, WAIST_R, kind=Kind.ARC), -WAIST_R, kind=Kind.ARC)


def neck_w(y):
    t = min(max(-y / -Y_JOINT, 0), 1)
    return NUT_W + (JOINT_W - NUT_W) * t


def yz_prism(points, x_half):
    return extrude(Plane.YZ * Polygon(*points, align=None), x_half, both=True)


def cavity():
    cav = Pos(0, 0, Z_IN_LO) * extrude(offset(outline(), -WALL), Z_IN_HI - Z_IN_LO)
    zm = (Z_IN_LO + Z_IN_HI) / 2
    lo, hi = Z_IN_LO - 2, Z_IN_HI + 2
    gable = yz_prism([(Y_TAIL - 50, lo), (Y_BLOCK_END - (zm - lo), lo), (Y_BLOCK_END, zm),
                      (Y_BLOCK_END - (hi - zm), hi), (Y_TAIL - 50, hi)], 200)
    return cav & gable


CAV_V = cavity().volume * 1e-9                  # m^3 (braces/ribs/pad ~3 %, ignored)
TEAR_K = math.pi + 1 - math.pi / 4              # teardrop area / r^2


def helmholtz_hz(r_mm):
    r = r_mm / 1000
    a = TEAR_K * r * r
    r_eq = math.sqrt(a / math.pi)
    return C_AIR / (2 * math.pi) * math.sqrt(a / (CAV_V * (TOP_T / 1000 + HELM_END_K * r_eq)))


def _solve_hole():
    lo, hi = 5.0, 40.0
    for _ in range(60):
        m = (lo + hi) / 2
        lo, hi = (lo, m) if helmholtz_hz(m) > HELM_TARGET else (m, hi)
    return (lo + hi) / 2


HOLE_R = _solve_hole()

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="Guitar Core ABS+ 0.20mm @BBL H2C",
    standing=False,
    # total string tension (~14.1 kgf) at the two anchors: saddle and nut/headstock
    loads=[dict(at=(0, Y_SADDLE, BODY_H + SADDLE_CREST_Z), grams=round(TOTAL_TENSION_G)),
           dict(at=(0, 0, BODY_H + FB_ABOVE_TOP + NUT_Z), grams=round(TOTAL_TENSION_G))],
    # parts are pre-oriented in build(): neck/bridge/saddle flat (tension along layers),
    # body on its tail (body is in compression only).
    print_orientation=(0, 0, 0),
    # WARN accepted: ~1.1 cm2 "support" = ceilings of the 4 heat-set insert holes
    # (Ø5.6-6.4 mm, bridge fine). Several bodies = 4 separate parts by design.
    supports="off",
    brim="on",  # 240 mm-tall body on a 68x58 mm tail: brim for bed adhesion
)


# ---------------- parts ----------------
def neck():
    """Neck-local: back at z=0, nut fret-side edge at y=0, body toward -Y."""
    def sec(y, w):
        c = NECK_CHAMFER
        pl = Plane(origin=(0, y, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
        return pl * Polygon((-w / 2 + c, 0), (w / 2 - c, 0), (w / 2, 1.25 * c), (w / 2, NECK_H),
                            (-w / 2, NECK_H), (-w / 2, 1.25 * c), align=None)
    n = loft([sec(NUT_L, NUT_W), sec(Y_JOINT + 1, neck_w(Y_JOINT))])
    n = n + Pos(0, (Y_JOINT + 8 + Y_TENON_END) / 2, 0) * Box(
        JOINT_W, Y_JOINT + 8 - Y_TENON_END, NECK_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    head_end = NUT_L + HEAD_L
    ramp = NECK_H - HEAD_T
    head = yz_prism([(NUT_L - 0.5, 0), (head_end, 0), (head_end, HEAD_T),
                     (NUT_L + ramp, HEAD_T), (NUT_L, NECK_H), (NUT_L - 0.5, NECK_H)], HEAD_W / 2)
    head = chamfer(head.edges().filter_by(Axis.Z).group_by(Axis.Y)[-1], 8)
    n = n + head
    # nut
    n = n + yz_prism([(0, NECK_H - 0.5), (NUT_L, NECK_H - 0.5), (NUT_L, NECK_H + NUT_Z - 0.5),
                      (1.0, NECK_H + NUT_Z), (0, NECK_H + NUT_Z)], NUT_W / 2 - 0.5)
    for i in range(4):
        x = (i - 1.5) * STR_SPACING_NUT
        n = n - Pos(x, NUT_L / 2, NECK_H + NUT_Z) * Box(NOTCH_W, NUT_L + 2, 1.0)
    # frets
    for d in FRETS:
        w = neck_w(-d) - 1.0
        n = n + yz_prism([(-d - FRET_W / 2, NECK_H - 0.2), (-d + FRET_W / 2, NECK_H - 0.2),
                          (-d, NECK_H + FRET_H)], w / 2)
    # position dots
    dots = [(0, -(FRETS[f - 1] + FRETS[f - 2]) / 2) for f in (5, 7, 10)]
    y12 = -(FRETS[11] + FRETS[10]) / 2
    dots += [(-8, y12), (8, y12)]
    for x, y in dots:
        n = n - Pos(x, y, NECK_H + 0.01) * Cylinder(DOT_D / 2, 0.6,
                                                     align=(Align.CENTER, Align.CENTER, Align.MAX))
    # peg holes
    for x, y in PEG_POS:
        n = n - Pos(x, NUT_L + y, 0) * Cylinder(PEG_D / 2, 3 * HEAD_T)
    # truss channel (open at tenon end)
    tl = -TRUSS_STOP - (Y_TENON_END - 1)
    h = TRUSS / 2                       # 45 deg gable roof: no bridging needed
    prof = Polygon((-h, TRUSS_Z), (h, TRUSS_Z), (h, TRUSS_Z + TRUSS), (0, TRUSS_Z + TRUSS + h),
                   (-h, TRUSS_Z + TRUSS), align=None)
    pl = Plane(origin=(0, -TRUSS_STOP, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    n = n - extrude(pl * prof, tl)
    # heat-set inserts from the underside of the tenon
    for sx in (-1, 1):
        n = n - Pos(sx * NECK_BOLT_X, Y_NECK_BOLT, 0) * Rot(180, 0, 0) * insert_hole("M5")
    return n


def tri_brace(y0, z_face, h, down=True):
    """Triangular brace along X at y0 on a horizontal face; 45 deg face toward -Y."""
    s = -1 if down else 1
    pts = [(y0, z_face), (y0, z_face + s * h), (y0 - h, z_face)]
    return yz_prism(pts, 200)


def body():
    """In-use coordinates: back at z=0, top at BODY_H, neck end toward +Y."""
    out = extrude(outline(), BODY_H)
    b = out - cavity()
    inner = Pos(0, 0, Z_IN_LO - 0.5) * extrude(offset(outline(), -WALL + 0.2), Z_IN_HI - Z_IN_LO + 1)
    inner = inner & Pos(0, Y_BLOCK_END - 20, 0) * Box(400, 400, 400, align=(Align.CENTER, Align.MAX, Align.MIN))
    # top braces either side of the sound hole, back ribs, bridge pad
    adds = [tri_brace(HOLE_Y + HOLE_R * 1.42 + 10, Z_IN_HI, BRACE_H),
            tri_brace(HOLE_Y - HOLE_R - 8, Z_IN_HI, BRACE_H),
            tri_brace(HOLE_Y, Z_IN_LO, BACK_RIB_H, down=False),
            tri_brace(Y_SADDLE - 10, Z_IN_LO, BACK_RIB_H, down=False)]
    pf, pb = Y_SADDLE + BRIDGE_FRONT + 2, Y_SADDLE - BRIDGE_BACK - 2
    adds.append(yz_prism([(pf, Z_IN_HI), (pf, Z_IN_HI - PAD_T), (pb, Z_IN_HI - PAD_T),
                          (pb - PAD_T, Z_IN_HI)], BRIDGE_W / 2 + 6))
    for a in adds:
        b = b + (a & inner)
    # sound hole (teardrop, point toward the neck = up when printing)
    th = Pos(0, HOLE_Y, BODY_H + 1) * extrude(
        Circle(HOLE_R) + Rot(0, 0, 45) * Rectangle(HOLE_R, HOLE_R, align=(Align.MIN, Align.MIN)),
        -(TOP_T + 2))
    b = b - th
    # bridge inserts
    for sx in (-1, 1):
        b = b - Pos(sx * BRIDGE_BOLT_X, Y_SADDLE + BRIDGE_BOLT_Y, BODY_H) * insert_hole("M4")
    # neck pocket
    pl = (Y_JOINT + 20) - (Y_TENON_END - POCKET_GAP)
    b = b - Pos(0, Y_TENON_END - POCKET_GAP + pl / 2, Z_NECK_BACK) * Box(
        JOINT_W + 2 * POCKET_GAP, pl, 50, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # M5 clearance + counterbore from the back, teardrop (point toward the neck)
    for sx in (-1, 1):
        for d, h in ((M5_CLEAR, Z_NECK_BACK + 2), (CBORE_D, CBORE_H + 1)):
            td = Rot(-90, 0, 0) * teardrop_hole(d, h, along="Y")
            b = b - Pos(sx * NECK_BOLT_X, Y_NECK_BOLT, h / 2 - 1) * td
    return b


def bridge():
    """In-use: sits on the soundboard (z=0 local), saddle crest line at local y=0."""
    base = Pos(0, (BRIDGE_FRONT - BRIDGE_BACK) / 2, 0) * Box(
        BRIDGE_W, BRIDGE_FRONT + BRIDGE_BACK, BRIDGE_BASE_H, align=ON_BED)
    base = chamfer(base.edges().group_by(Axis.Z)[-1], 1.2)
    sb = Box(SADDLE_LEN + 8, 8, BRIDGE_H, align=ON_BED)
    sb = chamfer(sb.edges().group_by(Axis.Z)[-1], 1.5)
    tie = Pos(0, -BRIDGE_BACK + 4.5, 0) * Box(4 * STR_SPACING_BRIDGE + 10, 9, TIE_H, align=ON_BED)
    tie = chamfer(tie.edges().group_by(Axis.Z)[-1], 1.5)
    b = base + sb + tie
    b = b - Pos(0, 0, BRIDGE_H + 0.01) * Box(SADDLE_LEN, SADDLE_SLOT, SADDLE_SLOT_D,
                                            align=(Align.CENTER, Align.CENTER, Align.MAX))
    for i in range(4):
        x = (i - 1.5) * STR_SPACING_BRIDGE
        b = b - Pos(x, -BRIDGE_BACK + 4.5, TIE_HOLE_Z) * teardrop_hole(TIE_HOLE_D, 12, along="Y")
    for sx in (-1, 1):
        b = b - Pos(sx * BRIDGE_BOLT_X, BRIDGE_BOLT_Y, BRIDGE_H) * Cylinder(
            clearance(4.0) / 2, 30, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return b


def saddle_part():
    s = Box(SADDLE_LEN - 0.4, SADDLE_T, SADDLE_H, align=ON_BED)
    return chamfer(s.edges().group_by(Axis.Z)[-1], 1.0)


def build():
    """Print layout on one plate: neck flat (along Y), body on its tail, bridge + saddle."""
    nk = neck()
    nb = nk.bounding_box()
    nk = Pos(-150 + 2 - nb.min.X, -(nb.min.Y + nb.max.Y) / 2, 0) * nk
    nb = nk.bounding_box()
    bd = Rot(90, 0, 0) * body()          # +Y (neck end) -> +Z, top (+Z) -> -Y
    bb = bd.bounding_box()
    bd = Pos(nb.max.X + GAP - bb.min.X, 160 - 2 - bb.max.Y, -bb.min.Z) * bd
    bb = bd.bounding_box()
    br = bridge()
    rb = br.bounding_box()
    br = Pos((bb.min.X + bb.max.X) / 2, bb.min.Y - GAP - rb.max.Y, 0) * br
    rb = br.bounding_box()
    sd = Pos((bb.min.X + bb.max.X) / 2, rb.min.Y - GAP - SADDLE_T / 2, 0) * saddle_part()
    return [nk, bd, br, sd]
