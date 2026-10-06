"""star-tree-topper: faceted 5-point Christmas star with a cone sleeve for the tree tip.

Spec: 150 mm wide 5-point star, 25 mm thick, every face bevelled to a central ridge
(classic faceted star). A hollow cone sleeve underneath slides over a tree tip of
10-25 mm diameter.

Print strategy (zero supports): the star is split along its mid-plane into two identical
halves, each printed flat on its back face with the bevels facing up. A half-round neck
boss at the bottom inner vertex carries a diamond (45 deg roof) groove; glued together the
two grooves form a square socket. The sleeve prints upright in its in-use orientation
(wide opening down, 6.8 deg cone walls, 45 deg inner cone tip) and has a square peg on
top that plugs into the socket. Three 1.75 mm filament dowels align the halves.
build() returns the print layout (two halves + sleeve), not the assembled star, so the
mesh check's "3 separate bodies" WARN is intended.

Assembly: glue halves back to back with 3 filament dowels (9.5 mm long) in the pin holes,
then push/glue the sleeve peg into the socket.

Assumptions:
- "150 mm across" = width between the two side tips; tip radius = 150/2/cos(18 deg).
- Inner/outer radius ratio 0.382 (regular pentagram); top flat 12 % of outline.
- Tree tips taper, so the sleeve is a 9->28 mm ID cone 80 mm long; it wedges wherever
  the tip diameter matches.
- Square peg/socket with snug fit; glue recommended for permanence.
- Alignment pins are 1.75 mm filament scraps (no bought hardware).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,            # sits on a tree tip, not free-standing
    loads=[],
    print_orientation=(0, 0, 0),  # parts are modelled already laid out for printing
    supports="off",
    brim="auto",
)

# Star
STAR_WIDTH = 150.0                     # side tip to side tip
STAR_THICK = 25.0                      # total, both halves
R_OUT = STAR_WIDTH / 2 / math.cos(math.radians(18))
R_IN = R_OUT * 0.382
TOP_SCALE = 0.12                       # size of flat top relative to outline
BASE_H = 1.5                           # vertical rim under the bevel
HALF_T = STAR_THICK / 2
EDGE_CHAMFER = 0.4                     # elephant foot

# Neck boss + socket (in each half, along -Y = down in use)
BOSS_R = 9.0
BOSS_DROP = 10.0                       # boss sticks out below the bottom inner vertex
BOSS_END = -8.0                        # y where boss ends inside the star
PEG = 8.0                              # square peg side
PEG_LEN = 20.0
SOCKET_CLR = FIT["snug"]               # per side
SOCKET_SIDE = PEG + 2 * SOCKET_CLR
SOCKET_DEPTH = PEG_LEN + 1.0

# Alignment dowels (1.75 mm filament)
DOWEL_D = 1.75
DOWEL_DEPTH = 5.0                      # per half
DOWEL_RADIUS = 32.0                    # on the tip rays at 90, 162, 18 deg

# Sleeve
SLEEVE_LEN = 80.0
SLEEVE_ID_BOT = 28.0
SLEEVE_ID_TOP = 9.0
SLEEVE_WALL = 2.4
SLEEVE_TOP_OD = 14.0
SLEEVE_CAP = 3.0                       # solid above the inner cone tip

# Layout
GAP = 8.0


def star_pts(scale=1.0):
    pts = []
    for i in range(10):
        a = math.radians(90 + 36 * i)
        r = (R_OUT if i % 2 == 0 else R_IN) * scale
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def star_half() -> Part:
    base = extrude(Plane.XY * Polygon(*star_pts(), align=None), BASE_H)
    base = chamfer(base.edges().group_by(Axis.Z)[0], EDGE_CHAMFER)
    bevel = loft([
        Plane.XY.offset(BASE_H) * Polygon(*star_pts(), align=None),
        Plane.XY.offset(HALF_T) * Polygon(*star_pts(TOP_SCALE), align=None),
    ])
    part = base + bevel

    # neck boss: half cylinder along Y on the bed
    y0 = -R_IN - BOSS_DROP
    blen = BOSS_END - y0
    boss = Pos(0, y0 + blen / 2, 0) * (Rot(90, 0, 0) * Cylinder(BOSS_R, blen))
    boss = boss & Box(4 * BOSS_R, 2 * blen, 2 * BOSS_R, align=ON_BED)
    part = part + boss

    # diamond socket groove (45 deg roof)
    sock = Pos(0, y0 + SOCKET_DEPTH / 2 - 0.5, 0) * (
        Rot(0, 45, 0) * Box(SOCKET_SIDE, SOCKET_DEPTH + 1, SOCKET_SIDE))
    part = part - sock

    for deg in (90, 162, 18):
        a = math.radians(deg)
        part = part - Pos(DOWEL_RADIUS * math.cos(a), DOWEL_RADIUS * math.sin(a),
                          DOWEL_DEPTH) * pin_hole(DOWEL_D, DOWEL_DEPTH)
    return part


def sleeve() -> Part:
    ro_b = SLEEVE_ID_BOT / 2 + SLEEVE_WALL
    ri_b = SLEEVE_ID_BOT / 2
    ri_t = SLEEVE_ID_TOP / 2
    ro_t = SLEEVE_TOP_OD / 2
    z_tip = SLEEVE_LEN + ri_t          # 45 deg inner cone closes the top
    z_top = z_tip + SLEEVE_CAP
    outer = Cone(ro_b, ro_t, z_top, align=ON_BED)
    inner = Cone(ri_b, ri_t, SLEEVE_LEN, align=ON_BED)
    tip = Pos(0, 0, SLEEVE_LEN) * Cone(ri_t, 0.5, ri_t - 0.5, align=ON_BED)  # no apex point (meshes badly)
    body = outer - inner - tip
    body = chamfer(body.edges().group_by(Axis.Z)[0], EDGE_CHAMFER)
    peg = Pos(0, 0, z_top) * (Rot(0, 0, 45) * Box(PEG, PEG, PEG_LEN, align=ON_BED))
    peg = chamfer(peg.edges().group_by(Axis.Z)[-1], 1.0)
    return body + peg


def build():
    h = star_half()
    bb = h.bounding_box()
    h_len = bb.max.Y - bb.min.Y
    h2 = Pos(0, h_len + GAP, 0) * h
    s = sleeve()
    s = Pos(bb.max.X + GAP + SLEEVE_ID_BOT / 2 + SLEEVE_WALL, 0, 0) * s
    return [h, h2, s]
