"""travel-laptop-stand: Roost-style folding travel stand for a MacBook Pro 13" and 15", three heights.

Function: lifts the laptop to a raised, tilted position on a desk (used with an external keyboard) and
  folds into two flat bundles + two cross bars for a bag. Indoor use, but it travels (bags, trains, a
  parked car) -> PETG: PLA softens at ~55-60 C and is too brittle for the hook fingers.
Kit (one plate): 2 rest arms (A), 2 hook struts (B), 2 spreaders, 2 height keys + 1 spare.
How it works (side view: Y = depth towards the screen, Z up; frames at X = +/-100):
  - Bar A (rest arm, inner): front foot on the desk, rises to the rear; its rounded top end carries the
    laptop's underside.
  - Bar B (hook strut, outer): rear foot on the desk, rises to the front; its top end is a C-hook that
    holds the laptop's front edge so the laptop cannot slide off or be tipped out.
  - A and B cross at one M5 pivot bolt per side. The load tries to flatten the X. A height key (a flat
    cam with a square peg) plugs into a square socket on an ear of bar B; bar A's edge lands on the
    key's flat and that is the stop. The key goes in three ways round, the number 1, 2 or 3 against
    bar A:
        setting   front edge   tilt     rear edge 15" / 13"
        1 (low)     84 mm      14 deg     141 / 134 mm
        2          100 mm      18 deg     175 / 166 mm
        3 (high)   115 mm      23 deg     210 / 199 mm
    To change height: lift the laptop off, close the X a little, pull the key, turn it, push it back.
    Both keys must show the same number. The key is the same for the left and the right frame.
  - The hook is cut for setting 1; in settings 2 and 3 the laptop swings up inside it, so the finger
    opens upwards by that swing (20 deg) and the laptop's front edge leans on the hook wall.
  - Two identical spreaders (10 mm square tenons, snug) plug 20 mm deep into square sockets in the
    round feet: front one joins the A feet, rear one the B feet. Both pairs of socket bosses end at the
    same X (bar B's boss is longer by one bar thickness), so one spreader length fits both. Tenons enter
    from the boss side = the top of the print, away from any elephant foot.
  - To fold: pull the spreaders and the keys, swing the bars the other way until they lie on each
    other; park each key in a foot socket (same square).
  - Taking the laptop off: slide it ~10 mm up the slope out of the hooks, then lift. Lifting the rear
    edge first only picks the (light) stand up with it.
Print: build() is the print layout (all parts flat on one plate, mating faces down, no supports);
  assembled(setting) returns the in-use pose; the geometry is drawn in setting 2.
Mechanism (docs/mechanisms.md): metal pivot bolt, not a printed pin; hard stop, no flexing parts;
  every bar printed flat so bending runs along the layers; hook finger root 5 mm (>= 3). The key's peg
  stands up from its cam, so it is loaded across its layers: see Loads.

Dimensions
  laptop 13": 304.1 x 212.4, 1.40 kg                   MEASURED (Apple spec, obj("macbook-pro-13"))
  laptop 15": 349.3 x 240.7, 1.83 kg                   MEASURED (Apple spec, obj("macbook-pro-15"))
  hook slot SLOT_W 12.0                                MEASURED (fit gauge: slot 12 goes on freely)
  pivot: M5 x 20 countersunk screw + M5 nyloc nut      MEASURED (standard; bore 5.3, csk 10.4, nut 8 AF)
  spreader tenon / key peg 10.0 in socket 10.3 (snug)  UNVERIFIED as a fit -> travel-laptop-stand-joint-coupon
  frame spacing 200, bar 22 x 10, heights and tilts above: design choices, nothing mates with them
Loads (hand calculation, per side frame, 40 N total = 1.83 kg laptop + 20 N hand pressure):
  rest ~15 N, hook ~5 N; stop moment at the pivot ~2.3 N.m, taken 34-46 mm from the pivot -> 50-70 N on
  the key: under 1 MPa bearing on its flat, 0.7 MPa shear and ~2 MPa peel across the layers at the peg
  root (PETG layer bond is 15+ MPa). The force runs through the peg's centre, so it does not turn the
  key. Bar bending 2.8 MPa; rest-end deflection ~0.6 mm. Side sway at 5 N: ~3 mm from bar bending
  (skins only, infill ignored) + 1-2 mm from socket play = about 5 mm.
  Stability, 15" at setting 3 (worst): centre of mass 60 mm inside the rear feet, tips at ~18 deg.
  META force is not set: the audit's beam estimate runs on the flat print layout, where it means nothing.

Print order: travel-laptop-stand-joint-coupon first (26 min, 13 g): it proves the 10 mm square fit used by
  the spreaders and the keys, and the pivot hardware. Only then this plate (first-print risk HIGH).

Assumptions
  - The gauge result applies to both laptops (one number was reported).
  - 2x M5 x 20 countersunk screw + 2x M5 nyloc nut are acceptable hardware; tighten until the bars
    still swing with light drag.
  - The laptop is not typed on while it is on the stand.
  - Desk grip: the feet are round (they roll as the height changes), so a rubber dot will not stick;
    a wide rubber band or a turn of silicone tape around each foot. Not modelled.
Risks
  - Side-to-side wobble: 0.15 mm play in four 20 mm sockets is ~1 mm of sway each; if it annoys, the
    spreader tenons want a wrap of tape or a tighter fit ("press").
  - The two keys set to different numbers twist the laptop; a lost key means no stop (one spare printed).
  - Spreaders and keys are held by friction only and can drop out when the stand is carried assembled.
  - Bare PETG feet slide on a smooth desk.
  - PETG creeps at the stop under load in a hot car: store it folded. If a key ever lets go the X
    flattens and the laptop sinks; it does not fall off.
  - Hook finger (5 x 10 mm, two walls + infill) breaks if the laptop is levered up by its rear edge while
    the stand is held down. In setting 1 the finger sits ~3 mm above the palm rest (looser hold).
Accept
  - Both laptops' front edges slide into the hooks with no force in all three settings and cannot lift
    straight out.
  - Front edge height 84 / 100 / 115 mm (+/- 5) in settings 1 / 2 / 3; unchanged after 30 min with the 15".
  - The key goes in and out by hand and the same key fits either side.
  - 2 kg pressed on the laptop's rear edge in setting 3: no collapse, feet stay down.
  - 5 N sideways push on the laptop: sway under 6 mm.
  - Folds into two bundles of about 310 x 42 x 32 mm plus two 200 mm bars; under 190 g with hardware.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="PETG",
    quality="standard",        # "strong" (4 walls, 40 %) is stiffer sideways but 205 g instead of 123 g
    status="draft",
    standing=False,            # build() is the flat print layout; stability is worked out in the docstring
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="on",                 # six long PETG parts on one plate: one lifted corner scraps 3 h
)

# --- Parameters (side view: y = depth, z = height). Everything is drawn in setting 2 (middle). -----
TILT = 18.0              # laptop tilt in setting 2 (deg)
HOOK_Y = 30.0            # hook corner (where the laptop's front-bottom edge sits), behind the front feet
HOOK_Z = 100.0           # ... and above the desk, in setting 2
REST_S = 170.0           # rest point in setting 2, measured along the laptop from its front edge
REAR_Y = 230.0           # rear feet behind the front feet in setting 2
STEP = 12.0              # bar A turns this much against bar B between settings (deg)
SETTINGS = (1, 2, 3)     # 1 = low, 2 = middle, 3 = high

BAR_W = 22.0             # bar width (in the side plane)
BAR_T = 10.0             # bar thickness (across): sets the sideways stiffness
FRAME_X = 100.0          # plane where bar A (inside) and bar B (outside) slide on each other
HUB_D = 26.0
FOOT_R = BAR_W / 2       # round feet (= the bar's own round end): they roll on the desk between settings

LAPTOP_T = 11.6          # stand-in laptop base thickness (slot 12 goes on freely)
SLOT_W = 12.0            # hook slot at its root (fit gauge)
JAW_L = 16.0             # lower jaw length under the laptop
JAW_T = 6.0
WALL_T = 5.0             # wall the laptop's front edge rests against
FINGER_T = 5.0
FINGER_L = 7.0           # finger reach over the palm rest
FLARE_MARGIN = 2.0       # extra opening of the finger beyond the laptop's swing between settings (deg)
LEAD = 1.5               # lead-in chamfer at the jaw tip

PIVOT_D = 5.3            # bore for an M5 screw with little play
CSK_D = 10.4
NUT_DEPTH = 5.5          # nyloc nut (5 mm) sits below the face; an M5 x 20 screw just passes through it

KEY_R = 50.0             # key socket: distance from the pivot
KEY_DELTA = 35.0         # ... and angle below bar A's centre line in setting 2 (deg)
KEY_GAP_X = 0.4          # key and its peg are this much thinner than a bar

TENON = 10.0             # spreader tenon and key peg (square)
TENON_L = 20.0
BOSS = 12.0              # socket boss on bar A's inner face (bar B's boss is BOSS + BAR_T)
COLLAR_W = 16.0
COLLAR_UP = 3.0
COLLAR_T = 4.0
NUM_SIZE = 5.0
NUM_H = 0.6

PLATE_GAP = 4.0          # spacing between parts on the print plate
SPARE_KEYS = 1


# --- Side-view maths ---------------------------------------------------------------------------------
def add(p, q, k=1.0):
    return (p[0] + k * q[0], p[1] + k * q[1])


def unit(p, q):
    d = math.dist(p, q)
    return ((q[0] - p[0]) / d, (q[1] - p[1]) / d)


def polar(deg, r=1.0):
    return (r * math.cos(math.radians(deg)), r * math.sin(math.radians(deg)))


def angle_of(d):
    return math.degrees(math.atan2(d[1], d[0]))


def turn(p, pivot, deg):
    """Rotate side-plane point p about pivot (counter-clockwise seen from the right-hand side)."""
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    y, z = p[0] - pivot[0], p[1] - pivot[1]
    return (pivot[0] + y * c - z * s, pivot[1] + y * s + z * c)


def _cross(p, q):
    return p[0] * q[1] - p[1] * q[0]


U, N = polar(TILT), polar(TILT + 90)           # along / out of the laptop's underside in setting 2
HOOK = (HOOK_Y, HOOK_Z)
FA = (0.0, FOOT_R)                                             # bar A: front foot ...
TA = add(add(HOOK, U, REST_S), N, -BAR_W / 2)                  # ... to the rest end (round end = rest)
FB = (REAR_Y, FOOT_R)                                          # bar B: rear foot ...
HB = add(add(HOOK, U, 4.0), N, -BAR_W / 2 - 3.5)               # ... to under the hook jaw
DIR_A, DIR_B = unit(FA, TA), unit(FB, HB)
PIVOT = add(FA, DIR_A, _cross((FB[0] - FA[0], FB[1] - FA[1]), DIR_B) / _cross(DIR_A, DIR_B))

KEY_C = add(PIVOT, polar(angle_of(DIR_A) - KEY_DELTA), KEY_R)  # key socket centre (on bar B's ear)
KEY_TURN = angle_of(DIR_A)                                     # socket is square to bar A in setting 2


def key_radius(setting: int) -> float:
    """Distance from the key socket centre to bar A's lower edge in that setting = lobe radius."""
    return KEY_R * math.sin(math.radians(KEY_DELTA + (setting - 2) * STEP)) - BAR_W / 2


def pose(setting: int) -> tuple[float, float, tuple[float, float]]:
    """(A's turn against B, turn of the whole frame, shift) that puts both feet on the desk."""
    rel = (setting - 2) * STEP
    foot_a = turn(FA, PIVOT, rel)
    tip = -angle_of((FB[0] - foot_a[0], FB[1] - foot_a[1]))
    landed = turn(foot_a, (0.0, 0.0), tip)
    return rel, tip, (-landed[0], FOOT_R - landed[1])


def to_world(p, setting: int, on_a: bool = False):
    rel, tip, shift = pose(setting)
    if on_a:
        p = turn(p, PIVOT, rel)
    return add(turn(p, (0.0, 0.0), tip), shift)


def _tangent(corner, setting: int) -> float:
    """Tilt of a line from `corner` that just clears bar A's round rest end from above."""
    rest = to_world(TA, setting, on_a=True)
    reach = math.dist(corner, rest)
    return angle_of((rest[0] - corner[0], rest[1] - corner[1])) + math.degrees(math.asin(BAR_W / 2 / reach))


# The hook is cut for setting 1 (lowest); raising the stand swings the laptop upwards inside it, so the
# finger opens by that swing and the laptop's front-top edge leans on the hook wall.
HOOK_ANG = _tangent(to_world(HOOK, 1), 1) - pose(1)[1]                       # in drawing coordinates
FLARE = _tangent(to_world(HOOK, 3), 3) - pose(3)[1] - HOOK_ANG + FLARE_MARGIN
UH, NH = polar(HOOK_ANG), polar(HOOK_ANG + 90)


def laptop_line(setting: int) -> tuple[tuple[float, float], float]:
    """World position of the laptop's front-bottom edge and its tilt in a setting."""
    corner = to_world(HOOK, setting)
    hook_world = HOOK_ANG + pose(setting)[1]
    tilt = _tangent(corner, setting)
    for _ in range(3):   # the bottom edge slides back along the jaw as the laptop leans on the wall
        back = LAPTOP_T * math.sin(math.radians(max(tilt - hook_world, 0.0)))
        tilt = _tangent(add(corner, polar(hook_world), back), setting)
    return add(corner, polar(hook_world), back), tilt


# --- Sketch helpers (side plane: sketch x = model y, sketch y = model z) --------------------------
def stadium(p, q, width):
    mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    return Pos(*mid) * Rot(0, 0, angle_of((q[0] - p[0], q[1] - p[1]))) * SlotOverall(math.dist(p, q) + width, width)


def foot(p):
    return Pos(*p) * Circle(FOOT_R)


def slab(sketch, x0, x1):
    """Extrude a side-plane sketch between two X positions."""
    return Pos(min(x0, x1), 0, 0) * extrude(Plane.YZ * sketch, abs(x1 - x0))


def along_x(solid, x, p):
    """Place a Z-axis cutter so its axis runs along X through side-plane point p, centred at x."""
    return Pos(x, p[0], p[1]) * Rot(0, 90, 0) * solid


def about(p, deg):
    """Location: turn about the X-parallel axis through side-plane point p."""
    return Pos(0, p[0], p[1]) * Rot(deg, 0, 0) * Pos(0, -p[0], -p[1])


def hook_sketch():
    rise = FINGER_L * math.tan(math.radians(FLARE))
    pts = [(-WALL_T, -JAW_T), (JAW_L, -JAW_T), (JAW_L, -LEAD), (JAW_L - LEAD, 0), (0, 0), (0, SLOT_W),
           (FINGER_L, SLOT_W + rise), (FINGER_L, SLOT_W + rise + FINGER_T), (-WALL_T, SLOT_W + FINGER_T)]
    return Polygon(*[add(add(HOOK, UH, s), NH, n) for s, n in pts], align=None)


def ear_sketch():
    """Bridge from bar B out to the key socket."""
    foot_on_b = add(FB, DIR_B, (KEY_C[0] - FB[0]) * DIR_B[0] + (KEY_C[1] - FB[1]) * DIR_B[1])
    return stadium(foot_on_b, KEY_C, BAR_W)


def bed_chamfer(part: Part) -> Part:
    """0.4 mm chamfer around the face that lies on the bed (the +X face of a right-hand bar)."""
    return chamfer(part.edges().group_by(Axis.X)[-1], 0.4)


# --- Parts, drawn in setting 2 for the right-hand frame (x > 0) ------------------------------------
def bar_a() -> Part:
    """Rest arm: x from FRAME_X - BAR_T to FRAME_X, socket boss on its inner face."""
    x_in = FRAME_X - BAR_T
    part = slab(stadium(FA, TA, BAR_W) + Pos(*PIVOT) * Circle(HUB_D / 2), x_in, FRAME_X)
    part += slab(foot(FA), x_in - BOSS, x_in)
    socket = clearance(TENON, "snug")
    part -= Pos(FRAME_X - (BAR_T + BOSS) / 2, FA[0], FA[1]) * Box(BAR_T + BOSS + 1, socket, socket)
    part -= along_x(Cylinder(PIVOT_D / 2, BAR_T + 1), FRAME_X - BAR_T / 2, PIVOT)
    part -= Pos(x_in, PIVOT[0], PIVOT[1]) * Rot(0, -90, 0) * nut_trap("M5", NUT_DEPTH)
    return bed_chamfer(part)


def bar_b() -> Part:
    """Hook strut: x from FRAME_X to FRAME_X + BAR_T; foot boss on its inner face, key socket on an ear."""
    x_out = FRAME_X + BAR_T
    sketch = stadium(FB, HB, BAR_W) + hook_sketch() + ear_sketch() + Pos(*PIVOT) * Circle(HUB_D / 2)
    part = slab(sketch, FRAME_X, x_out)
    part += slab(foot(FB), FRAME_X - BAR_T - BOSS, FRAME_X)
    socket = clearance(TENON, "snug")
    part -= Pos(FRAME_X - BOSS / 2, FB[0], FB[1]) * Box(2 * BAR_T + BOSS + 1, socket, socket)
    part -= Pos(FRAME_X + BAR_T / 2, KEY_C[0], KEY_C[1]) * Rot(KEY_TURN, 0, 0) * Box(BAR_T + 1, socket, socket)
    part -= along_x(Cylinder(PIVOT_D / 2, BAR_T + 1), FRAME_X + BAR_T / 2, PIVOT)
    part = bed_chamfer(part)
    depth = (CSK_D - PIVOT_D) / 2
    part -= along_x(Cone(PIVOT_D / 2, CSK_D / 2 + 0.01, depth + 0.01), x_out - depth / 2, PIVOT)
    return part


def spreader(p) -> Part:
    """Cross bar between the two feet at side-plane point p; tenons reach TENON_L into the sockets."""
    x_face = FRAME_X - BAR_T - BOSS                  # inner face of the socket bosses
    half = x_face + TENON_L
    bar = Pos(0, p[0], p[1]) * Box(2 * half, TENON, TENON)
    bar = chamfer(bar.edges().filter_by(Axis.Y) + bar.edges().filter_by(Axis.Z), 0.6)   # tenon tips
    bar = chamfer(bar.edges().filter_by(Axis.X).group_by(Axis.Z)[0], 0.4)               # bed edges
    for side in (-1, 1):
        collar = Box(COLLAR_T, COLLAR_W, TENON + COLLAR_UP, align=(Align.CENTER, Align.CENTER, Align.MIN))
        bar += Pos(side * (x_face - COLLAR_T / 2), p[0], p[1] - TENON / 2) * collar
    return bar


def key_outline() -> list:
    """Corners of the key around its peg centre. Six flats: for each setting the one that lies on bar A's
    edge, once for a right-hand and once for a left-hand frame (the two differ by STEP either side of the
    lobe), plus a back. The key is the region that never crosses bar A's edge in any of those cases."""
    r1, r2, r3 = key_radius(1), key_radius(2), key_radius(3)
    flats = [(-90 - STEP, r1), (-90 + STEP, r1), (0, r2), (90 - STEP, r3), (90 + STEP, r3), (180, r1)]
    corners = []
    for (a1, d1), (a2, d2) in zip(flats, flats[1:] + flats[:1]):
        n1, n2 = polar(a1), polar(a2)
        det = _cross(n1, n2)
        corners.append(((d1 * n2[1] - d2 * n1[1]) / det, (n1[0] * d2 - n2[0] * d1) / det))
    return corners


def key() -> Part:
    """Height key, as printed: flat cam on the bed, square peg up. The side marked 1, 2 or 3 goes against
    bar A; each flat is square to a line through the peg, so the load runs straight into the peg."""
    thick = BAR_T - KEY_GAP_X
    part = extrude(Polygon(*key_outline(), align=None), thick)
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    peg = Pos(0, 0, thick) * Box(TENON, TENON, thick, align=ON_BED)
    part += chamfer(peg.edges().group_by(Axis.Z)[-1], 0.6)
    marks = ((3, (0, key_radius(3) - 6.5)), (2, (key_radius(2) - 5.5, 0)), (1, (0, -key_radius(1) + 4.5)))
    for number, (x, y) in marks:                     # engraved on the bed face = the face you see in use
        text = mirror(label(str(number), size=NUM_SIZE, depth=NUM_H), about=Plane.YZ)
        box = text.bounding_box()
        part -= Pos(x - (box.min.X + box.max.X) / 2, y - (box.min.Y + box.max.Y) / 2, 0) * text
    return part


def key_in_place(setting: int) -> Part:
    """The key plugged into bar B's ear with lobe `setting` against bar A (drawing coordinates)."""
    seated = Plane.YZ.location * key()               # print X, Y, Z -> model Y, Z, X
    return Pos(FRAME_X - (BAR_T - KEY_GAP_X), 0, 0) * about(KEY_C, KEY_TURN + 90 * (3 - setting)) * Pos(0, *KEY_C) * seated


def assembled(setting: int = 2) -> list:
    """In-use pose: [A right, B right, key right, A left, B left, key left, front spreader, rear spreader]."""
    rel, tip, shift = pose(setting)
    world = Pos(0, *shift) * Rot(tip, 0, 0)
    on_a = world * about(PIVOT, rel)
    right = [on_a * bar_a(), world * bar_b(), world * key_in_place(setting)]
    left = [mirror(part, about=Plane.YZ) for part in right]
    return right + left + [on_a * spreader(FA), world * spreader(FB)]


def laptop(setting: int = 2, width: float = 349.3, depth: float = 240.7) -> Part:
    """Stand-in for the laptop base on the stand (for checks and renders only, never printed)."""
    corner, tilt = laptop_line(setting)
    slab_ = Box(width, depth, LAPTOP_T, align=(Align.CENTER, Align.MIN, Align.MIN))
    return Pos(0, *corner) * Rot(tilt, 0, 0) * slab_


# --- Print layout ------------------------------------------------------------------------------------
def flat(part: Part, face_down: int, axis) -> Part:
    """Lay a bar on the bed with its +X (face_down=+1) or -X (-1) face down and its long axis along Y."""
    lying = Rot(0, 90 * face_down, 0) * part
    # after the turn a side-plane direction (y, z) lies on the bed as (x, y) = (z * face_down, y)
    angle = math.degrees(math.atan2(axis[0], axis[1] * face_down))
    return Rot(0, 0, 90 - angle) * lying


def build():
    a, b = bar_a(), bar_b()
    pieces = [flat(a, +1, DIR_A), flat(b, +1, DIR_B),
              flat(mirror(a, about=Plane.YZ), -1, DIR_A), flat(mirror(b, about=Plane.YZ), -1, DIR_B),
              Rot(0, 0, 90) * spreader(FA), Rot(0, 0, 90) * spreader(FA)]
    placed, cursor = [], 0.0
    for piece in pieces:
        box = piece.bounding_box()
        placed.append(Pos(cursor - box.min.X, -(box.min.Y + box.max.Y) / 2, -box.min.Z) * piece)
        cursor += box.max.X - box.min.X + PLATE_GAP
    row_y, width = -60.0, 0.0
    for _ in range(2 + SPARE_KEYS):                  # keys in a column beside the spreaders
        piece = key()
        box = piece.bounding_box()
        placed.append(Pos(cursor - box.min.X, row_y - box.min.Y, 0) * piece)
        row_y += box.max.Y - box.min.Y + PLATE_GAP
        width = box.max.X - box.min.X
    total = cursor + width
    return [Pos(-total / 2, 0, 0) * piece for piece in placed]
