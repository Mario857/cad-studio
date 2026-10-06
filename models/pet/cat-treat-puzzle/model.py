"""cat-treat-puzzle: puzzle feeder for dry treats - 6 wells, rotating disc + 3 sliding covers.

Spec: low, wide round base (210 mm at the bed, 200 mm body, 30 mm tall) with 6 treat wells:
- 3 inner wells (26 mm, r = 30 mm) under a rotating disc (104 mm, 5 mm) that has ONE opening;
  the cat spins the disc (paw in the opening) to reach the next well. The disc sits in a 3 mm
  pocket on a 14 mm centre pin and is held by a 36 mm press-fit knob (pull the knob to wash).
- 3 outer wells (26 mm, r = 76 mm) under sliding covers that run in 45 deg dovetail tracks
  tangential to the base; the cat paws the raised ridge to slide a cover off its well. Tracks
  are open at the outer end so covers can be slid out for washing (closed end = stop).
Parts (6 separate bodies by design, printed together, laid out flat on one plate): base, disc,
3 covers, knob.

Use: DRY TREATS ONLY (no wet food). Wash by hand in warm soapy water - not dishwasher safe.
Pet safety: ABS must not hold food/water directly and is not a chew toy - only dry treats,
supervise use, discard if chewed or cracked. All features >= 2 mm, cat-touched edges filleted,
bed edges 0.4 mm chamfer. Anti-tip: 30 mm tall on a 210 mm footprint.

Fits (params): disc on pin and in pocket DISC_FIT (loose, spins freely with treat dust),
covers in tracks SLIDE_FIT per side, knob on pin KNOB_FIT (press).
Assumptions: treats ~10 mm kibble-size (wells 26 mm wide, 16-18 mm deep); a cat can pull a
cover fully out of the open track end - just slide it back in; the knob may be glued for a
permanent disc if the press fit loosens.
"""

import math

from build123d import *

from cadlib import *

# Parameters (mm)
BASE_R_BED = 105.0      # footprint radius (anti-tip flare)
BASE_R = 100.0          # body radius
BASE_H = 30.0
FLARE_H = 8.0           # height of the flare cone
TOP_FILLET = 4.0
WELL_D = 26.0
WELL_BOTTOM_R = 4.0     # rounded well bottom (easy cleaning)
INNER_R = 30.0          # inner well ring radius
INNER_DEPTH = 18.0      # from pocket floor
OUTER_R = 76.0          # outer well ring radius
OUTER_DEPTH = 16.0      # from track floor
INNER_ANGLES = (90.0, 210.0, 330.0)
OUTER_ANGLES = (30.0, 150.0, 270.0)

DISC_R = 52.0
DISC_T = 5.0
POCKET_DEPTH = 3.0
DISC_OPENING_D = 30.0
DISC_FIT = 0.4          # radial play: disc in pocket / on pin
PIN_D = 14.0
PIN_ABOVE_DISC = 11.0   # pin length above disc top (knob engages it)
KNOB_D = 36.0
KNOB_H = 20.0
KNOB_HOLE_DEPTH = 9.0     # straight part; 45 deg cone ceiling above (support-free)
KNOB_FIT = 0.10         # press

TRACK_DEPTH = 6.0
TRACK_TOP_W = 30.0      # slot opening at the top
TRACK_FLOOR_W = TRACK_TOP_W + 2 * TRACK_DEPTH   # 45 deg dovetail
TRACK_BACK = 22.0       # closed end, behind the well centre
SLIDE_FIT = 0.4         # play per side, cover in track
COVER_L = 40.0
COVER_H = 5.0           # slider height (1 mm below the base top)
RIDGE_W = 24.0
RIDGE_L = 5.0
RIDGE_H = 4.0           # above slider top -> 3 mm proud of the base

TOP = BASE_H
DISC_Z0 = TOP - POCKET_DEPTH

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(BASE_R, 0, BASE_H), grams=1500)],  # cat paw leaning on the rim
    print_orientation="auto",
    supports="auto",
    brim="auto",
)

# plate layout (parts printed together, H2C bed 300 x 320)
DISC_AT = (130.0, 150.0)
KNOB_AT = (-80.0, 140.0)
COVERS_AT = ((135.0, -80.0), (135.0, -30.0), (135.0, 20.0))


def _well(x, y, z_top, depth):
    w = Pos(x, y, z_top - depth) * Cylinder(WELL_D / 2, depth + 1, align=ON_BED)
    return fillet(w.edges().group_by(Axis.Z)[0], WELL_BOTTOM_R)


def _base() -> Part:
    prof = Polygon(
        (0, 0), (BASE_R_BED - 0.4, 0), (BASE_R_BED, 0.4), (BASE_R, FLARE_H), (BASE_R, TOP), (0, TOP),
        align=None,
    )
    base = revolve(Plane.XZ * prof, Axis.Z, 360)
    base = fillet(base.edges().group_by(Axis.Z)[-1], TOP_FILLET)

    # disc pocket + pin
    base -= Pos(0, 0, DISC_Z0) * Cylinder(DISC_R + DISC_FIT, POCKET_DEPTH + 1, align=ON_BED)
    base += Pos(0, 0, DISC_Z0) * Cylinder(PIN_D / 2, POCKET_DEPTH + DISC_T + PIN_ABOVE_DISC, align=ON_BED)

    for a in INNER_ANGLES:
        r = math.radians(a)
        base -= _well(INNER_R * math.cos(r), INNER_R * math.sin(r), DISC_Z0, INNER_DEPTH)

    # tracks: local frame well at (0, OUTER_R), slide along +X, open end runs out of the base
    exit_t = math.sqrt(BASE_R_BED**2 - OUTER_R**2) + 10
    hw_t, hw_f = TRACK_TOP_W / 2, TRACK_FLOOR_W / 2
    tprof = Polygon(
        (OUTER_R - hw_f, TOP - TRACK_DEPTH), (OUTER_R + hw_f, TOP - TRACK_DEPTH),
        (OUTER_R + hw_t, TOP), (OUTER_R + hw_t, TOP + 5), (OUTER_R - hw_t, TOP + 5),
        (OUTER_R - hw_t, TOP),
        align=None,
    )
    track = extrude(Plane.YZ.offset(-TRACK_BACK) * tprof, TRACK_BACK + exit_t)
    track += _well(0, OUTER_R, TOP - TRACK_DEPTH, OUTER_DEPTH)
    for a in OUTER_ANGLES:
        base -= Rot(0, 0, a - 90) * track
    return base


def _disc() -> Part:
    d = Cylinder(DISC_R, DISC_T, align=ON_BED)
    d -= Cylinder(PIN_D / 2 + DISC_FIT, 3 * DISC_T)
    d -= Pos(INNER_R, 0, 0) * Cylinder(DISC_OPENING_D / 2, 3 * DISC_T)
    d = fillet(d.edges().group_by(Axis.Z)[-1], 1.5)
    d = chamfer(d.edges().group_by(Axis.Z)[0], 0.4)
    return d


def _cover() -> Part:
    # dovetail slider, X = slide direction
    hb = TRACK_FLOOR_W / 2 - SLIDE_FIT
    ht = hb - COVER_H  # 45 deg
    prof = Polygon((-hb, 0), (hb, 0), (ht, COVER_H), (-ht, COVER_H), align=None)
    c = extrude(Plane.YZ.offset(-COVER_L / 2) * prof, COVER_L)
    ridge = Pos(0, 0, COVER_H - 0.5) * Box(RIDGE_L, RIDGE_W, RIDGE_H + 0.5, align=ON_BED)
    ridge = fillet(ridge.edges().group_by(Axis.Z)[-1], 2.0)
    c += ridge
    c = chamfer(c.edges().group_by(Axis.Z)[0], 0.4)
    return c


def _knob() -> Part:
    k = Cylinder(KNOB_D / 2, KNOB_H, align=ON_BED)
    k = fillet(k.edges().group_by(Axis.Z)[-1], 4.0)
    k = chamfer(k.edges().group_by(Axis.Z)[0], 0.4)
    hr = (PIN_D + 2 * KNOB_FIT) / 2
    k -= Pos(0, 0, -1) * Cylinder(hr, KNOB_HOLE_DEPTH + 1, align=ON_BED)
    k -= Pos(0, 0, KNOB_HOLE_DEPTH) * Cone(hr, 0.5, hr - 0.5, align=ON_BED)
    return k


def build():
    parts = [_base(), Pos(*DISC_AT, 0) * _disc(), Pos(*KNOB_AT, 0) * _knob()]
    parts += [Pos(x, y, 0) * _cover() for x, y in COVERS_AT]
    return parts
