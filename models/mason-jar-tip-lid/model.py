"""mason-jar-tip-lid: two-piece regular-mouth mason jar lid with note + coin slots and TIPS.

Spec: like a canning lid, a threaded band clamps a flat insert disk onto the jar rim.
  - BAND: internal 45°-flank thread (2 turns) for a regular-mouth (70 mm) jar, inward top
    flange that holds the disk, vertical grip ribs. Prints flange-down, no supports.
  - DISK: 70 mm insert, 2.6 mm thick, banknote slot (folded note) + €2 coin slot, raised
    "TIPS" between them. Prints flat with the text up, so the text is truly raised.
Two pieces avoid a 70 mm unsupported ceiling and keep the text crisp.

MEASURE BEFORE PRINTING: jar glass thread major diameter (JAR_THREAD_D, ~70 mm on regular
mouth), thread pitch (JAR_PITCH, ~4.23 mm = 6 TPI), €2 coin 25.75 x 2.20 (COIN_SLOT_*).
Assumptions: glass thread depth ~1.6 mm; THREAD_CLEAR radial 0.5 mm covers glass tolerance.
Banknote slot 50 x 4 mm takes a note folded to ~1/4 width. 2 bodies (intended).
Supports off: only the clipped thread-start ledges (~1 cm2) face down.
"""

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm. Parts laid out side by side in print orientation.
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation="auto",
    supports="off",
    brim="auto",
)

# Jar (regular mouth)
JAR_THREAD_D = 70.0         # glass thread major diameter
JAR_PITCH = 4.23
THREAD_DEPTH = 1.6
THREAD_CLEAR = 0.5          # radial
THREAD_TURNS = 2.0

# Band
BAND_WALL = 2.4
FLANGE_T = 2.4
FLANGE_ID = 62.0
BAND_H = 14.0
GRIP_N = 36
GRIP_W = 1.6
GRIP_H = 1.0

# Disk
DISK_FIT = 0.5              # diametral, disk in band bore
DISK_T = 2.6
NOTE_SLOT_L = 50.0
NOTE_SLOT_W = 4.0
COIN_SLOT_L = 29.0
COIN_SLOT_W = 3.4
SLOT_OFFSET = 15.0          # slot centrelines from disk centre (Y)
TEXT = "TIPS"
TEXT_SIZE = 10.0
TEXT_RAISE = 0.6

R_ROOT = JAR_THREAD_D / 2 + THREAD_CLEAR      # band thread root radius (bore)
R_OUT = R_ROOT + BAND_WALL


def thread_in(r_root, length):
    d = THREAD_DEPTH
    pts = ((r_root + 0.3, -d - 0.3), (r_root - d, 0), (r_root + 0.3, d + 0.3))   # 45° flanks
    ridge = sweep(Plane.XZ * Polygon(*pts, align=None),
                  path=Helix(pitch=JAR_PITCH, height=length + 2 * JAR_PITCH, radius=r_root), is_frenet=True)
    return (Pos(0, 0, -JAR_PITCH) * ridge) & Cylinder(r_root + 1, length, align=ON_BED)


def build_band():
    """modelled in print orientation: flange on the bed (in use it is on top)"""
    band = Cylinder(R_OUT, BAND_H, align=ON_BED) - Cylinder(R_ROOT, BAND_H, align=ON_BED)
    band += Cylinder(R_OUT, FLANGE_T, align=ON_BED) - Pos(0, 0, -1) * Cylinder(FLANGE_ID / 2, FLANGE_T + 2, align=ON_BED)
    band = chamfer(band.edges().group_by(Axis.Z)[0], 0.4)
    for i in range(GRIP_N):
        band += Rot(0, 0, i * 360 / GRIP_N) * Pos(R_OUT - 0.4, 0, 0) * Box(2 * GRIP_H, GRIP_W, BAND_H - 1.5, align=ON_BED)
    z0 = FLANGE_T + DISK_T + 0.6
    tl = min(THREAD_TURNS * JAR_PITCH, BAND_H - z0 - 0.5)
    band += Pos(0, 0, z0) * thread_in(R_ROOT, tl)
    return band


def build_disk():
    r = (2 * R_ROOT - DISK_FIT) / 2
    disk = Cylinder(r, DISK_T, align=ON_BED)
    disk = chamfer(disk.edges().group_by(Axis.Z)[0], 0.4)
    disk -= Pos(0, SLOT_OFFSET, DISK_T + 1) * Box(NOTE_SLOT_L, NOTE_SLOT_W, DISK_T + 2, align=(Align.CENTER, Align.CENTER, Align.MAX))
    disk -= Pos(0, -SLOT_OFFSET, DISK_T + 1) * Box(COIN_SLOT_L, COIN_SLOT_W, DISK_T + 2, align=(Align.CENTER, Align.CENTER, Align.MAX))
    t = label(TEXT, size=TEXT_SIZE, depth=TEXT_RAISE + 0.2)
    bb = t.bounding_box()
    disk += Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, DISK_T - 0.2) * t
    return disk


def build():
    return [build_band(), Pos(2 * R_OUT + 10, 0, 0) * build_disk()]
