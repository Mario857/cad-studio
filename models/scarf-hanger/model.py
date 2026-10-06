"""scarf-hanger: flat 10-ring scarf hanger that hooks onto a closet rod.

Spec: flat plate (in use: hangs in the XZ plane, thickness along Y, perpendicular to the rod).
5 columns x 2 rows of rings (wide like a clothes hanger, ~253 x 173 mm), Ø45 mm clear opening, every ring edge chamfered on both faces so
scarves slide without snagging. A J-hook on top (centred over the ring grid so it hangs plumb)
fits closet rods Ø25-35 mm; the rod enters from the lower right of the hook, between the hook
tip and the flat shoulder that ties the two top rings together.

Print: lying flat (rx=90 -> plate thickness becomes Z), so the in-plane bending of the hook and
ring web runs along the layers (strongest direction). No supports needed.

Assumptions:
- "Ø45 mm" is the clear inner opening of each ring (scarf passes through it).
- Max rod Ø35 mm; hook inner Ø = ROD_MAX + 2*HOOK_CLEAR, rod entry gap >= ROD_MAX + 2 mm.
- Load: up to ~10 scarves (~1.5 kg total) hanging from the rings.
- 5x2 layout instead of 2x5: a 2x5 column is ~320 mm tall, beyond the ~280 mm the H2C
  dual-nozzle area reliably slices; 5x2 keeps the footprint ~253 x 173 mm. The plate sits
  perpendicular to the rod, ~127 mm each side of it (normal closet depth is fine).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,            # hangs from a rod
    loads=[],
    print_orientation=(90, 0, 0),  # plate flat on the bed: in-plane loads run along layers
    supports="off",
    brim="auto",
)

# Parameters
RING_ID = 45.0            # clear opening of each ring
RING_WALL = 4.0           # radial ring wall
RING_PITCH = 50.0         # centre-to-centre: 5 mm web between openings
COLS = 5
ROWS = 2
THICK = 7.0               # plate thickness (Y in use, Z when printing)
EDGE_CHAMFER = 1.5        # anti-snag chamfer on ring openings, both faces
OUTER_CHAMFER = 1.0       # chamfer on outer contour edges, both faces

ROD_MAX = 35.0            # largest closet rod diameter
ROD_MIN = 25.0            # smallest (sits at top of hook, nothing to size)
HOOK_CLEAR = 1.0          # radial clearance around the largest rod
HOOK_WALL = 7.0           # hook cross-section width (in plane)
HOOK_TIP_DEG = -10.0      # hook arc runs from 180 deg (stem) over the top to this angle
ENTRY_GAP = ROD_MAX + 2.0 # vertical gap from hook tip to plate top
GUSSET = 8.5              # stem/shoulder gusset leg

RING_RO = RING_ID / 2 + RING_WALL
HOOK_RI = ROD_MAX / 2 + HOOK_CLEAR
HOOK_RO = HOOK_RI + HOOK_WALL
HOOK_RM = (HOOK_RI + HOOK_RO) / 2


def ring_centres():
    xs = [(c - (COLS - 1) / 2) * RING_PITCH for c in range(COLS)]
    zs = [RING_RO + r * RING_PITCH for r in range(ROWS)]
    return [(x, z) for x in xs for z in zs]


def build() -> Part:
    centres = ring_centres()
    top_c = max(z for _, z in centres)
    top_z = top_c + RING_RO
    x_span = max(x for x, _ in centres)

    # hook geometry
    tip_drop = HOOK_RM * math.sin(math.radians(-HOOK_TIP_DEG)) + HOOK_WALL / 2
    zc = top_z + ENTRY_GAP + tip_drop

    # plate = rounded hull of the ring grid (no snag-prone cusps between rings)
    z_lo = min(z for _, z in centres)
    prof = Pos(0, (z_lo + top_c) / 2) * RectangleRounded(
        2 * (x_span + RING_RO), (top_c - z_lo) + 2 * RING_RO, RING_RO - 0.01)
    # stem (left side of hook)
    stem_x = -HOOK_RM
    stem_bot = top_z - 3.0
    prof += Pos(stem_x, (stem_bot + zc) / 2) * Rectangle(HOOK_WALL, zc - stem_bot)
    # gusset right of stem
    sx = -HOOK_RI
    prof += Polygon((sx - 1.0, top_z - 1.0), (sx + GUSSET, top_z - 1.0),
                    (sx, top_z + GUSSET), (sx - 1.0, top_z + GUSSET), align=None)
    # hook arc (annular sector) + rounded tip
    a0 = math.radians(HOOK_TIP_DEG)
    L = 3 * HOOK_RO
    wedge = Polygon((0, 0), (L * math.cos(a0), L * math.sin(a0)), (L, L), (-L, L), (-L, 0),
                    align=None)
    prof += Pos(0, zc) * ((Circle(HOOK_RO) - Circle(HOOK_RI)) & wedge)
    prof += Pos(HOOK_RM * math.cos(a0), zc + HOOK_RM * math.sin(a0)) * Circle(HOOK_WALL / 2)

    # ring openings
    for x, z in centres:
        prof -= Pos(x, z) * Circle(RING_ID / 2)

    part = extrude(Plane.XZ * prof, THICK)  # extrudes toward -Y
    part = Pos(0, THICK / 2, 0) * part

    # anti-snag chamfers: ring openings bigger, outer contour smaller
    face_edges = part.edges().filter_by(Axis.Y, reverse=True)
    hole_edges = [e for e in face_edges
                  if e.geom_type == GeomType.CIRCLE and abs(e.radius - RING_ID / 2) < 0.01]
    part = chamfer(hole_edges, EDGE_CHAMFER)
    face_edges = part.edges().filter_by(Axis.Y, reverse=True)
    outer = [e for e in face_edges
             if abs(abs(e.center().Y) - THICK / 2) < 0.01
             and not (e.geom_type == GeomType.CIRCLE
                      and abs(e.radius - (RING_ID / 2 + EDGE_CHAMFER)) < 0.05)]
    part = chamfer(outer, OUTER_CHAMFER)
    return part
