"""shower-rail-shelf: soap/razor tray that clamps onto a vertical shower riser rail.

Spec: single printed part. A split collar (split at the back, toward the wall) wraps a vertical
round riser rail (RAIL_D, 19-25 mm, default 22). Two ears beside the split are pinched by one
M4 bolt (through a teardrop hole along X) into a hex nut trap - closing the 3 mm gap squeezes the
collar onto the rail. A ~100 x 70 mm tray hangs in front (+Y) of the rail, bottom flush with the
collar bottom.

Drainage: the tray has no solid floor - it is a grid of 45-degree trapezoid ribs along Y (1.4 mm
convex ridge on top) with ~4 mm open through-slots between them, so nothing can hold water; the lip
top is bevelled 45 deg both sides to a 1.3 mm ridge (ridges are kept >= 1.2 mm wide for the
wall check; a convex 1.3 mm ridge cannot pool). The collar/ear top is cut at TOP_SLOPE_DEG falling toward the tray, so it sheds into it.

Print orientation (0, 0, 0) = in-use orientation, chosen for strength: the rail axis is vertical,
so the collar ring and the ears lie IN the layer planes. Bolt tension pulls the ears apart and
creates hoop stress around the ring - both run along the extrusion lines, never across layer
bonds, so the collar cannot delaminate/split along a layer line. (Printing it on its side would put
the ring hoop across layers and it would crack at the ears on first tightening.) The tray load
(cantilever moment about X) also loads the collar-tray joint in-plane. Everything starts on the
bed: no supports.

Hardware: 1x M4x20 socket head bolt, 1x M4 hex nut (in trap on -X ear),
optional 1 mm rubber strip (bicycle inner tube) inside the collar - set RUBBER_T = 1.0.

Assumptions: rail centre is >= 25 mm from the wall (ears reach ~21 mm behind rail centre);
one print per rail size (change RAIL_D); 0.5 kg max on the tray.
"""

import math

from build123d import *

from cadlib import *

# Parameters
RAIL_D = 22.0           # riser rail outer diameter (19-25)
RUBBER_T = 0.0          # optional rubber liner thickness inside collar
BORE_FIT = "loose"      # collar bore clearance over rail (+ liner)
COLLAR_WALL = 4.0       # collar ring wall
CLAMP_H = 30.0          # collar height
SPLIT_GAP = 3.0         # clamp slot width (closes when bolt tightened)
EAR_T = 7.0             # each ear thickness along the bolt (X)
EAR_MARGIN = 4.5        # material beyond bolt hole centre
BOLT = "M4"
BOLT_NOM = 4.0
BOLT_FIT = "loose"
BOLT_Z = CLAMP_H / 2
NUT_DEPTH = 3.6
TOP_SLOPE_DEG = 10.0    # collar top falls toward the tray

TRAY_W = 100.0          # along X
TRAY_D = 70.0           # along Y (away from rail)
TRAY_H = 14.0           # lip height above bed
TRAY_WALL = 2.5
LIP_CHAMFER = 0.6       # 45-deg bevel each side of lip top, leaves a 1.3 mm ridge
TRAY_R = 6.0            # plan corner radius
RIB_BASE = 4.4          # floor rib base width (45 deg faces)
RIB_TOP = 1.4           # narrow convex ridge on top of each rib (sheds water, >= 1.2 wall)
RIB_H = (RIB_BASE - RIB_TOP) / 2
RIB_FOOT = 1.0          # vertical foot so the bed edge is square, not a 45-deg knife edge
RIB_PITCH = 8.4         # rib spacing -> 4 mm drain slots
CROSS_RIBS = 2          # triangular ribs along X tying the Y ribs

BORE_D = clearance(RAIL_D + 2 * RUBBER_T, BORE_FIT)
BORE_R = BORE_D / 2
COLLAR_R = BORE_R + COLLAR_WALL
BOLT_CLEAR = clearance(BOLT_NOM, BOLT_FIT)
BOLT_Y = -(BORE_R + 2.0 + BOLT_CLEAR / 2)
EAR_X = SPLIT_GAP / 2 + EAR_T
TRAY_Y0 = COLLAR_R - TRAY_WALL  # tray back wall inner face tangent to collar

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,  # clamped to the rail
    loads=[dict(at=(0, TRAY_Y0 + TRAY_D / 2, 8), grams=500)],
    print_orientation=(0, 0, 0),  # in-use: collar hoop & bolt tension lie in layer planes
    supports="off",
    brim="auto",
)


def _rib_y(length: float) -> Part:
    """Triangular rib along Y, peaked, base on bed, centred on origin."""
    tri = Polygon((-RIB_BASE / 2, 0), (RIB_BASE / 2, 0), (RIB_BASE / 2, RIB_FOOT),
                  (RIB_TOP / 2, RIB_FOOT + RIB_H), (-RIB_TOP / 2, RIB_FOOT + RIB_H),
                  (-RIB_BASE / 2, RIB_FOOT), align=None)
    return extrude(Plane.XZ * tri, length / 2, both=True)


def _rib_x(length: float) -> Part:
    tri = Polygon((-RIB_BASE / 2, 0), (RIB_BASE / 2, 0), (RIB_BASE / 2, RIB_FOOT),
                  (RIB_TOP / 2, RIB_FOOT + RIB_H), (-RIB_TOP / 2, RIB_FOOT + RIB_H),
                  (-RIB_BASE / 2, RIB_FOOT), align=None)
    return extrude(Plane.YZ * tri, length / 2, both=True)


def build() -> Part:
    # --- collar body: ring + block reaching the tray + ears
    ring = Cylinder(COLLAR_R, CLAMP_H, align=ON_BED)
    block_len = TRAY_Y0 + TRAY_WALL
    block = Pos(0, block_len / 2, 0) * Box(2 * COLLAR_R, block_len, CLAMP_H, align=ON_BED)
    ear_len = -BOLT_Y + EAR_MARGIN
    ears = Pos(0, -ear_len / 2, 0) * Box(2 * EAR_X, ear_len, CLAMP_H, align=ON_BED)
    collar = ring + block + ears
    collar = chamfer(collar.edges().group_by(Axis.Z)[0], 0.4)

    # --- tray frame
    cy = TRAY_Y0 + TRAY_D / 2
    outer = Pos(0, cy, 0) * rounded_box(TRAY_W, TRAY_D, TRAY_H, radius=TRAY_R)
    inner = Pos(0, cy, -1) * Box(TRAY_W - 2 * TRAY_WALL, TRAY_D - 2 * TRAY_WALL, TRAY_H + 2,
                                align=ON_BED)
    inner = fillet(inner.edges().filter_by(Axis.Z), TRAY_R - TRAY_WALL)
    frame = outer - inner
    # peaked lip top: 45-degree chamfers on both top edges
    frame = chamfer(frame.edges().group_by(Axis.Z)[-1], LIP_CHAMFER)

    # --- floor: peaked ribs with through-slots between
    in_w = TRAY_W - 2 * TRAY_WALL
    in_d = TRAY_D - 2 * TRAY_WALL
    n = int(in_w // RIB_PITCH)
    x0 = -(n - 1) * RIB_PITCH / 2
    ribs = [Pos(x0 + i * RIB_PITCH, cy, 0) * _rib_y(in_d + 1) for i in range(n)]
    for j in range(CROSS_RIBS):
        y = TRAY_Y0 + TRAY_WALL + in_d * (j + 1) / (CROSS_RIBS + 1)
        ribs.append(Pos(0, y, 0) * _rib_x(in_w + 1))
    tray = frame
    for r in ribs:
        tray = tray + r

    part = collar + tray

    # --- cuts
    part = part - Cylinder(BORE_R, CLAMP_H + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
        Location((0, 0, -1)))
    slot_len = ear_len + 2
    part = part - Pos(0, -slot_len / 2, -1) * Box(SPLIT_GAP, slot_len, CLAMP_H + 2, align=ON_BED)
    # sloped top (falls toward +Y / tray)
    big = 300
    cutter = Pos(0, 0, big / 2) * Box(big, big, big)
    cutter = Pos(0, -ear_len, CLAMP_H) * Rot(-TOP_SLOPE_DEG, 0, 0) * cutter
    part = part - cutter
    # bolt + nut trap
    part = part - Pos(0, BOLT_Y, BOLT_Z) * teardrop_hole(BOLT_CLEAR, 2 * EAR_X + 2, along="X")
    nut = nut_trap(BOLT, NUT_DEPTH, rotation=30)
    part = part - Pos(-EAR_X, BOLT_Y, BOLT_Z) * Rot(0, -90, 0) * nut
    return part
