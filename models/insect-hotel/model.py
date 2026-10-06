"""insect-hotel: solitary-bee / insect hotel frame that holds natural nesting tubes.

Spec: gabled box ~180 W x 150 H x 145 D (box 160 wide, 125 deep + 20 mm roof overhang). The
45° pitched roof overhangs the front by ROOF_OVERHANG and the sides by EAVE, keeping rain off
the tube ends. Inside, two diamond lattices (front, 12 mm deep; back, 10 mm deep) hold
bamboo or paper tubes Ø6-8 mm x 120 mm by their ends; bees nest only inside the natural tubes,
never in plastic. The lattices start DRAIN_GAP above a slotted floor so water drains away and
the lowest tubes stay dry. A keyhole hanger in the back wall (behind a solid boss) hangs it on
a screw.
Prints upright as used: the 45° roof/eaves and the 45° diamond cells need no supports.
Material: AzureFilm ABS PLUS. ABS+ yellows/embrittles after a season or two in full sun; the
user's "AzureFilm ASA @BBL H2C 0.4 nozzle" preset is the long-life swap (same geometry).

Assumptions:
- Diamond cell inscribed size CELL = 8.6 mm (8 mm tube + clearance; 6 mm tubes sit loosely).
  Partial cells at the edges are left open (fill them with short tubes or leave empty).
- Tubes: 120 mm long, interior depth TUBE_LEN + 1 mm.
- Hang from one Ø4-5 mm pan-head screw (head ≤ Ø9 mm) in a fence/wall, facing south-east.
- Not free-standing (wall-hung).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),   # upright as used
    supports="off",
    brim="auto",
    copies=1,
)

BOX_W = 160.0
WALL_H = 66.0          # side wall height (roof springs from here)
WALL = 2.0
FLOOR_T = 2.4
BACK_T = 2.4
TUBE_LEN = 120.0
ROOF_T = 2.4
EAVE = 10.0
ROOF_OVERHANG = 20.0
CELL = 8.6             # diamond cell inscribed size
LATTICE_WALL = 1.4
FRONT_LATTICE = 12.0
BACK_LATTICE = 10.0
DRAIN_GAP = 8.0
DRAIN_SLOT_W = 4.0
DRAIN_PITCH = 16.0
KEYHOLE_HEAD_D = 10.0
KEYHOLE_SLOT_W = 5.0
KEYHOLE_TRAVEL = 12.0
KEYHOLE_Z = WALL_H + 30.0

B = BOX_W / 2
DEPTH = TUBE_LEN + 1 + BACK_T
S2 = math.sqrt(2)


def gable(half_w: float, z0: float, wall_h: float, ridge: float) -> Sketch:
    """Pentagon in XZ: floor at z0, side walls to wall_h, 45° gable up to the ridge height."""
    return Polygon((-half_w, z0), (half_w, z0), (half_w, wall_h), (0, ridge), (-half_w, wall_h), align=None)


def diamond_lattice(region: Sketch) -> Sketch:
    pitch = CELL + LATTICE_WALL
    holes = None
    n = int(400 / pitch)
    hole = Rot(0, 0, 45) * Rectangle(CELL, CELL)
    pts = []
    for i in range(-n, n):
        for j in range(-n, n):
            x = (i + j) * pitch / S2
            z = (i - j) * pitch / S2
            if abs(x) < B + 10 and -5 < z < WALL_H + B + 10:
                pts.append((x, z))
    holes = Locations(*pts) * hole
    # bottom edge: zigzag through cell centres, so every lattice strip ends in a 45° point
    # (no flat underside) at least DRAIN_GAP above the floor
    h = pitch / S2
    k = math.ceil((FLOOR_T + DRAIN_GAP) / h)
    zig = [(-B - 4 * h, -10.0)]
    m0 = -int((B + 3 * h) / h)
    if (m0 - k) % 2:
        m0 -= 1
    for m in range(m0, -m0 + 2):
        zig.append((m * h, (k + (m - k) % 2) * h))
    zig.append((zig[-1][0], -10.0))
    return region - holes - Polygon(*zig, align=None)


def build() -> Part:
    ridge_in = WALL_H + B                      # roof underside ridge (45° from the outer wall top)
    outer = gable(B, 0, WALL_H, ridge_in)
    inner = gable(B - WALL, FLOOR_T, WALL_H - WALL * (S2 - 1), ridge_in - WALL * S2)   # wall-thick offset
    body = extrude(Plane.XZ * outer, DEPTH, dir=(0, 1, 0))
    body -= Pos(0, -1, 0) * extrude(Plane.XZ * inner, DEPTH - BACK_T + 1, dir=(0, 1, 0))

    # roof slab (with eaves and front overhang); underside = 45° gable lines
    rt = ROOF_T * S2
    e = B + EAVE
    roof = Polygon((-e, ridge_in - e), (0, ridge_in), (e, ridge_in - e), (e, ridge_in - e + rt),
                   (0, ridge_in + rt), (-e, ridge_in - e + rt), align=None)
    body += Pos(0, -ROOF_OVERHANG, 0) * extrude(Plane.XZ * roof, DEPTH + ROOF_OVERHANG, dir=(0, 1, 0))
    body = chamfer(body.edges().group_by(Axis.Z)[0], 0.4)

    # drain slots in the floor
    nslots = int((BOX_W - 2 * WALL - 10) // DRAIN_PITCH)
    for k in range(nslots):
        x = (k - (nslots - 1) / 2) * DRAIN_PITCH
        body -= Pos(x, 10, -1) * Box(DRAIN_SLOT_W, DEPTH - BACK_T - 20, FLOOR_T + 2,
                                     align=(Align.CENTER, Align.MIN, Align.MIN))

    # tube lattices (start DRAIN_GAP above the floor)
    region = gable(B - WALL + 0.2, FLOOR_T, WALL_H - WALL * (S2 - 1) + 0.2, ridge_in - WALL * S2 + 0.2)
    lat = diamond_lattice(region)
    body += extrude(Plane.XZ * lat, FRONT_LATTICE, dir=(0, 1, 0))
    body += Pos(0, DEPTH - BACK_T - BACK_LATTICE, 0) * extrude(Plane.XZ * lat, BACK_LATTICE + 0.5, dir=(0, 1, 0))

    # keyhole boss behind the back wall: 45° underside, pocket for the screw head
    yb = DEPTH - BACK_T
    boss_d = 6.0
    zb0, zb1 = KEYHOLE_Z - KEYHOLE_HEAD_D, KEYHOLE_Z + KEYHOLE_TRAVEL + KEYHOLE_HEAD_D
    boss = Polygon((yb + 0.5, zb0 - boss_d - 1), (yb - boss_d, zb0), (yb - boss_d, zb1), (yb + 0.5, zb1),
                   align=None)
    body += extrude(Plane.YZ * boss, 15, both=True)
    pocket = Pos(0, 0, KEYHOLE_Z) * (Circle(KEYHOLE_HEAD_D / 2 + 0.3)
                                     + Pos(0, KEYHOLE_TRAVEL / 2) * Rectangle(KEYHOLE_HEAD_D + 0.6, KEYHOLE_TRAVEL)
                                     + Pos(0, KEYHOLE_TRAVEL) * Circle(KEYHOLE_HEAD_D / 2 + 0.3))
    body -= Pos(0, yb - 4.5, 0) * extrude(Plane.XZ * pocket, 4.5, dir=(0, 1, 0))
    slot = Pos(0, 0, KEYHOLE_Z) * (Circle(KEYHOLE_HEAD_D / 2 + 0.3)
                                   + Pos(0, KEYHOLE_TRAVEL / 2) * Rectangle(KEYHOLE_SLOT_W, KEYHOLE_TRAVEL)
                                   + Pos(0, KEYHOLE_TRAVEL) * Circle(KEYHOLE_SLOT_W / 2))
    body -= Pos(0, yb - 1, 0) * extrude(Plane.XZ * slot, BACK_T + 2, dir=(0, 1, 0))
    return body
