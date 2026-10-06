"""shower-corner-caddy: 90 deg wall-corner shower shelf for 3 shampoo bottles.

Spec: two back walls (wall A in plane x=0, wall B in plane y=0) meet at 90 deg in the corner
(origin). Square shelf (SHELF x SHELF) with the far corner rounded (CORNER_R), 10 mm lip on the
two free sides, floor sloped ~1.5 deg down toward the far corner, drain slots across the whole
floor, a drain notch through the lip at the lowest point. Three triangular gussets under the
shelf, perpendicular to wall A. Mount: 2 countersunk screws per wall, both ABOVE the shelf
(they take the tension of the cantilever moment; the walls below the shelf bear in compression
on the tiles, so no lower screws are needed). Back faces are flat and unbroken except the
screw holes, so VHB/adhesive pads can be used instead of screws.

Drainage: floor top slopes down along the corner diagonal; slots every SLOT_PITCH mm cover
the floor; lip notch at the far corner; lip inner side is a 45 deg ramp and wall tops have
inner 45 deg chamfers, so no ledge can hold water; everything under the shelf is open.
Slots have 45 deg pointed ends (support-free in the print pose).

Print orientation (0, -90, 0): printed lying on wall A's back face. Reasoning:
- the shelf-to-wall-B joint, wall B and the whole shelf plane are then vertical in the
  printer, so the cantilever bending from wall B and wall bending along Z run along layers;
  wall A lies flat on the bed and is strong in every in-plane direction.
- the shelf outline (square + rounded corner) only has upward/vertical faces in this pose,
  the gussets are vertical plates whose sloped edge faces up, slots are vertical slits with
  rounded tops, so it prints with NO supports. Upright (as used) would need supports under
  the entire shelf; the corner-up 45 deg pose puts the diagonal cantilever stress across
  layers.
- the remaining weak direction (shelf-to-wall-A, stress across layers) is carried by three
  60 mm deep gussets: 1.5 kg at the front edge gives < 1 MPa in them, far below ABS layer
  strength (~15 MPa).

Assumptions: bottles <= 75 mm dia (3 fit: one in the corner, one along each wall);
M4 countersunk wood screws + 6 mm wall plugs (or 4 adhesive pads ~ 40x40 mm);
tiles are flat and the room corner is 90 deg.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[dict(at=(150, 150, 60), grams=1500)],
    print_orientation=(0, -90, 0),  # lying on wall A back face, see docstring
    supports="auto",
    brim="auto",
)

# Parameters
SHELF = 170.0          # shelf extent along each wall (from the corner, outer)
CORNER_R = 70.0        # rounding of the far corner
WALL_T = 5.0           # back wall thickness
WALL_UP = 40.0         # wall height above the floor (at the corner)
RIB_H = 60.0           # gusset depth below the floor at the wall
RIB_T = 4.0            # gusset thickness
RIB_Y = (48.0, 98.0, 145.0)  # gusset positions along wall A
FLOOR_T = 4.0          # floor thickness
SLOPE_DEG = 1.5        # floor slope toward the far corner
LIP_H = 10.0           # lip height above floor
LIP_T = 3.0            # lip thickness
TOP_CHAMFER = 2.0      # inner 45 deg chamfer on wall/lip tops (no flat ledges)
SLOT_W = 4.0           # drain slot width
SLOT_PITCH = 9.0       # drain slot row pitch
SLOT_SEG = 42.0        # max slot length (ties between segments keep slats stiff)
SLOT_TIE = 6.0         # tie width between slot segments
NOTCH_W = 12.0         # drain notch in lip at the lowest corner
NOTCH_H = 4.0
SCREW = "M4"           # countersunk screw size
SCREW_UP = 22.0        # screw height above floor top at the wall
SCREW_POS = (45.0, 125.0)  # screw positions along each wall from the corner
EF = 0.4               # elephant-foot chamfer on the bed face

Z_F = RIB_H + FLOOR_T  # floor top at the corner (walls bottom at z=0)
S = math.tan(math.radians(SLOPE_DEG))


def floor_top(x, y):
    return Z_F - S * (x + y) / math.sqrt(2)


def plane_at(dz):
    """Plane parallel to the floor top, offset dz vertically."""
    n = Vector(S / math.sqrt(2), S / math.sqrt(2), 1).normalized()
    return Plane(origin=(0, 0, Z_F + dz), z_dir=n)


def x_max(y):
    """Outer shelf edge x at a given y."""
    c = SHELF - CORNER_R
    if y <= c:
        return SHELF
    return c + math.sqrt(max(CORNER_R**2 - (y - c) ** 2, 0))


def outline():
    c = SHELF - CORNER_R
    sq = Pos(SHELF / 2, SHELF / 2) * Rectangle(SHELF, SHELF)
    cut = Pos(c + CORNER_R / 2 + 1, c + CORNER_R / 2 + 1) * Rectangle(CORNER_R + 2, CORNER_R + 2)
    return sq - cut + Pos(c, c) * Circle(CORNER_R)


def drain_slot(length, width, depth):
    """Slot cutter (long axis X) with 45 deg pointed ends: prints support-free when X is up."""
    h = width / 2
    a = length / 2
    pr = Polygon((-a, 0), (-a + h, h), (a - h, h), (a, 0), (a - h, -h), (-a + h, -h), align=None)
    c = extrude(pr, depth)
    return Pos(0, 0, -c.bounding_box().max.Z) * c


def prism(sk, z0, z1):
    return Pos(0, 0, z0) * extrude(sk, z1 - z0)


def wall(length):
    """Wall profile in XZ (thickness along +X), extruded along +Y."""
    top = Z_F + WALL_UP
    prof = Polygon((0, 0), (WALL_T, 0), (WALL_T, top - TOP_CHAMFER),
                   (WALL_T - TOP_CHAMFER, top), (0, top), align=None)
    w = extrude(Plane.XZ * prof, -length)
    return w


def build() -> Part:
    ol = outline()
    drop = S * 2 * SHELF / math.sqrt(2) + 2
    # floor slab (uniform thickness, sloped) + gussets trimmed to the floor top
    slab = prism(ol, Z_F - FLOOR_T - drop - 1, Z_F + 1)
    slab = split(slab, bisect_by=plane_at(0), keep=Keep.BOTTOM)
    slab = split(slab, bisect_by=plane_at(-FLOOR_T), keep=Keep.TOP)
    ribs = Part()
    for c in RIB_Y:
        xe = x_max(c) - LIP_T
        zb = floor_top(xe, c) - FLOOR_T
        tri = Polygon((0, Z_F - FLOOR_T - RIB_H), (0, Z_F + 1), (xe, Z_F + 1), (xe, zb), align=None)
        ribs += Pos(0, c + RIB_T / 2, 0) * extrude(Plane.XZ * tri, RIB_T)
    ribs = split(ribs, bisect_by=plane_at(-1), keep=Keep.BOTTOM)
    under = slab + ribs

    # lip ring on the outline, top parallel to floor
    ring = ol - offset(ol, -LIP_T)
    # built flat (inner face 45 deg so it prints without support), then tilted with the floor
    zb = -FLOOR_T - 1
    outer = extrude(ol, LIP_H - zb)
    inner = loft([Plane.XY * offset(ol, -(LIP_T + LIP_H)),
                  Plane.XY.offset(LIP_H) * offset(ol, -LIP_T)])
    flat = Pos(0, 0, zb) * outer - inner
    flat -= extrude(offset(ol, -(LIP_T + LIP_H)), LIP_H + 1)
    axis = Axis((0, 0, 0), (1, -1, 0))
    lip = Pos(0, 0, Z_F) * flat.rotate(axis, -SLOPE_DEG)  # far corner down
    lip &= prism(ol, 0, Z_F + LIP_H + 5)
    lip = split(lip, bisect_by=plane_at(-FLOOR_T), keep=Keep.TOP)

    wall_a = wall(SHELF)
    wall_b = mirror(wall(SHELF), about=Plane(origin=(0, 0, 0), z_dir=(1, -1, 0)))
    part = under + lip + wall_a + wall_b

    # drain slots: rows along X, avoiding gussets
    cutters = []
    y = WALL_T + 2 + SLOT_W / 2
    while y < SHELF - LIP_T - 2 - SLOT_W / 2:
        if all(abs(y - c) > RIB_T / 2 + SLOT_W / 2 + 1.0 for c in RIB_Y) and y + SLOT_W / 2 < x_max(y):
            x0 = WALL_T + 3
            x1 = min(x_max(y - SLOT_W / 2), x_max(y + SLOT_W / 2)) - LIP_T - 2.5
            n = max(1, math.ceil((x1 - x0 + SLOT_TIE) / (SLOT_SEG + SLOT_TIE)))
            seg = (x1 - x0 - (n - 1) * SLOT_TIE) / n
            stagger = (int(y / SLOT_PITCH) % 2) * 0.0
            for i in range(n):
                xs = x0 + stagger + i * (seg + SLOT_TIE)
                if seg > SLOT_W + 1:
                    zc = floor_top(xs + seg / 2, y) + 3
                    cutters.append(Pos(xs + seg / 2, y, zc) * drain_slot(seg, SLOT_W, FLOOR_T + 8))
        y += SLOT_PITCH
    for ct in cutters:
        part -= ct

    # drain notch through the lip at the lowest (far) corner
    c = SHELF - CORNER_R
    d = c / math.sqrt(2) * math.sqrt(2) + CORNER_R / math.sqrt(2)
    zn = floor_top(d, d)
    notch = Pos(d, d, zn - 1.0) * Rot(0, 0, 45) * Box(2 * (LIP_T + LIP_H) + 8, NOTCH_W, NOTCH_H + 1,
                                                      align=(Align.CENTER, Align.CENTER, Align.MIN))
    part -= notch

    # countersunk screw holes, heads on the inner faces
    for p in SCREW_POS:
        za = floor_top(WALL_T, p) + SCREW_UP
        part -= at(WALL_T, p, za, 0, 90, 0) * bolt_hole(SCREW, WALL_T + 2, head="csk")
        zb = floor_top(p, WALL_T) + SCREW_UP
        part -= at(p, WALL_T, zb, -90, 0, 0) * bolt_hole(SCREW, WALL_T + 2, head="csk")

    # elephant foot on the face that sits on the bed (wall A back face)
    try:
        part = chamfer(part.faces().sort_by(Axis.X)[0].edges(), EF)
    except Exception:
        pass
    return part
