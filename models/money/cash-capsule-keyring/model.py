"""cash-capsule-keyring: screw-cap capsule (inside dia 18 x 60 mm) for a rolled emergency banknote.

Spec: body + cap with a printed 3 mm-pitch, 45 deg-flank thread (> M8, so printed threads are OK;
45 deg flanks print without supports). Waterproofing: a face O-ring sits in a groove on the body
shoulder around the thread root; the cap skirt lands on the shoulder and squeezes it ~27 %.
Keyring: flat tab at the body base with a vertical hole for a split ring. Inside: body cavity
INNER_D x (BODY_CAVITY) + cap headroom = INNER_LEN total.
Printed together: body upright, cap laid top-down beside it (parts placed for printing).

MEASURE BEFORE PRINTING: O-ring ORING_ID x ORING_CS (23 x 1.5 mm NBR) - groove is sized from these;
a rolled EUR 5-20 note (62-72 mm short side) - roll along the long side, fold once if > 60 mm.
Assumptions: thread clearances THREAD_CLEAR (radial) / THREAD_AXIAL_CLEAR suit a calibrated H2C;
ABS walls are not reliably watertight: in Bambu Studio set wall loops >= 4 for the capsule; acetone vapour
smoothing improves sealing further.
Hardware: 1x O-ring 23 x 1.5 mm NBR (ID x CS), 1x split key ring 25 mm.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # parts already placed for printing
    supports="off",
    brim="auto",
)

# Parameters
INNER_D = 18.0
INNER_LEN = 60.0
OUTER_D = 28.0
BASE_T = 2.0             # body bottom / cap top
NECK_ROOT_D = 21.2       # male thread root dia (neck wall = 1.6)
THREAD_PITCH = 3.0
THREAD_DEPTH = 1.0
THREAD_ROOT_W = 2.4      # male tooth width at root (crest = root - 2*depth -> 45 deg flanks)
THREAD_CLEAR = 0.3       # radial clearance
THREAD_AXIAL_CLEAR = 0.3 # per flank (axial)
NECK_H = 10.0
CAP_HEADROOM = 8.0       # cavity in the cap above the neck
ORING_ID = 23.0
ORING_CS = 1.5
ORING_SQUEEZE = 0.27
TAB_T = 3.0              # keyring tab thickness
TAB_L = 9.0              # tab reach beyond the body
TAB_W = 10.0
RING_HOLE_D = 4.5
EDGE = 0.4               # bed chamfer
PRINT_GAP = 6.0

BODY_CAVITY = INNER_LEN - CAP_HEADROOM
SHOULDER_Z = BASE_T + BODY_CAVITY - NECK_H
NECK_TOP = SHOULDER_Z + NECK_H
R_ROOT = NECK_ROOT_D / 2
R_MAJOR = R_ROOT + THREAD_DEPTH
R_BORE = R_MAJOR + THREAD_CLEAR                  # cap bore (female root)
R_FCREST = R_ROOT + THREAD_CLEAR                 # female crest
GROOVE_DEPTH = ORING_CS * (1 - ORING_SQUEEZE)
GROOVE_IN = ORING_ID / 2 - 0.1
GROOVE_OUT = ORING_ID / 2 + ORING_CS + 0.3
CAP_H = BASE_T + NECK_H + CAP_HEADROOM
assert GROOVE_IN >= R_BORE - 0.5 and GROOVE_OUT < OUTER_D / 2 - 0.6


def _thread(r_base: float, depth: float, w_base: float, w_crest: float, z0: float, length: float) -> Part:
    """Helical tooth from radius r_base, depth>0 outward, <0 inward; trimmed to z0..z0+length."""
    turns_h = length + 2 * THREAD_PITCH
    helix = Helix(pitch=THREAD_PITCH, height=turns_h, radius=r_base)
    s = 1 if depth > 0 else -1
    a = r_base - s * 0.2                        # sink into the wall for a clean fuse
    b = r_base + depth
    prof = Polygon((a, -w_base / 2), (b, -w_crest / 2), (b, w_crest / 2), (a, w_base / 2), align=None)
    t = sweep(Plane.XZ * prof, path=helix, is_frenet=True)
    t = Pos(0, 0, z0 - THREAD_PITCH) * t
    band = Pos(0, 0, z0) * Cylinder(r_base + abs(depth) + 2, length, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return t & band


def body() -> Part:
    b = Cylinder(OUTER_D / 2, SHOULDER_Z, align=ON_BED)
    tab = Pos(OUTER_D / 4 + TAB_L / 2, 0, 0) * Box(OUTER_D / 2 + TAB_L, TAB_W, TAB_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    tab = fillet(tab.edges().filter_by(Axis.Z).group_by(Axis.X)[-1], TAB_W / 2 - 0.01)
    b += tab
    b = chamfer(b.edges().group_by(Axis.Z)[0], EDGE)
    b -= Pos(OUTER_D / 2 + TAB_L - TAB_W / 2, 0, -1) * Cylinder(RING_HOLE_D / 2, TAB_T + 2, align=ON_BED)
    b += Pos(0, 0, SHOULDER_Z) * Cylinder(R_ROOT, NECK_H, align=ON_BED)
    b += _thread(R_ROOT, THREAD_DEPTH, THREAD_ROOT_W, THREAD_ROOT_W - 2 * THREAD_DEPTH,
                 SHOULDER_Z + 0.6, NECK_H - 1.1)
    b = chamfer(b.edges().group_by(Axis.Z)[-1], 0.4)
    b -= Pos(0, 0, BASE_T) * Cylinder(INNER_D / 2, NECK_TOP, align=ON_BED)
    # face O-ring groove on the shoulder
    b -= Pos(0, 0, SHOULDER_Z - GROOVE_DEPTH) * (Cylinder(GROOVE_OUT, GROOVE_DEPTH + 1, align=ON_BED)
                                                 - Cylinder(GROOVE_IN, GROOVE_DEPTH + 1, align=ON_BED))
    return b


def cap() -> Part:
    """Cap in use orientation (open end down at z=0)."""
    c = Cylinder(OUTER_D / 2, CAP_H, align=ON_BED)
    c = chamfer(c.edges().group_by(Axis.Z)[-1], 1.0)
    c -= Pos(0, 0, -1) * Cylinder(R_BORE, NECK_H + 1, align=ON_BED)
    c -= Cylinder(INNER_D / 2, CAP_H - BASE_T, align=ON_BED)
    w_gap_crest = THREAD_PITCH - THREAD_ROOT_W + 2 * (R_FCREST - R_ROOT)   # space between male teeth at female crest
    w_crest = w_gap_crest - 2 * THREAD_AXIAL_CLEAR
    w_base = w_crest + 2 * (R_BORE - R_FCREST)
    c += _thread(R_BORE, -(R_BORE - R_FCREST), w_base, w_crest, 0.6, NECK_H - 0.6)
    # grip flutes
    for i in range(12):
        c -= Rot(0, 0, i * 30) * Pos(OUTER_D / 2 + 0.6, 0, 2) * Cylinder(1.2, CAP_H - 4.5, align=ON_BED)
    c = chamfer(c.edges().group_by(Axis.Z)[0].filter_by(GeomType.CIRCLE).sort_by(SortBy.RADIUS)[-1:], 0.4)
    return c


def build():
    flipped = Pos(-(OUTER_D + PRINT_GAP), 0, CAP_H) * Rot(180, 0, 0) * cap()
    return [body(), flipped]
