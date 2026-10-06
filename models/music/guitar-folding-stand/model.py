"""guitar-folding-stand: folding A-frame floor stand for acoustic and electric guitars.

Spec
- Two leg frames hinged on one M6 threaded rod at the apex (pivot). The FRONT frame carries
  the guitar: two cradle arms with front lips (bodies 40-120 mm deep) and a back rest on the
  upper rails; the REAR frame is a U-frame that folds forward flat against the front frame
  for gigs (rear rails sit just outside the front rails, so nothing collides when folded).
- Guitar leans back 15 deg = front-frame tilt, so the body back lies flat on the rail pads
  and the bottom edge sits square on the cradle (cradle surface is perpendicular to the rails).
- Every guitar-contact surface (cradle tops, lip inner faces, upper rail faces) has >= 1.5 mm
  fillets and a 1.5 mm recess for 3 mm self-adhesive FELT (or cork) pads, so the guitar only
  ever touches felt. Use felt, NOT rubber/foam: some rubbers and vinyls react with
  nitrocellulose lacquer finishes and leave permanent marks.
- Both frames print together, assembled and open, in use orientation (one plate, ~231 x 300 x
  262 mm). They are separate bodies with HINGE_GAP between them at the pivot; after printing
  push the rod through. Floor-protection felt can go under the runners.
- Strength / orientation: printed upright. The guitar weight (~40 N) goes from the cradle arms
  straight down into the floor runners they sit on (pure compression, no cantilever), the rails
  are near-vertical columns in compression and the back-rest reaction (~10 N) gives < 2 MPa
  bending in the rails. Cradle arms, gussets (rib) and runners have the load in-plane with
  layers; nothing load-bearing hangs on interlayer tension.

Hardware
- 1x M6 threaded rod, 250 mm (stainless), 2x M6 hex nuts (inside the front rails), 2x M6 wing
  nuts + 2x M6 washers outside the rear rails (tool-free fold; snug the wing nuts for friction).
- Felt: 2x 14x110 mm cradle pads, 2x 14x14 mm lip pads, 2x 14x90 mm rail pads, 3 mm thick.
- Anti-splay cord: ~0.6 m of 3-4 mm paracord through the two CORD_D holes in the front-frame
  rear cross bar and rear-frame cross bar, knotted so the frames open to the design angle.

Assumptions
- Guitar <= 4 kg, COM ~300 mm up the body from the bottom edge, mid-depth.
- Body widths >= 250 mm (cradle arms 170 mm apart); hard floor (cord takes the splay thrust).
- Fit sizes: rod hole M6 + FIT loose (teardrop, support-free), hinge side gap 0.8 mm.
"""

from math import atan2, cos, degrees, radians, sin, tan

from build123d import *

from cadlib import *

# ---------------- Parameters ----------------
PIVOT_H = 250.0         # hinge axis height
FRONT_TILT = 15.0       # front frame lean from vertical (= guitar lean)
REAR_TILT = 15.0        # rear frame lean from vertical
RAIL_W = 20.0           # rail size along X
RAIL_D = 18.0           # rail size across its plane
RAIL_R = 2.0            # rail edge fillet
FRONT_X = 85.0          # front rail centre |x|
HINGE_GAP = 0.8         # X gap between front and rear rails (print-in-place clearance)
ROD_D = 6.0             # M6 threaded rod
ROD_HOLE = clearance(ROD_D, "loose")

RUNNER_H = 10.0         # floor runner / cross bar height
CROSS_W = 15.0          # cross bar width (Y)
CORD_D = 5.0            # anti-splay cord holes
CORD_X = 40.0

CRADLE_Z = 45.0         # cradle surface height at the rail face
CRADLE_DEPTH = 128.0    # rail face -> lip (bodies up to 120 mm + felt)
LIP_H = 20.0
LIP_T = 9.0
CONTACT_R = 1.5         # fillet on guitar-contact edges (>= 1 mm)

FELT_T = 1.5            # felt recess depth (3 mm felt stands 1.5 mm proud)
FELT_W = 14.0
CRADLE_FELT_L = 110.0
RAIL_FELT_L = 90.0
RAIL_FELT_S = 75.0      # rail pad centre, distance below pivot along rail

CHEV_S = 150.0          # chevron foot, distance below pivot along rail
CHEV_ANG = 50.0         # chevron angle in frame plane (keeps overhang < 45 deg)
CHEV_W = 14.0
CHEV_D = 12.0
CHEV_SET = 4.0          # chevron front face set back from rail face (no guitar contact)

GUSSET_L = 45.0
GUSSET_H = 60.0
GUSSET_T = 12.0

REAR_RUN_L = 55.0       # rear runner length behind the rear rail foot
GUITAR_G = 4000
GUITAR_COM_UP = 300.0   # along the guitar from its bottom edge
GUITAR_COM_FWD = 60.0   # in front of the rail face (mid-depth of a 120 mm body)

# ---------------- Derived geometry (Y forward = -Y, Z up) ----------------
P = Vector(0, 0, PIVOT_H)
_f, _r = radians(FRONT_TILT), radians(REAR_TILT)
UF = Vector(0, -sin(_f), -cos(_f))      # down the front rail
NF = Vector(0, -cos(_f), sin(_f))       # front-frame front normal
UR = Vector(0, sin(_r), -cos(_r))       # down the rear rail
NR = Vector(0, cos(_r), sin(_r))        # rear-frame back normal
REAR_X = FRONT_X + RAIL_W + HINGE_GAP   # rear rail centre |x|

T_FRONT = PIVOT_H / cos(_f)             # pivot -> floor along rails
T_REAR = PIVOT_H / cos(_r)


def on_rail(t, off=0.0, x=0.0, u=UF, n=NF):
    return Vector(x, 0, 0) + P + u * t + n * off


# cradle: rail face point at CRADLE_Z
_t0 = (PIVOT_H + (RAIL_D / 2) * NF.Z - CRADLE_Z) / cos(_f)
Q0 = on_rail(_t0, RAIL_D / 2)
GUITAR_COM = Q0 + NF * GUITAR_COM_FWD - UF * GUITAR_COM_UP

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="Guitar Core ABS+ 0.20mm @BBL H2C",
    standing=True,
    loads=[dict(at=(0.0, round(GUITAR_COM.Y, 1), round(GUITAR_COM.Z, 1)), grams=GUITAR_G)],
    print_orientation=(0, 0, 0),   # upright: cradle load = compression into runners
    supports="auto",
    brim="auto",
    notes="2 bodies intended: front + rear frame print together, hinged after print by M6 rod",
)


def bar(a: Vector, b: Vector, w, d, n: Vector, r=RAIL_R):
    """Box from a to b, size w (local X) x d (along n), long edges filleted."""
    axis = b - a
    L = axis.length
    z = axis.normalized()
    x = n.cross(z).normalized()
    box = fillet(Box(w, d, L).edges().filter_by(Axis.Z), r)
    return Plane(origin=(a + b) * 0.5, x_dir=x, z_dir=z) * box


def floor_box(x0, x1, y0, y1, h=RUNNER_H):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, 0) * rounded_box(x1 - x0, y1 - y0, h, radius=2)


def pad_cut(center: Vector, normal: Vector, along: Vector, length, width=FELT_W, slope_top=False):
    """Felt recess cutter; slope_top bevels the upper wall 45 deg (no flat ceiling)."""
    x = normal.cross(along).normalized()
    box = Box(width, length, 2 * FELT_T)
    if slope_top:  # local -Y = +along end, deep side = -Z
        e = box.edges().filter_by(Axis.X).group_by(Axis.Y)[0].sort_by(Axis.Z)[0]
        box = chamfer(e, FELT_T * 0.99)
    return Plane(origin=center, x_dir=x, z_dir=normal) * box


def yz_prism(pts, x0, x1):
    return extrude(Plane.YZ.offset(x0) * Polygon(*pts, align=None), amount=x1 - x0)


def front_frame():
    parts = []
    lip_front_y = None
    for sx in (-1, 1):
        x = sx * FRONT_X
        x0, x1 = x - RAIL_W / 2, x + RAIL_W / 2
        # rail: pivot cap -> into the runner
        a = on_rail(0, 0, x)
        b = on_rail(T_FRONT - 5, 0, x)
        rail = bar(a, b, RAIL_W, RAIL_D, NF)
        rail += Pos(x, P.Y, P.Z) * Rot(0, 90, 0) * Cylinder(RAIL_D / 2, RAIL_W)
        parts.append(rail)
        # cradle arm (YZ profile)
        L0 = Q0 + NF * CRADLE_DEPTH
        L1 = L0 - UF * LIP_H
        L2 = L1 + NF * LIP_T
        prof = [(Q0.Y + 6, 0), (Q0.Y + 6, Q0.Z - 6), (Q0.Y, Q0.Z), (L0.Y, L0.Z),
                (L1.Y, L1.Z), (L2.Y, L2.Z), (L2.Y, 0)]
        # offset of a slimmer prism = every exposed edge rounded with CONTACT_R
        arm = offset(yz_prism(prof, x0 + CONTACT_R, x1 - CONTACT_R), CONTACT_R)
        arm = arm & Pos(x, 0, 0) * Box(RAIL_W, 600, 300, align=(Align.CENTER, Align.CENTER, Align.MIN))
        lip_front_y = arm.bounding_box().min.Y
        # felt recesses: cradle top and lip inner face
        top_c = Q0 + NF * (CRADLE_DEPTH / 2 - 2) + Vector(x, 0, 0)
        arm -= pad_cut(top_c, -UF, NF, CRADLE_FELT_L)
        lip_c = L0 - UF * (LIP_H / 2 + 6) + Vector(x, 0, 0)  # runs out over the lip top
        arm -= pad_cut(lip_c, -NF, -UF, LIP_H)
        parts.append(arm)
        # side runner under rail + arm, gusset behind the rail foot
        foot_y = on_rail(T_FRONT, 0).Y
        parts.append(floor_box(x0, x1, lip_front_y, foot_y + RAIL_D / 2 + GUSSET_L + 5))
        gy = on_rail((PIVOT_H - RUNNER_H) / cos(_f), -RAIL_D / 2 + 3).Y
        parts.append(Pos(x, gy, RUNNER_H - 1) * Rot(0, 0, 90)
                     * rib(GUSSET_L, GUSSET_H, GUSSET_T))
    # chevron brace (in frame plane, set back from guitar)
    off = RAIL_D / 2 - CHEV_SET - CHEV_D / 2
    s_apex = CHEV_S - FRONT_X * tan(radians(CHEV_ANG))
    apex = on_rail(s_apex, off, 0)
    for sx in (-1, 1):
        foot = on_rail(CHEV_S, off, sx * FRONT_X)
        parts.append(bar(foot, apex + Vector(sx * CHEV_W / 2, 0, 0), CHEV_W, CHEV_D, NF))
    # cross bars on the floor
    xw = FRONT_X + RAIL_W / 2
    parts.append(floor_box(-xw, xw, lip_front_y, lip_front_y + CROSS_W))
    foot_y = on_rail(T_FRONT, 0).Y
    yb = foot_y + RAIL_D / 2 + GUSSET_L + 5
    parts.append(floor_box(-xw, xw, yb - CROSS_W, yb))
    frame = parts[0]
    for p in parts[1:]:
        frame += p
    # felt recess on the rail faces (back rest)
    for sx in (-1, 1):
        frame -= pad_cut(on_rail(RAIL_FELT_S, RAIL_D / 2, sx * FRONT_X), NF, -UF, RAIL_FELT_L,
                         slope_top=True)
    for sx in (-1, 1):
        frame -= Pos(sx * CORD_X, yb - CROSS_W / 2, RUNNER_H) * pin_hole(CORD_D, RUNNER_H + 1)
    return frame


def rear_frame():
    parts = []
    foot_y = on_rail(T_REAR, 0, 0, UR, NR).Y
    y_end = foot_y + REAR_RUN_L
    for sx in (-1, 1):
        x = sx * REAR_X
        x0, x1 = x - RAIL_W / 2, x + RAIL_W / 2
        a = on_rail(0, 0, x, UR, NR)
        b = on_rail(T_REAR - 5, 0, x, UR, NR)
        rail = bar(a, b, RAIL_W, RAIL_D, NR)
        rail += Pos(x, P.Y, P.Z) * Rot(0, 90, 0) * Cylinder(RAIL_D / 2, RAIL_W)
        parts.append(rail)
        y0 = foot_y - RAIL_D / 2 - GUSSET_L - 5
        parts.append(floor_box(x0, x1, y0, y_end))
        # gusset inside the A (front side of the rear rail)
        gy = on_rail((PIVOT_H - RUNNER_H) / cos(_r), -RAIL_D / 2 + 3, 0, UR, NR).Y
        parts.append(Pos(x, gy, RUNNER_H - 1) * Rot(0, 0, -90)
                     * rib(GUSSET_L, GUSSET_H, GUSSET_T))
        gz = RUNNER_H + GUSSET_H
        # back gusset (behind the rail)
        gyb = on_rail((PIVOT_H - gz) / cos(_r), RAIL_D / 2 - 3, 0, UR, NR).Y
        parts.append(Pos(x, gyb, RUNNER_H - 1) * Rot(0, 0, 90)
                     * rib(y_end - CROSS_W - gyb, GUSSET_H, GUSSET_T))
    xw = REAR_X + RAIL_W / 2
    parts.append(floor_box(-xw, xw, y_end - CROSS_W, y_end))
    frame = parts[0]
    for p in parts[1:]:
        frame += p
    for sx in (-1, 1):
        frame -= Pos(sx * CORD_X, y_end - CROSS_W / 2, RUNNER_H) * pin_hole(CORD_D, RUNNER_H + 1)
    return frame


def build():
    rod = Pos(0, P.Y, P.Z) * teardrop_hole(ROD_HOLE, 2 * (REAR_X + RAIL_W), along="X")
    return [front_frame() - rod, rear_frame() - rod]
