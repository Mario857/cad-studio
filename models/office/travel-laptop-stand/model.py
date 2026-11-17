"""travel-laptop-stand: Roost-style folding travel stand for a MacBook Pro 13" and 15" (kit of 6 parts).

Function: lifts the laptop to a raised, tilted position on a desk (used with an external keyboard) and
  folds into two flat bundles + two cross bars for a bag. Indoor use, but it travels (bags, trains, a
  parked car) -> PETG: PLA softens at ~55-60 C and is too brittle for the hook fingers.
How it works (assembled, side view: Y = depth towards the screen, Z up; frames at X = +/-100):
  - Bar A (rest arm, inner): front foot on the desk, rises to the rear; its rounded top end carries the
    laptop's underside REST_S = 170 mm behind the front edge.
  - Bar B (hook strut, outer): rear foot on the desk, rises to the front; its top end is a C-hook that
    holds the laptop's front edge (slot SLOT_W) so the laptop cannot slide off or be tipped out.
  - A and B cross at one M5 pivot bolt per side. The load tries to flatten the X; a solid lug on B
    (on an ear, 34 mm from the pivot) lands on A's edge and stops it at the open angle. To fold, swing
    the bars the other way until they lie on top of each other.
  - Two identical spreaders (10 mm square tenons, snug) plug 20 mm deep into square sockets in the
    feet: front one joins the A feet, rear one the B feet. Pull them out to fold. Both pairs of socket
    bosses end at the same X (bar B's boss is longer by one bar thickness), so one spreader length fits
    both. Tenons enter from the boss side = the top of the print, away from any elephant foot.
  - Taking the laptop off: slide it ~10 mm up the slope out of the hooks, then lift. Lifting the rear
    edge first only picks the (light) stand up with it.
  - Laptop sits at 18 deg, front edge 100 mm up, rear edge ~175 mm up (15").
Print: build() is the print layout (all six parts flat on one plate, mating faces down, no supports);
  assembled() returns the in-use pose and is what the geometry is defined in.
Mechanism (docs/mechanisms.md): metal pivot bolt, not a printed pin; hard stop, no flexing parts;
  every bar printed flat so bending runs along the layers; hook finger root 5 mm (>= 3). The stop lug
  stands up from bar B, so it is loaded across its layers: see Loads.

Dimensions
  laptop 13": 304.1 x 212.4, 1.40 kg                   MEASURED (Apple spec, obj("macbook-pro-13"))
  laptop 15": 349.3 x 240.7, 1.83 kg                   MEASURED (Apple spec, obj("macbook-pro-15"))
  hook slot SLOT_W 12.0                                MEASURED (fit gauge: slot 12 goes on freely)
  pivot: M5 x 20 countersunk screw + M5 nyloc nut      MEASURED (standard; bore 5.3, csk 10.4, nut 8 AF)
  spreader tenon 10.0 in socket 10.3 (snug)            UNVERIFIED as a fit -> travel-laptop-stand-joint-coupon
  frame spacing 200, hook height 100, tilt 18 deg, bar 22 x 10: design choices, nothing mates with them
Loads (hand calculation, per side frame, 40 N total = 1.83 kg laptop + 20 N hand pressure):
  rest 14.8 N, hook 5.2 N; stop moment at the pivot 2.3 N.m -> ~66 N on the lug: 0.6 MPa shear and
  ~1.7 MPa peel across the layers on its 12 x 10 footprint (PETG layer bond is 15+ MPa); bar bending
  2.8 MPa; rest-end deflection ~0.6 mm. Side sway at 5 N: ~3 mm from bar bending (skins only, infill
  ignored) + 1-2 mm from socket play = about 5 mm.
  META force is not set: the audit's beam estimate runs on the flat print layout, where it means nothing.

Print order: travel-laptop-stand-joint-coupon first (25 min, 12 g): it proves the spreader fit and the
  pivot hardware. Only then this plate (first-print risk HIGH).

Assumptions
  - The gauge result applies to both laptops (one number was reported).
  - 2x M5 x 20 countersunk screw + 2x M5 nyloc nut are acceptable hardware; tighten until the bars
    still swing with light drag.
  - The laptop is not typed on while it is on the stand.
  - A stick-on rubber dot under each of the four feet (desk grip); not modelled.
Risks
  - Side-to-side wobble: 0.15 mm play in four 20 mm sockets is ~1 mm of sway each; if it annoys, the
    spreader tenons want a wrap of tape or a tighter fit ("press").
  - Spreaders are held by friction only and can drop out when the stand is carried assembled.
  - Bare PETG feet slide on a smooth desk without the rubber dots.
  - PETG creeps at the stop under load in a hot car: store it folded. If the lug ever lets go the X
    flattens and the laptop sinks ~70 mm; it does not fall off.
  - Hook finger (5 x 10 mm, two walls + infill) breaks if the laptop is levered up by its rear edge while
    the stand is held down.
Accept
  - Both laptops' front edges slide into the hooks with no force and cannot lift straight out.
  - 15" laptop on the stand for 30 min: front edge stays 100 +/- 5 mm above the desk.
  - 2 kg pressed on the laptop's rear edge: no collapse, feet stay down.
  - 5 N sideways push on the laptop: sway under 6 mm.
  - Folds into two bundles of about 310 x 42 x 32 mm plus two 200 mm bars; under 170 g with hardware.
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

# --- Parameters (side view: y = depth, z = height) ----------------------------------------------
TILT = 18.0              # laptop tilt (deg)
HOOK_Y = 30.0            # laptop front-bottom corner, behind the front feet
HOOK_Z = 100.0           # ... and above the desk
REST_S = 170.0           # rest point, measured along the laptop from its front edge
REAR_Y = 230.0           # rear feet behind the front feet
FOOT_Z = 11.0            # socket centre above the desk

BAR_W = 22.0             # bar width (in the side plane)
BAR_T = 10.0             # bar thickness (across): sets the sideways stiffness
FRAME_X = 100.0          # plane where bar A (inside) and bar B (outside) slide on each other
HUB_D = 26.0

SLOT_W = 12.0            # hook slot (fit gauge)
JAW_L = 16.0             # lower jaw length under the laptop
JAW_T = 6.0
WALL_T = 5.0             # wall the laptop's front edge rests against
FINGER_T = 5.0
FINGER_L = 7.0           # finger reach over the palm rest
LEAD = 1.5               # lead-in chamfers at the slot mouth

PIVOT_D = 5.3            # bore for an M5 screw with little play
CSK_D = 10.4
NUT_DEPTH = 5.5          # nyloc nut (5 mm) sits below the face; an M5 x 20 screw just passes through it

LUG_L = 12.0             # stop lug, along bar A's edge
LUG_W = 10.0
LUG_CLEAR = 1.0          # lug stays this far outside bar A when folded
LUG_GAP_X = 0.4          # lug stops short of bar A's inner face

TENON = 10.0             # spreader tenon (square)
TENON_L = 20.0
BOSS = 12.0              # socket boss on bar A's inner face (bar B's boss is BOSS + BAR_T)
FOOT_W = 24.0
FOOT_H = 22.0
COLLAR_W = 16.0
COLLAR_UP = 3.0
COLLAR_T = 4.0

PLATE_GAP = 4.0          # spacing between parts on the print plate

# --- Derived side-view geometry -------------------------------------------------------------------
_t = math.radians(TILT)
U = (math.cos(_t), math.sin(_t))          # along the laptop, front -> rear
N = (-math.sin(_t), math.cos(_t))         # out of the laptop's underside (upwards)


def add(p, q, k=1.0):
    return (p[0] + k * q[0], p[1] + k * q[1])


def unit(p, q):
    d = math.dist(p, q)
    return ((q[0] - p[0]) / d, (q[1] - p[1]) / d)


def on_laptop(s, n):
    """Point given along (s) and normal to (n) the laptop underside, from its front-bottom corner."""
    return add(add((HOOK_Y, HOOK_Z), U, s), N, n)


FA = (0.0, FOOT_Z)                              # bar A: front foot ...
TA = on_laptop(REST_S, -BAR_W / 2)              # ... to the rest end (its round end touches the laptop)
FB = (REAR_Y, FOOT_Z)                           # bar B: rear foot ...
HB = on_laptop(4.0, -BAR_W / 2 - 0.5)           # ... to just under the hook jaw
DIR_A, DIR_B = unit(FA, TA), unit(FB, HB)


def _cross(p, q):
    return p[0] * q[1] - p[1] * q[0]


_k = _cross((FB[0] - FA[0], FB[1] - FA[1]), DIR_B) / _cross(DIR_A, DIR_B)
PIVOT = add(FA, DIR_A, _k)

# Stop lug (part of B, reaching into A's plane): sits against A's lower edge on A's top side, far enough
# from B's centre line that A can fold flat over B without touching it.
_edge = (DIR_A[1], -DIR_A[0])                   # from A's centre line towards its lower edge
_off = BAR_W / 2 + LUG_W / 2
_cab, _ceb = _cross(DIR_A, DIR_B), _cross(_edge, DIR_B)
_dab = DIR_A[0] * DIR_B[0] + DIR_A[1] * DIR_B[1]
# wanted distance of the lug centre from B's centre line (the lug is turned to A's edge, so its reach
# towards B's centre line is that of a rotated rectangle)
_lat = BAR_W / 2 + LUG_CLEAR + LUG_L / 2 * abs(_cab) + LUG_W / 2 * abs(_dab)
LUG_R = max((_lat - _off * _ceb) / _cab, (-_lat - _off * _ceb) / _cab)   # distance from the pivot along A
LUG_C = add(add(PIVOT, DIR_A, LUG_R), _edge, _off)


# --- Sketch helpers (side plane: sketch x = model y, sketch y = model z) --------------------------
def stadium(p, q, width):
    mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    angle = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
    return Pos(*mid) * Rot(0, 0, angle) * SlotOverall(math.dist(p, q) + width, width)


def foot(p):
    return Pos(p[0], FOOT_H / 2) * RectangleRounded(FOOT_W, FOOT_H, 3.0)


def slab(sketch, x0, x1):
    """Extrude a side-plane sketch between two X positions."""
    return Pos(min(x0, x1), 0, 0) * extrude(Plane.YZ * sketch, abs(x1 - x0))


def along_x(solid, x, p):
    """Place a Z-axis cutter so its axis runs along X through side-plane point p, centred at x."""
    return Pos(x, p[0], p[1]) * Rot(0, 90, 0) * solid


def hook_sketch():
    top = SLOT_W + FINGER_T
    pts = [(-WALL_T, -JAW_T), (JAW_L, -JAW_T), (JAW_L, -LEAD), (JAW_L - LEAD, 0), (0, 0), (0, SLOT_W),
           (FINGER_L - LEAD, SLOT_W), (FINGER_L, SLOT_W + LEAD), (FINGER_L, top), (-WALL_T, top)]
    return Polygon(*[on_laptop(s, n) for s, n in pts], align=None)


def lug_sketch():
    angle = math.degrees(math.atan2(DIR_A[1], DIR_A[0]))
    return Pos(*LUG_C) * Rot(0, 0, angle) * Rectangle(LUG_L, LUG_W)


def ear_sketch():
    """Bridge from bar B out to the lug."""
    foot_on_b = add(FB, DIR_B, (LUG_C[0] - FB[0]) * DIR_B[0] + (LUG_C[1] - FB[1]) * DIR_B[1])
    return stadium(foot_on_b, LUG_C, LUG_L + 4.0)


def bed_chamfer(part: Part) -> Part:
    """0.4 mm chamfer around the face that lies on the bed (the +X face of a right-hand bar)."""
    return chamfer(part.edges().group_by(Axis.X)[-1], 0.4)


# --- Parts in the assembled pose (right-hand frame, x > 0) -----------------------------------------
def bar_a() -> Part:
    """Rest arm: x from FRAME_X - BAR_T to FRAME_X, socket boss on its inner face."""
    x_in = FRAME_X - BAR_T
    part = slab(stadium(FA, TA, BAR_W) + foot(FA) + Pos(*PIVOT) * Circle(HUB_D / 2), x_in, FRAME_X)
    part += slab(foot(FA), x_in - BOSS, x_in)
    socket = clearance(TENON, "snug")
    part -= Pos(FRAME_X - (BAR_T + BOSS) / 2, FA[0], FA[1]) * Box(BAR_T + BOSS + 1, socket, socket)
    part -= along_x(Cylinder(PIVOT_D / 2, BAR_T + 1), FRAME_X - BAR_T / 2, PIVOT)
    part -= Pos(x_in, PIVOT[0], PIVOT[1]) * Rot(0, -90, 0) * nut_trap("M5", NUT_DEPTH)
    return bed_chamfer(part)


def bar_b() -> Part:
    """Hook strut: x from FRAME_X to FRAME_X + BAR_T; socket boss and stop lug on its inner face."""
    x_out = FRAME_X + BAR_T
    sketch = stadium(FB, HB, BAR_W) + foot(FB) + hook_sketch() + ear_sketch() + Pos(*PIVOT) * Circle(HUB_D / 2)
    part = slab(sketch, FRAME_X, x_out)
    part += slab(foot(FB), FRAME_X - BAR_T - BOSS, FRAME_X)
    part += slab(lug_sketch(), FRAME_X - BAR_T + LUG_GAP_X, FRAME_X)
    socket = clearance(TENON, "snug")
    part -= Pos(FRAME_X - (BOSS) / 2, FB[0], FB[1]) * Box(2 * BAR_T + BOSS + 1, socket, socket)
    part -= along_x(Cylinder(PIVOT_D / 2, BAR_T + 1), FRAME_X + BAR_T / 2, PIVOT)
    depth = (CSK_D - PIVOT_D) / 2
    part = bed_chamfer(part)
    part -= along_x(Cone(PIVOT_D / 2, CSK_D / 2 + 0.01, depth + 0.01), x_out - depth / 2, PIVOT)
    return part


def spreader(y: float) -> Part:
    """Cross bar between the two feet at depth y; tenons reach TENON_L into the sockets."""
    x_face = FRAME_X - BAR_T - BOSS                  # inner face of the socket bosses
    half = x_face + TENON_L
    bar = Pos(0, y, FOOT_Z) * Box(2 * half, TENON, TENON)
    bar = chamfer(bar.edges().filter_by(Axis.Y) + bar.edges().filter_by(Axis.Z), 0.6)   # tenon tips
    bar = chamfer(bar.edges().filter_by(Axis.X).group_by(Axis.Z)[0], 0.4)               # bed edges
    for side in (-1, 1):
        collar = Box(COLLAR_T, COLLAR_W, TENON + COLLAR_UP, align=(Align.CENTER, Align.CENTER, Align.MIN))
        bar += Pos(side * (x_face - COLLAR_T / 2), y, FOOT_Z - TENON / 2) * collar
    return bar


def assembled() -> list:
    """In-use pose: [A right, B right, A left, B left, front spreader, rear spreader]."""
    a, b = bar_a(), bar_b()
    return [a, b, mirror(a, about=Plane.YZ), mirror(b, about=Plane.YZ), spreader(FA[0]), spreader(FB[0])]


def laptop(width: float = 349.3, depth: float = 240.7, thickness: float = SLOT_W - 0.6) -> Part:
    """Stand-in for the laptop base on the stand (for checks and renders only, never printed)."""
    slab_ = Box(width, depth, thickness, align=(Align.CENTER, Align.MIN, Align.MIN))
    return Pos(0, HOOK_Y, HOOK_Z) * Rot(TILT, 0, 0) * slab_


# --- Print layout ------------------------------------------------------------------------------------
def flat(part: Part, face_down: int, axis) -> Part:
    """Lay a bar on the bed with its +X (face_down=+1) or -X (-1) face down and its long axis along Y."""
    lying = Rot(0, 90 * face_down, 0) * part
    # after the turn a side-plane direction (y, z) lies on the bed as (x, y) = (z * face_down, y)
    angle = math.degrees(math.atan2(axis[0], axis[1] * face_down))
    return Rot(0, 0, 90 - angle) * lying


def build():
    a_r, b_r, a_l, b_l, front, rear = assembled()
    pieces = [flat(a_r, +1, DIR_A), flat(b_r, +1, DIR_B), flat(a_l, -1, DIR_A), flat(b_l, -1, DIR_B),
              Rot(0, 0, 90) * front, Rot(0, 0, 90) * rear]
    placed, cursor = [], 0.0
    for piece in pieces:
        box = piece.bounding_box()
        placed.append(Pos(cursor - box.min.X, -(box.min.Y + box.max.Y) / 2, -box.min.Z) * piece)
        cursor += box.max.X - box.min.X + PLATE_GAP
    total = cursor - PLATE_GAP
    return [Pos(-total / 2, 0, 0) * piece for piece in placed]
