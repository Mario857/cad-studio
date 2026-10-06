"""piggy-bank: geometric low-poly piggy bank with €2 coin slot and screw-out bottom plug.

Spec: ~144 x 104 x 95 mm faceted pig. The body is a ruled loft of gable-shaped sections, so
every face is flat (low-poly look) and every inside ceiling is >= 50° from horizontal: it
prints hollow, upright, with no supports. Four hexagonal feet stand on the bed with the flat
belly. Coin slot on the back ridge takes €2 coins (25.75 x 2.20). A cup-shaped plug with a
coarse 45°-flank thread (P5, 40 mm major) screws into a boss in the belly; turn it with a
coin in the cross slot. Emptying hole 37 mm clear.

MEASURE BEFORE PRINTING: €2 coin 25.75 mm diameter, 2.20 mm thick (SLOT_L / SLOT_W).
Assumptions: radial thread clearance THREAD_CLEAR suits ABS at 0.2 mm layers; if tight,
raise it 0.1. Supports off: the ~3 cm2 the audit lists are thread run-out ledges, 4 mm nostril
tops and 3.2 mm coin-slot bridges, all fine unsupported. 2 bodies = pig + plug (intended). Capacity ~0.6 l (≈ €1000 in €2 coins). Plug printed alongside (flange down).
"""

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm.
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(-5, 0, 20), grams=600)],   # coins pile on the belly
    print_orientation="auto",
    supports="off",
    brim="auto",
)

# Body: (x station, half-width, height); bottom flat = BELLY * half-width
STATIONS = [(-72, 22, 55), (-48, 40, 84), (-5, 46, 95), (32, 42, 88), (55, 28, 64)]
BELLY = 0.6
ROOF = 1.19                 # roof rise per unit run (tan 50°)
WALL = 2.4

# Snout / ears / eyes
SNOUT_L = 17.0
SNOUT_Z = 30.0
EAR_X = 18.0
EAR_Y = 18.0
EAR_T = 3.0
EYE_D = 5.0

# Feet
FOOT_R = 11.0
FOOT_H = 20.0
FEET = [(-45, 32), (-45, -32), (30, 32), (30, -32)]

# Coin slot (€2)
SLOT_X = -15.0
SLOT_L = 29.0
SLOT_W = 3.4

# Bottom plug + thread
PLUG_X = -5.0
THREAD_D = 40.0             # plug major diameter
THREAD_P = 5.0
THREAD_H = 1.6              # thread depth (45° flanks)
THREAD_L = 12.0
THREAD_CLEAR = 0.4          # radial
FLANGE_D = 50.0
FLANGE_T = 3.0
RECESS_CLEAR = 0.3          # radial, flange in recess
PLUG_WALL = 2.4
BOSS_D = 54.0


def section(w, h):
    wb = BELLY * w
    z1 = h - ROOF * w
    return Polygon((-wb, 0), (wb, 0), (w, w - wb), (w, z1), (0, h), (-w, z1), (-w, w - wb), align=None)


def thread(r_root, length, outward=True):
    d = THREAD_H
    if outward:
        pts = ((r_root - 0.3, -d - 0.3), (r_root + d, 0), (r_root - 0.3, d + 0.3))
    else:
        pts = ((r_root + 0.3, -d - 0.3), (r_root - d, 0), (r_root + 0.3, d + 0.3))
    ridge = sweep(Plane.XZ * Polygon(*pts, align=None),
                  path=Helix(pitch=THREAD_P, height=length + 2 * THREAD_P, radius=r_root), is_frenet=True)
    ridge = Pos(0, 0, -THREAD_P) * ridge
    keep = Cylinder(r_root + d + 1, length, align=ON_BED)
    return ridge & keep


def build_pig():
    outer = loft([Plane.YZ.offset(x) * section(w, h) for x, w, h in STATIONS], ruled=True)
    xs = [x for x, _, _ in STATIONS]
    xs[0] += WALL * 1.5
    xs[-1] -= WALL * 1.5
    inner = loft([Plane.YZ.offset(xi) * offset(section(w, h), -WALL) for xi, (_, w, h) in zip(xs, STATIONS)],
                 ruled=True)

    x5, w5, h5 = STATIONS[-1]
    snout = Polygon((-8, 12), (8, 12), (13, 5), (13, -3), (0, -16), (-13, -3), (-13, 5), align=None)
    body = outer + Pos(x5 + SNOUT_L / 2 - 0.5, 0, SNOUT_Z) * extrude(Plane.YZ * snout, (SNOUT_L + 1) / 2, both=True)
    for y in (-EAR_Y, EAR_Y):
        ear = Polygon((EAR_X - 10, 58), (EAR_X + 6, 58), (EAR_X - 4, 84), align=None)
        body += Pos(0, y, 0) * extrude(Plane.XZ * ear, EAR_T / 2, both=True)
    for fx, fy in FEET:
        f = Pos(fx, fy, 0) * extrude(RegularPolygon(FOOT_R, 6), FOOT_H)
        body += chamfer(f.edges().group_by(Axis.Z)[0], 0.4)
    body -= inner

    # nostrils + eyes
    for y in (-5, 5):
        body -= Pos(x5 + SNOUT_L, y, SNOUT_Z + 1) * (Rot(0, 90, 0) * Cylinder(2, 6))
    for y in (-7, 7):
        body -= Pos(x5 + 0.5, y, 48) * (Rot(0, -90, 0) * Cone(EYE_D / 2, 0.6, 2.5, align=ON_BED))

    # coin slot through the ridge
    body -= Pos(SLOT_X, 0, 200) * Box(SLOT_L, SLOT_W, 200, align=(Align.CENTER, Align.CENTER, Align.MAX))

    # belly boss with internal thread
    rr = FLANGE_D / 2 + RECESS_CLEAR
    r_nut = THREAD_D / 2 + THREAD_CLEAR
    z_thr = FLANGE_T + (rr - r_nut)
    boss_h = z_thr + THREAD_L + 2
    p = Pos(PLUG_X, 0, 0)
    body += p * Cylinder(BOSS_D / 2, boss_h, align=ON_BED)
    body -= p * Pos(0, 0, -1) * Cylinder(r_nut, boss_h + 2, align=ON_BED)
    body -= p * Pos(0, 0, -1) * Cylinder(rr, FLANGE_T + 1, align=ON_BED)
    body -= p * Pos(0, 0, FLANGE_T) * Cone(rr, r_nut, rr - r_nut, align=ON_BED)
    body += p * Pos(0, 0, z_thr) * thread(r_nut, THREAD_L, outward=False)
    return body


def build_plug():
    r_core = THREAD_D / 2 - THREAD_H
    rf = FLANGE_D / 2
    cone_h = rf - THREAD_D / 2
    plug = Cylinder(rf, FLANGE_T, align=ON_BED)
    plug = chamfer(plug.edges().group_by(Axis.Z)[0], 0.4)
    plug += Pos(0, 0, FLANGE_T) * Cone(rf, THREAD_D / 2, cone_h, align=ON_BED)
    top = FLANGE_T + cone_h + THREAD_L
    plug += Cylinder(r_core, top, align=ON_BED)
    plug += Pos(0, 0, FLANGE_T + cone_h + 0.6) * thread(r_core, THREAD_L - 0.6, outward=True)
    plug -= Pos(0, 0, FLANGE_T) * Cylinder(r_core - PLUG_WALL, top, align=ON_BED)
    for a in (0, 90):
        plug -= Rot(180, 0, 0) * (Rot(0, 0, a) * slot(26, 3.2, 1.5))
    return plug


def build():
    return [build_pig(), Pos(0, 85, 0) * build_plug()]
