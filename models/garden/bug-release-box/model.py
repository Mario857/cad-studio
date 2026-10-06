"""bug-release-box: pocket catch-and-release box for stink bugs.

Spec: 60x40x30 box. Sliding trapdoor lid on top (45 deg dovetail rails, 0.25 mm clearance, slides out
toward +X). One-way funnel in the -X end wall (45 deg cone narrowing to a 15 mm hole inside the box).
Lanyard hole in a lug at the +X foot. Two parts printed side by side flat: box (open top up) and slide.
Assumptions: lid friction fit only (no detent); funnel axis at mid-height; lid printed wide side down.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="auto",
)

L = 60.0
W = 40.0
H = 30.0
WALL_X = 2.4
FLOOR = 2.0
CAV_W = 32.0          # cavity width (Y)
RAIL_H = 3.0          # groove height at top
GROOVE_B = 17.5       # groove half width at ledge (z = H - RAIL_H)
CLR = 0.25
LID_T = RAIL_H - CLR  # 2.75
HOLE_D = 15.0         # funnel exit hole
FUNNEL_ZC = 14.5
FUNNEL_R0 = 13.0      # entry radius at outer face
SHELL_T = 1.4
LUG_D = 4.5


def cone_x(x0, r0, r1, zc=FUNNEL_ZC):
    h = abs(r0 - r1)  # 45 deg
    return Pos(x0 + h / 2, 0, zc) * Rot(0, 90, 0) * Cone(r0, r1, h)


def build():
    zl = H - RAIL_H
    box = rounded_box(L, W, H, radius=3)
    # inner funnel shell (45 deg)
    xs = -L / 2
    r_in_wall = FUNNEL_R0 - WALL_X  # inner radius at inner wall face
    r_end = HOLE_D / 2
    x_end = xs + WALL_X + (r_in_wall - r_end)
    shell = cone_x(xs + WALL_X - 0.6, r_in_wall + SHELL_T + 0.6, r_end + SHELL_T)
    box = box + shell
    # cavity under the lid
    box = box - Pos(0, 0, FLOOR + (zl - FLOOR) / 2) * Box(L - 2 * WALL_X, CAV_W, zl - FLOOR + 0.01)
    # dovetail groove, open at +X
    g = Pos(-L / 2 + WALL_X, 0, 0) * extrude(
        Plane.YZ * Polygon((-GROOVE_B, zl), (GROOVE_B, zl), (GROOVE_B - RAIL_H, H + 0.01),
                           (-GROOVE_B + RAIL_H, H + 0.01), align=None),
        L / 2 + 1 - (-L / 2 + WALL_X) + 0.01)
    box = box - g
    # funnel opening (45 deg cone through wall and shell)
    box = box - cone_x(xs - 0.01, FUNNEL_R0 + 0.01, r_end)
    # lanyard lug
    lug = Pos(L / 2 + 3, 0, 0) * rounded_box(10, 12, 4, radius=2)
    lug = lug - Pos(L / 2 + 4, 0, 4) * pin_hole(LUG_D, 10)
    box = box + lug

    # slide (printed flat beside the box, wide face down)
    hb = GROOVE_B - CLR
    ht = hb - LID_T
    lx0 = -L / 2 + WALL_X + 0.3
    lx1 = L / 2 - 0.1
    lid = Pos(lx0, 0, 0) * extrude(
        Plane.YZ * Polygon((-hb, 0), (hb, 0), (ht, LID_T), (-ht, LID_T), align=None), lx1 - lx0)
    lid = lid + Pos(lx1 - 2, 0, LID_T) * Box(3, 2 * ht - 2, 1.5, align=ON_BED)
    lid = Pos(0, -(W / 2 + hb + 6), 0) * lid
    return [box, lid]
