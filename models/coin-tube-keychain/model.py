"""coin-tube-keychain: screw-cap keychain tube for 5 x €2 (or 5 x €1) trolley/parking coins.

Spec: a cup-shaped body with a coarse external thread on its neck and a keyring lug at the
bottom, plus a screw cap with the matching internal thread, flush with the body. Thread:
single start, 3.5 mm pitch, 1.2 mm deep, 45° flanks (support-free both ways), ~2 turns.
Grip flutes on the cap. Body prints upright, cap prints top-down (both open side up).

Fits: bore = €2 Ø + BORE_CLEAR (€1 coins also fit); thread radial clearance THREAD_CLEAR;
keyring hole KEYRING_D.

MEASURE BEFORE PRINTING (calipers, Ø / thickness mm): €2 25.75/2.20, €1 23.25/2.33.

Assumptions: 5 coins of the thickest kind (€1, 2.33 mm) + 0.6 mm headroom; standard split
keyring up to 1.5 mm wire.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="auto",
    # 2 bodies intended: body + cap (cap shown top-down, as printed)
)

COIN_D = 25.75         # €2
COIN_T = 2.33          # thickest of €1/€2
COUNT = 5
BORE_CLEAR = 0.6
HEADROOM = 0.6
WALL = 1.6
FLOOR = 1.6
PITCH = 3.5
THREAD_DEPTH = 1.2
THREAD_CREST = 0.4
THREAD_CLEAR = 0.3     # radial
NECK_L = 8.0
CAP_TOP = 1.6
CAP_WALL = 1.6
FLUTES = 18
FLUTE_R = 0.9
LUG_L = 9.0            # lug beyond the body
LUG_W = 11.0
LUG_T = 4.0
KEYRING_D = 4.5
PRINT_GAP = 6.0


def thread(r_root, depth, pitch, z0, z1, external=True):
    """45° trapezoid thread swept on a helix, clipped to z0..z1 (45° cone at the bottom so
    the thread start has no flat underside)."""
    base = 2 * depth + THREAD_CREST
    s = 1 if external else -1
    pts = [(r_root - s * 0.3, -base / 2), (r_root, -base / 2), (r_root + s * depth, -THREAD_CREST / 2),
           (r_root + s * depth, THREAD_CREST / 2), (r_root, base / 2), (r_root - s * 0.3, base / 2)]
    length = (z1 - z0) + 2 * pitch
    th = sweep(Plane.XZ * Polygon(*pts, align=None), path=Helix(pitch, length, r_root), is_frenet=True)
    th = Pos(0, 0, z0 - pitch) * th
    a, b = r_root - s * 1, r_root + s * (depth + 1)
    keep = Polygon((a, z0 - 1), (b, z0 + depth + 1), (b, z1), (a, z1), align=None)
    return th & revolve(Plane.XZ * keep, Axis.Z, 360)


def build():
    bore = COIN_D + BORE_CLEAR
    r_root = bore / 2 + WALL                    # body neck / thread root
    r_crest = r_root + THREAD_DEPTH
    rc_root = r_crest + THREAD_CLEAR            # cap internal root
    r_out = rc_root + CAP_WALL                  # body + cap outer radius
    h = FLOOR + COUNT * COIN_T + HEADROOM       # body height (rim)
    zn = h - NECK_L                             # shoulder

    body = Cylinder(r_out, zn, align=ON_BED) + Cylinder(r_root, h, align=ON_BED)
    lug = Pos(r_out, 0, 0) * (Box(LUG_L * 2, LUG_W, LUG_T, align=ON_BED)
                              + Pos(LUG_L, 0, 0) * Cylinder(LUG_W / 2, LUG_T, align=ON_BED))
    lug -= Pos(r_out + LUG_L, 0, -1) * Cylinder(KEYRING_D / 2, LUG_T + 2, align=ON_BED)
    body += lug
    body = chamfer(body.edges().group_by(Axis.Z)[0], 0.4)
    body += thread(r_root - 0.01, THREAD_DEPTH, PITCH, zn + 0.8, h - 0.6)
    body -= Pos(0, 0, FLOOR) * Cylinder(bore / 2, h, align=ON_BED)
    body = chamfer(body.edges().group_by(Axis.Z)[-1].filter_by(GeomType.CIRCLE), 0.4)

    cap_h = CAP_TOP + NECK_L + 0.3
    cap = Cylinder(r_out, cap_h, align=ON_BED)
    cap = chamfer(cap.edges().group_by(Axis.Z)[0], 0.6)
    cap -= Pos(0, 0, CAP_TOP) * Cylinder(rc_root, cap_h, align=ON_BED)
    cap += thread(rc_root + 0.01, THREAD_DEPTH, PITCH, CAP_TOP + 0.6, cap_h - 0.3, external=False)
    for i in range(FLUTES):
        cap -= Rot(0, 0, i * 360 / FLUTES) * Pos(r_out + 0.3, 0, 1.2) * Cylinder(FLUTE_R, cap_h, align=ON_BED)
    cap = Pos(-(r_out * 2 + PRINT_GAP), 0, 0) * cap
    return [body, cap]
