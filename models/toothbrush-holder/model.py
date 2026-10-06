"""toothbrush-holder: free-standing bathroom holder, 4 toothbrushes + 1 toothpaste tube.

Spec: wide drained floor plate with underside drain channels, a waist block with four D16.4 bores
(brush handles) plus one D28 bore (tube standing on its cap), capped by a raised plate whose underside is
a 45 deg skirt (prints without supports).
Handles rest on the floor; water leaves through slots in the floor into V-less triangular channels
that run out of both long sides, so nothing pools. Assumptions: brush handle < 16 mm wide at the head end (head passes the hole), ~20 g each with centre
of mass ~50 mm above the plate; tube cap < 28 mm; PETG for wet use. Floor is wider than the top
plate (106 x 68 vs 98 x 60) to give a tip angle > 12 deg with brushes loaded.
"""

from build123d import *

from cadlib import *

TOP_Z = 56.0
BRUSH_LOADS = [dict(at=(x, y, TOP_Z + 50), grams=20) for x in (-33.0, -7.0) for y in (-15.0, 15.0)]

META = dict(
    material="PETG",
    quality="standard",
    standing=True,
    loads=BRUSH_LOADS,
    print_orientation="auto",
    supports="auto",
    brim="auto",
)

# Parameters
FLOOR_L, FLOOR_W, FLOOR_T = 106.0, 68.0, 6.0
PLATE_L, PLATE_W, PLATE_T = 98.0, 60.0, 4.0
SKIRT = 4.0                     # 45 deg underside skirt of the top plate
BRUSH_D = 16.4                  # brush hole
BRUSH_WALL = 2.0
BRUSH_XS = (-33.0, -7.0)
BRUSH_YS = (-15.0, 15.0)
PASTE_D = 28.0                  # toothpaste hole
PASTE_WALL = 2.0
PASTE_X = 25.0
ENTRY_CH = 1.0                  # lead-in chamfer on the top holes
CHAN_W = 8.0                    # underside drain channels: triangular, 45 deg walls, depth = CHAN_W/2
SLOT_W, SLOT_L = 5.0, 13.0      # drain slots at each brush
PASTE_SLOT_W, PASTE_SLOT_L = 5.0, 18.0


def build() -> Part:
    floor = rounded_box(FLOOR_L, FLOOR_W, FLOOR_T, radius=8, bottom_chamfer=0.4)

    sleeves_h = TOP_Z - FLOOR_T
    brush_pts = [(x, y) for x in BRUSH_XS for y in BRUSH_YS]
    r_b = BRUSH_D / 2 + BRUSH_WALL
    r_p = PASTE_D / 2 + PASTE_WALL
    # monolithic waist between floor and plate (no flat ceilings inside)
    waist = Pos(0, 0, FLOOR_T) * extrude(RectangleRounded(PLATE_L - 2 * SKIRT, PLATE_W - 2 * SKIRT, 8 - SKIRT), sleeves_h)
    body = floor + waist

    # top plate with 45 deg skirt below it
    z_plate = TOP_Z - PLATE_T
    plate = extrude(Plane.XY.offset(z_plate) * RectangleRounded(PLATE_L, PLATE_W, 8), PLATE_T)
    skirt = loft([
        Plane.XY.offset(z_plate - SKIRT) * RectangleRounded(PLATE_L - 2 * SKIRT, PLATE_W - 2 * SKIRT, 8 - SKIRT),
        Plane.XY.offset(z_plate) * RectangleRounded(PLATE_L, PLATE_W, 8),
    ])
    body += plate + skirt

    # bores from the floor top up through the plate
    for (x, y) in brush_pts:
        body -= Pos(x, y, FLOOR_T) * Cylinder(BRUSH_D / 2, TOP_Z - FLOOR_T + 1, align=ON_BED)
        body -= Pos(x, y, TOP_Z - ENTRY_CH) * Cone(BRUSH_D / 2, BRUSH_D / 2 + ENTRY_CH + 0.01, ENTRY_CH + 0.01, align=ON_BED)
    body -= Pos(PASTE_X, 0, FLOOR_T) * Cylinder(PASTE_D / 2, TOP_Z - FLOOR_T + 1, align=ON_BED)
    body -= Pos(PASTE_X, 0, TOP_Z - ENTRY_CH) * Cone(PASTE_D / 2, PASTE_D / 2 + ENTRY_CH + 0.01, ENTRY_CH + 0.01, align=ON_BED)

    # drain slots through the floor + triangular channels underneath running out the long sides
    for x in BRUSH_XS:
        for y in BRUSH_YS:
            body -= Pos(x, y, 0) * extrude(Plane.XY * SlotOverall(SLOT_L, SLOT_W, rotation=90), FLOOR_T + 0.5)
    body -= Pos(PASTE_X, 0, 0) * extrude(Plane.XY * SlotOverall(PASTE_SLOT_L, PASTE_SLOT_W, rotation=90), FLOOR_T + 0.5)
    for cx in (*BRUSH_XS, PASTE_X):
        prof = Polygon((cx - CHAN_W / 2, 0), (cx + CHAN_W / 2, 0), (cx, CHAN_W / 2), align=None)
        body -= extrude(Plane.XZ * prof, FLOOR_W, both=True)
    return body
