"""sofa-arm-tray: saddle tray for a sofa arm with a drained cup holder and a phone slot.

Spec: an inverted-U saddle drops over a sofa arm (ARM_WIDTH 80-120 mm, default 100). The deck
carries a Ø80 mm cup holder (drain holes in the floor) and an upright phone slot running along
the arm, so the screen faces the person sitting inboard. All edges get 1.5 mm fillets except the
bed-contact (skirt bottom) edges, which get the 0.4 mm elephant-foot chamfer.
Load: 0.6 kg drink in the cup holder.

Prints upright (in-use orientation) with zero supports: the saddle ceiling is a 45° gable that
meets at a narrow BRIDGE-wide apex; the gable also self-centres the tray on rounded arm tops.

Assumptions:
- Arm is roughly rectangular/rounded; the arm's top corners rest on the 45° gable faces, so the
  skirts hang ~SKIRT_H down each side. Set ARM_WIDTH to the measured arm width.
- Cups up to Ø80 mm (hole Ø82); drain holes let spills/condensation through instead of
  pooling (put a cloth under it if the arm upholstery must stay dry).
- Phone up to 13 mm thick incl. case (slot 14 mm), screen facing -X (inboard side).
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,            # rests on the sofa arm, not free-standing on a flat surface
    loads=[],                  # filled in below from the cup position
    print_orientation=(0, 0, 0),  # upright: gable ceiling is support-free
    supports="off",            # only flagged area is the 2 mm rounded gable apex: a tiny bridge, prints clean
    brim="on",                # ABS on two long thin skirt rails: brim against warping
)

# Parameters
ARM_WIDTH = 100.0       # sofa arm width (80-120)
ARM_CLEAR = 2.0         # per side
SKIRT_T = 4.0           # side skirt thickness
SKIRT_H = 30.0          # vertical skirt height below the gable
BRIDGE = 2.0            # flat at the gable apex (keeps the ceiling support-free)
DECK_T = 4.0            # deck thickness above the gable apex
LENGTH = 180.0          # along the arm (Y)

CUP_D = 80.0            # cup diameter
CUP_CLEAR = 1.0         # per side
CUP_WALL = 3.2
CUP_H = 45.0            # ring height above deck
CUP_Y = -LENGTH / 2 + 8.0 + (CUP_D / 2 + CUP_CLEAR + CUP_WALL)
DRAIN_D = 6.0
DRAIN_R = 22.0          # radius of the outer drain-hole circle

PHONE_SLOT_W = 14.0     # across X
PHONE_SLOT_DEPTH = 32.0
PHONE_FLOOR = 4.0       # slot floor above deck
PHONE_WALL = 6.0
PHONE_BLOCK_L = 70.0    # along Y
PHONE_Y = LENGTH / 2 - 8.0 - PHONE_BLOCK_L / 2

FILLET = 1.5
FILLET_2D = 2.0        # profile corners; != FILLET avoids degenerate corner blends
BED_CHAMFER = 0.4

INNER_W = ARM_WIDTH + 2 * ARM_CLEAR
OUTER_W = INNER_W + 2 * SKIRT_T
Z_GABLE = SKIRT_H
Z_APEX = SKIRT_H + (INNER_W - BRIDGE) / 2
Z_DECK = Z_APEX + DECK_T

META["loads"] = [dict(at=(0, CUP_Y, Z_DECK + 20), grams=600)]


def _ends(part, y0):
    """Edges of the end-cap faces at |y| = y0 (above the bed)."""
    return [e for e in part.edges()
            if abs(abs(e.center().Y) - y0) < 0.01 and abs(e.bounding_box().size.Y) < 0.01
            and e.bounding_box().max.Z > BED_CHAMFER + 0.01]


def build() -> Part:
    c = BED_CHAMFER
    xo, xi, b = OUTER_W / 2, INNER_W / 2, BRIDGE / 2
    # saddle profile (XZ), bed corners chamfered, every other corner rounded in 2D
    profile = Polygon(
        (-xo, c), (-xo + c, 0), (-xi - c, 0), (-xi, c), (-xi, Z_GABLE), (-b, Z_APEX),
        (b, Z_APEX), (xi, Z_GABLE), (xi, c), (xi + c, 0), (xo - c, 0), (xo, c),
        (xo, Z_DECK), (-xo, Z_DECK),
        align=None,
    )
    profile = fillet(profile.vertices().filter_by_position(Axis.Y, 1.0, 1e3), FILLET_2D)
    saddle = extrude(Plane.XZ * profile, LENGTH / 2, both=True)
    saddle = fillet(_ends(saddle, LENGTH / 2), FILLET)

    # cup holder ring, top rim rounded
    cup_ri = CUP_D / 2 + CUP_CLEAR
    ring = Cylinder(cup_ri + CUP_WALL, CUP_H, align=ON_BED) - Cylinder(cup_ri, CUP_H, align=ON_BED)
    ring = fillet(ring.edges().group_by(Axis.Z)[-1], FILLET)
    ring = Pos(0, CUP_Y, Z_DECK - 1) * ring

    # phone block: U profile (XZ) extruded along Y, slot through along Y
    blk_w = PHONE_SLOT_W + 2 * PHONE_WALL
    blk_h = PHONE_FLOOR + PHONE_SLOT_DEPTH
    sw = PHONE_SLOT_W / 2
    bprof = Polygon(
        (-blk_w / 2, -1), (blk_w / 2, -1), (blk_w / 2, blk_h), (sw, blk_h), (sw, PHONE_FLOOR),
        (-sw, PHONE_FLOOR), (-sw, blk_h), (-blk_w / 2, blk_h),
        align=None,
    )
    bprof = fillet(bprof.vertices().filter_by_position(Axis.Y, 0.5, 1e3), FILLET_2D)
    block = extrude(Plane.XZ * bprof, PHONE_BLOCK_L / 2, both=True)
    block = fillet(_ends(block, PHONE_BLOCK_L / 2), FILLET)
    block = Pos(0, PHONE_Y, Z_DECK) * block

    part = saddle + ring + block
    # concave roots of ring and block on the deck
    roots = [e for e in part.edges()
             if abs(e.center().Z - Z_DECK) < 0.01 and abs(e.bounding_box().size.Z) < 0.01
             and abs(e.center().Y) < LENGTH / 2 - 2 and abs(e.center().X) < xo - 2]
    part = fillet(roots, FILLET)

    # drain holes through the deck/gable (vertical), rims softened
    drains = [(0, CUP_Y)] + [
        (x * DRAIN_R, CUP_Y + y * DRAIN_R) for x, y in ((1, 0), (-1, 0), (0, 1), (0, -1))
    ]
    for x, y in drains:
        part -= Pos(x, y, -1) * Cylinder(DRAIN_D / 2, Z_DECK + 2, align=ON_BED)
    rims = [e for e in part.edges().filter_by(GeomType.CIRCLE)
            if abs(e.radius - DRAIN_D / 2) < 0.01] + [
        e for e in part.edges() if e.geom_type == GeomType.BSPLINE or e.geom_type == GeomType.ELLIPSE]
    rims = [e for e in rims if abs(e.center().Y - CUP_Y) < DRAIN_R + DRAIN_D]
    part = fillet(rims, 1.0)
    return part
