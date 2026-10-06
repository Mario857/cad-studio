"""vent-screen-frame: snap-in two-ring frame clamping insect mesh over a 100 mm round vent.

Spec: INNER ring (98 mm OD press-fit body, 90 mm ID) with a 110 mm flange, 4 tab slots and
8 peg holes. OUTER retaining ring (110 OD / 92 ID) with 4 snap tabs + 8 pegs. Mesh is laid on
the flange, outer ring pegs pierce it, tabs snap through the slots and hook under the flange.
Both parts are modelled in PRINT layout (flat, side by side, no supports): inner flange-down
with body up; outer plate-down with tabs/pegs up.
Two separate bodies are intentional (inner + outer ring).
Assumptions: vent bore 100 mm (0.5 mm radial clearance from 98 OD is taken up by a snug
press, tune BODY_OD); mesh <= 0.5 mm thick; ABS+ tabs flex ~0.6 mm.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="off",
)

BODY_OD = 98.0
BODY_ID = 90.0
BODY_H = 8.0
FLANGE_OD = 110.0
FLANGE_T = 2.4
PLATE_ID = 92.0
PLATE_T = 2.4
TAB_R0, TAB_R1 = 50.2, 51.8   # arm radial extent
TAB_W = 8.0
HOOK_OUT = 53.6
CATCH_Z = 3.2                 # catch height above plate (>= flange + mesh)
SLOT_R0, SLOT_R1, SLOT_W = 49.6, 53.0, 9.0
PEG_R = 52.0
PEG_D = 2.4
PEG_H = 3.0
HOLE_D = 2.9
GAP = 8.0


def inner_ring():
    p = Cylinder(FLANGE_OD / 2, FLANGE_T, align=ON_BED)
    p = p + Cylinder(BODY_OD / 2, BODY_H + FLANGE_T, align=ON_BED)
    p = p - Cylinder(BODY_ID / 2, BODY_H + FLANGE_T, align=ON_BED)
    p = chamfer(p.edges().group_by(Axis.Z)[0].filter_by(GeomType.CIRCLE).sort_by(SortBy.RADIUS)[-1], 0.4)
    p = chamfer(p.edges().group_by(Axis.Z)[-1].sort_by(SortBy.RADIUS)[-1], 0.6)
    for i in range(4):
        a = 90 * i + 45
        slot = Pos(0, 0, 0) * Rot(0, 0, a) * Pos((SLOT_R0 + SLOT_R1) / 2, 0, 0) * Box(
            SLOT_R1 - SLOT_R0, SLOT_W, FLANGE_T, align=ON_BED)
        p = p - slot
    for i in range(8):
        a = math.radians(22.5 + 45 * i + 0)
        p = p - Pos(PEG_R * math.cos(a), PEG_R * math.sin(a), 0) * Cylinder(HOLE_D / 2, FLANGE_T, align=ON_BED)
    return p


def outer_ring():
    p = Cylinder(FLANGE_OD / 2, PLATE_T, align=ON_BED) - Cylinder(PLATE_ID / 2, PLATE_T, align=ON_BED)
    p = chamfer(p.edges().group_by(Axis.Z)[0].sort_by(SortBy.RADIUS)[-1], 0.4)
    T = PLATE_T
    prof = Polygon((TAB_R0, T - 0.2), (TAB_R1, T - 0.2), (TAB_R1, T + CATCH_Z),
                   (HOOK_OUT, T + CATCH_Z + 1.8), (TAB_R1, T + CATCH_Z + 3.6), (TAB_R0, T + CATCH_Z + 3.6),
                   align=None)
    tab = extrude(Plane.XZ * prof, TAB_W / 2, both=True)
    for i in range(4):
        p = p + Rot(0, 0, 90 * i + 45) * tab
    cone = Cone(PEG_D / 2, PEG_D / 2 - 0.9, PEG_H, align=ON_BED)
    for i in range(8):
        a = math.radians(22.5 + 45 * i)
        p = p + Pos(PEG_R * math.cos(a), PEG_R * math.sin(a), T - 0.1) * cone
    return p


def build():
    dx = FLANGE_OD + GAP
    return [Pos(-dx / 2, 0, 0) * inner_ring(), Pos(dx / 2, 0, 0) * outer_ring()]
