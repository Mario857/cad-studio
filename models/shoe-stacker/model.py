"""shoe-stacker: one-piece angled shoe stacker (one shoe above the other).

Spec: Z-free "C" profile seen from the side, extruded across the shoe width.
  - Floor plate: the lower shoe stands on it (its weight also anchors the stacker).
  - Back wall at the heel end, rising to a short heel-stop lip.
  - Top ramp: the upper shoe rests on it, sloping down toward the toe (front, +X)
    so the lower shoe's toe box and heel collar both fit under it.
  - Ramp is thicker at the root (back) and tapers to the tip; 45-degree gussets in
    both inner corners stiffen the cantilever.
  Overall L_TOTAL x WIDTH x (H_BACK + LIP), fits the 300 x 320 bed in one piece,
  so no 2-part slide-together version is needed.

Print: lying on its side (profile flat on the bed, extrusion axis vertical), so
every wall is vertical (no overhangs, no supports) and the ramp bending load runs
along the layers, not across them.

Assumptions:
  - Adult shoes up to EU 46 (~320 mm long, ~110 mm wide). The stacker need not be
    full shoe length: 280 mm supports heel to ball of foot; toe overhangs ~40 mm.
  - Lower shoe: heel collar <= ~120 mm, toe box <= ~85 mm tall (low/mid sneakers,
    dress shoes). High-tops/boots will not fit under the ramp.
  - 1.5 kg load = both shoes worst case, modelled on the ramp near mid-length.
  - WIDTH 100 mm < shoe width 110 mm on purpose (shoe sole overlaps slightly).
"""

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm. Heel end at x=0, toe toward +X.
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=True,
    loads=[dict(at=(140, 50, 120), grams=1500)],
    # printed on its side: profile (XZ) flat on the bed, width (Y) vertical,
    # so the ramp's bending stress runs along the layers.
    print_orientation=(90, 0, 0),
    supports="off",
    brim="auto",
)

# Parameters
L_TOTAL = 280.0      # length of floor plate and ramp (X)
WIDTH = 100.0        # across the shoe (Y), extrusion length
T_FLOOR = 4.0        # floor plate thickness
T_WALL = 6.0         # back wall thickness
H_BACK = 135.0       # ramp top surface height at the back wall
H_FRONT = 95.0       # ramp top surface height at the front tip
T_RAMP_ROOT = 8.0    # ramp thickness at the back (root of cantilever)
T_RAMP_TIP = 4.0     # ramp thickness at the front tip
LIP = 12.0           # heel-stop lip above the ramp at the back
GUSSET = 25.0        # 45-degree corner gusset legs (both inner corners)
EDGE_CHAMFER = 0.4   # elephant-foot chamfer on the print-bed face


def _z_top(x: float) -> float:
    return H_BACK + (H_FRONT - H_BACK) * x / L_TOTAL


def _z_under(x: float) -> float:
    t = T_RAMP_ROOT + (T_RAMP_TIP - T_RAMP_ROOT) * x / L_TOTAL
    return _z_top(x) - t


def build() -> Part:
    tw, g = T_WALL, GUSSET
    pts = [
        (0, 0),
        (L_TOTAL, 0),
        (L_TOTAL, T_FLOOR),
        (tw + g, T_FLOOR),                 # lower gusset
        (tw, T_FLOOR + g),
        (tw, _z_under(tw) - g),            # upper gusset
        (tw + g, _z_under(tw + g)),
        (L_TOTAL, _z_under(L_TOTAL)),      # ramp underside to tip
        (L_TOTAL, _z_top(L_TOTAL)),
        (tw, _z_top(tw)),                  # ramp top back to heel stop
        (tw, _z_top(tw) + LIP),
        (0, _z_top(tw) + LIP),
    ]
    profile = Polygon(*pts, align=None)
    # Plane.XZ normal is -Y; extrude from y=0 to y=-WIDTH, then shift to y in [0, WIDTH]
    part = Pos(0, WIDTH, 0) * extrude(Plane.XZ * profile, WIDTH)
    # soften the free outer corners of the profile (edges parallel to Y)
    tip_edges = part.edges().filter_by(Axis.Y).filter_by_position(Axis.X, L_TOTAL - 0.1, L_TOTAL + 0.1)
    part = fillet(tip_edges, 1.5)
    # elephant-foot chamfer on both side faces (one becomes the print-bed face)
    side_edges = part.faces().sort_by(Axis.Y)[0].edges() + part.faces().sort_by(Axis.Y)[-1].edges()
    part = chamfer(side_edges, EDGE_CHAMFER)
    return part
