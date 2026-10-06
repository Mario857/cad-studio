"""euro-coin-sorter: 8-tray stacking shake-sorter for all euro coins.

Spec: 8 round nesting trays (150 mm OD). Pour mixed coins into the top tray, shake: each
tray's holes are just bigger than the next-smaller coin, so every tray keeps exactly one
denomination and passes the rest down. Order top -> bottom: 2€, 50c, 1€, 20c, 5c, 10c,
2c, 1c (bottom tray has a solid floor). Each tray has a spigot under its floor that drops
into the rim of the tray below; the denomination is engraved on the outer rim.

Hole tolerances: hole Ø = (diameter of the next-smaller coin) + HOLE_MARGIN. With
HOLE_MARGIN = 0.5 mm the smaller coin passes even with a printed hole ~0.2 mm undersize,
while the kept coin is still >= 0.5 mm larger than the hole (the closest pairs, 2c/10c,
1€/50c and 20c/1€, differ by only 1.0 mm). A coin can only pass a round hole if its
diameter is smaller than the hole, whatever its tilt, so the margin is all that matters.
If a printed tray lets its own coin slip, lower HOLE_MARGIN; if the smaller coin jams,
raise it (max 0.9).

MEASURE BEFORE PRINTING (calipers, coin Ø mm): 1c 16.25, 2c 18.75, 5c 21.25, 10c 19.75,
20c 22.25, 50c 24.25, €1 23.25, €2 25.75 (thickness not critical here).

Assumptions: trays 24 mm tall (≈ 20 coins of loose depth); trays printed in two or more
plate loads (8 x 150 mm does not fit one bed) — set PRINT_TRAYS to choose which trays
go on the current plate (2 per plate: [0,1], [2,3], [4,5], [6,7]; the
committed .3mf is plate 1).
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[],
    print_orientation=(0, 0, 0),  # floor on the bed, holes vertical
    supports="off",               # the only 'support' area is the 1-2 mm letter ceilings of
                                  # the engraved rim labels: short bridges, prints clean
    brim="on",                    # large flat ABS footprint
    # 2 bodies: two trays per plate (8 x 150 mm cannot share one bed)
)

# Coin diameters (mm), top tray first: (label, coin kept on this tray, next-smaller coin)
COINS = [
    ("€2", 25.75), ("50c", 24.25), ("€1", 23.25), ("20c", 22.25),
    ("5c", 21.25), ("10c", 19.75), ("2c", 18.75), ("1c", 16.25),
]
HOLE_MARGIN = 0.5      # hole = next-smaller coin Ø + this
OD = 150.0             # tray outer diameter
WALL = 2.0             # rim wall
TRAY_H = 24.0          # tray height incl. floor
FLOOR = 2.4            # floor thickness
SPIGOT_H = 5.0         # spigot that drops into the tray below
STACK_FIT = 0.4        # radial clearance spigot <-> rim of tray below
LOW_WALL_R = 70.6      # cavity radius in the lower (thick-walled, labelled) band
LOW_BAND_TOP = 17.0    # cavity widens to the rim ID above this
RIB = 2.6              # min web between holes
TEXT_SIZE = 7.0
TEXT_DEPTH = 0.8       # engraving depth at the label centre edges (curved wall)
PRINT_TRAYS = [0, 1]   # trays on this plate (0 = top/€2 ... 7 = bottom/1c)
PLATE_GAP = 4.0


def tray(i: int) -> Part:
    r_out = OD / 2
    r_in = r_out - WALL
    r_sp = r_in - STACK_FIT
    c = SPIGOT_H + (r_out - r_sp)          # end of 45° step-out chamfer
    outer = Polygon((0, 0), (r_sp - 0.4, 0), (r_sp, 0.4), (r_sp, SPIGOT_H), (r_out, c),
                    (r_out, TRAY_H), (0, TRAY_H), align=None)
    body = revolve(Plane.XZ * outer, Axis.Z, 360)
    w = r_in - LOW_WALL_R
    cav = Polygon((0, FLOOR), (LOW_WALL_R, FLOOR), (LOW_WALL_R, LOW_BAND_TOP),
                  (r_in, LOW_BAND_TOP + w), (r_in, TRAY_H + 1), (0, TRAY_H + 1), align=None)
    body -= revolve(Plane.XZ * cav, Axis.Z, 360)

    name, _ = COINS[i]
    if i < len(COINS) - 1:
        hole = COINS[i + 1][1] + HOLE_MARGIN
        pitch = hole + RIB
        lim = LOW_WALL_R - hole / 2 - RIB
        pts = []
        row = 0
        y = 0.0
        n = int(lim // (pitch * 0.866)) + 1
        for j in range(-n, n + 1):
            y = j * pitch * 0.866
            off = (pitch / 2) if j % 2 else 0
            k = int(lim // pitch) + 2
            for m in range(-k, k + 1):
                x = m * pitch + off
                if (x * x + y * y) ** 0.5 <= lim:
                    pts.append((x, y))
        holes = [Pos(x, y, -1) * Cylinder(hole / 2, FLOOR + 2, align=ON_BED) for x, y in pts]
        body -= Part() + holes

    # engraved denomination on the front (-Y) of the thick lower band, twice
    zc = (c + LOW_BAND_TOP) / 2 + 0.5
    for rz in (0, 180):
        txt = Text(name, font_size=TEXT_SIZE, font_style=FontStyle.BOLD)
        cut = extrude(Plane.XZ.offset(r_out - TEXT_DEPTH - 0.6) * Pos(0, zc) * txt, 3)
        body -= Rot(0, 0, rz) * cut
    return body


def build():
    parts = []
    step = OD + PLATE_GAP
    for n, i in enumerate(PRINT_TRAYS):
        parts.append(Pos(0, n * step, 0) * tray(i))  # 2 trays per plate, along Y (320 mm)
    return parts
