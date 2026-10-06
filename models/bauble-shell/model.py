"""bauble-shell: 70 mm Christmas ornament ball, two snap-together halves + hanging cap.

Spec:
- Ball outer diameter BALL_D = 70 mm, wall WALL = 1.6 mm. Split at the equator.
- Each half prints open side up (as a bowl) with no supports. Below 45 deg latitude the sphere
  would overhang more than 45 deg, so each pole is a 45 deg tangent cone (onion/finial look).
  Bottom half ends in a flat (BOTTOM_FLAT_D) that sits on the bed; top half ends in a neck
  (NECK_D x NECK_H) that sits on the bed and carries the cap.
- Decorative cut-outs: two staggered rings of diamond windows per half (12 large + 12 small),
  cut radially. Diamond edges are at 45 deg and the radial cut tilts downward-outward in the
  bowl orientation, so every window ceiling is <= 45 deg from vertical -> self-supporting.
- Snap joint: bottom half has an inner lip (LIP_T wall, LIP_H tall) with a 45 deg triangular bead;
  top half has a thickened band with a bore + matching groove. Inner ledges use 45 deg chamfers.
- Cap: cup that slides over the neck (CAP_FIT diametral clearance), 45 deg conical inside
  ceiling (no bridge), flat tab with a teardrop ribbon hole (LOOP_HOLE_D) on top.
  Prints rim down.
- Parts are returned already in print orientation (bottom half, top half flipped, cap):
  3 separate bodies on one plate is intended (mesh WARN expected).

Assumptions:
- "70 mm ball" = 70 mm equator diameter; poles are 45 deg cones for support-free printing,
  so assembled height is ~89 mm + cap.
- Bead interference 0.2 mm radial is enough to hold the halves; ABS flexes enough to assemble.
- Cap is friction fit on the neck; a drop of glue makes it permanent if wanted.
- Ribbon/hook through a 3.5 mm hole.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # parts are modelled in print orientation (halves bowl-up)
    supports="off",
    brim="auto",
)

# Ball
BALL_D = 70.0
R = BALL_D / 2
WALL = 1.6
POLE_T = 2.0            # floor thickness at the bottom flat / above the neck
BOTTOM_FLAT_D = 16.0    # bed flat of the bottom half

# Neck + cap (top half)
NECK_D = 12.0
NECK_H = 4.0
CAP_FIT = 0.15          # diametral clearance cap cup over neck (friction)
CAP_D = 17.0
CAP_SEAT_GAP = 0.3      # cup is deeper than the neck so the rim seats on the ball
CAP_TOP_D = 6.0
LOOP_W = 9.0
LOOP_T = 3.0
LOOP_HOLE_D = 3.5

# Snap joint
BORE_R = 31.6           # bore radius in the top-half band
BORE_DEPTH = 5.0
SNAP_CLEAR = 0.15       # radial clearance lip-to-bore
LIP_T = 1.6
LIP_H = 4.5
BEAD = 0.35             # bead protrusion on lip (radial)
GROOVE = 0.45           # groove depth in bore (radial)
BEAD_Z = 2.5            # bead height above equator

# Cut-outs
RING1_LAT = 20.0        # deg below equator (bowl orientation)
RING1_D = 10.0          # diamond diagonal
RING2_LAT = 38.0
RING2_D = 7.0
N_HOLES = 12

GAP = 10.0              # spacing on the plate
CHAMFER = 0.4

S2 = math.sqrt(2)


def _cone_band(r_tip_dist, z_low, z_high):
    """45 deg cone around Z whose apex is at z=-r_tip_dist, between z_low and z_high (<0)."""
    r_low = r_tip_dist + z_low
    r_high = r_tip_dist + z_high
    return Pos(0, 0, z_low) * Cone(r_low, r_high, z_high - z_low,
                                   align=(Align.CENTER, Align.CENTER, Align.MIN))


def _lower_half(r, z_flat):
    """Sphere radius r + tangent 45 deg cone, truncated at z_flat, below z=0."""
    tip = r * S2
    body = Sphere(r) + _cone_band(tip, z_flat, -r / S2)
    keep = Pos(0, 0, z_flat) * Box(4 * R, 4 * R, -z_flat, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return body & keep


def _revolve(pts):
    return revolve(Plane.XZ * Polygon(*pts, align=None), Axis.Z, 360)


def _diamond(d, lat, az):
    side = d / S2
    cutter = Rot(45, 0, 0) * Box(10, side, side)
    return Rot(0, 0, az) * Rot(0, lat, 0) * Pos(R, 0, 0) * cutter


def _windows():
    cuts = None
    for i in range(N_HOLES):
        a = 360 / N_HOLES * i
        for c in (_diamond(RING1_D, RING1_LAT, a), _diamond(RING2_D, RING2_LAT, a + 180 / N_HOLES)):
            cuts = c if cuts is None else cuts + c
    return cuts


def _ledge(r_in, z_vert_bottom):
    """Material ring from r_in outward, flat top at z=0, vertical to z_vert_bottom, then 45 deg."""
    d = R + 2 - r_in
    return _revolve([(r_in, 0), (R + 2, 0), (R + 2, z_vert_bottom - d),
                     (r_in, z_vert_bottom)])


def _chamfer_bottom(p):
    try:
        return chamfer(p.edges().group_by(Axis.Z)[0], CHAMFER)
    except Exception:
        return p


def bottom_half():
    z_flat = -(R * S2 - BOTTOM_FLAT_D / 2)
    outer = _lower_half(R, z_flat)
    inner = _lower_half(R - WALL, z_flat + POLE_T)
    lip_ro = BORE_R - SNAP_CLEAR
    lip_ri = lip_ro - LIP_T
    shell = outer - inner
    shell = shell + (_ledge(lip_ri, 0) & outer)
    lip = _revolve([(lip_ri, 0), (lip_ro, 0), (lip_ro, BEAD_Z - BEAD), (lip_ro + BEAD, BEAD_Z),
                    (lip_ro, BEAD_Z + BEAD), (lip_ro, LIP_H), (lip_ri, LIP_H)])
    shell = shell + lip
    shell = shell - _windows()
    shell = Pos(0, 0, -z_flat) * shell
    return _chamfer_bottom(shell)


def top_half():
    # Print orientation: bowl up, neck on the bed.
    z_neck_top = -(R * S2 - NECK_D / 2)
    z_neck_bot = z_neck_top - NECK_H
    outer = _lower_half(R, z_neck_top) + Pos(0, 0, z_neck_bot) * Cylinder(
        NECK_D / 2, NECK_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    inner = _lower_half(R - WALL, z_neck_top + POLE_T)
    shell = outer - inner
    shell = shell + (_ledge(BORE_R, -BORE_DEPTH) & outer)
    groove = _revolve([(BORE_R - 0.5, -BEAD_Z - GROOVE), (BORE_R, -BEAD_Z - GROOVE),
                       (BORE_R + GROOVE, -BEAD_Z), (BORE_R, -BEAD_Z + GROOVE), (BORE_R - 0.5, -BEAD_Z + GROOVE)])
    shell = shell - groove
    shell = shell - _windows()
    shell = Pos(0, 0, -z_neck_bot) * shell
    return _chamfer_bottom(shell)


def cap():
    r_out = CAP_D / 2
    r_in = (NECK_D + CAP_FIT) / 2
    cup_depth = NECK_H + CAP_SEAT_GAP
    cyl_h = cup_depth + 1.0
    cone_h = r_out - CAP_TOP_D / 2
    body = Cylinder(r_out, cyl_h, align=ON_BED)
    body += Pos(0, 0, cyl_h) * Cone(r_out, CAP_TOP_D / 2, cone_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    top_z = cyl_h + cone_h
    hole_z = top_z + LOOP_W / 2
    tab_bot = cyl_h + 2.5
    body += Pos(0, 0, tab_bot) * Box(LOOP_W, LOOP_T, hole_z - tab_bot,
                                     align=(Align.CENTER, Align.CENTER, Align.MIN))
    body += Pos(0, 0, hole_z) * Rot(90, 0, 0) * Cylinder(LOOP_W / 2, LOOP_T)
    body -= Pos(0, 0, hole_z) * teardrop_hole(LOOP_HOLE_D, LOOP_T + 2, along="Y")
    hollow = Cylinder(r_in, cup_depth, align=ON_BED)
    hollow += Pos(0, 0, cup_depth) * Cone(r_in, 0.01, r_in, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body -= Pos(0, 0, -0.01) * hollow
    return _chamfer_bottom(body)


def build():
    off = R + GAP / 2
    return [
        Pos(-off, 0, 0) * bottom_half(),
        Pos(off, 0, 0) * top_half(),
        Pos(0, R + GAP + CAP_D / 2, 0) * cap(),
    ]
