"""bed-frame-cup-holder: clamp-on cup + phone holder for a bed frame side rail.

Spec:
- C-clamp hooks over the top edge of a bed side rail 20-40 mm thick (gap RAIL_MAX + RAIL_CLEAR).
  Two M6 bolts thread through captive nuts in the inner (bed-side) jaw and press the rail
  against the outer jaw, so one clamp fits any rail from RAIL_MIN to RAIL_MAX.
- Outboard of the rail: a phone slot (PHONE_SLOT_W x PHONE_SLOT_T) right against the rail,
  then a Ø85 cup pocket (+ CUP_CLEAR) with drain holes in the floor. Load 0.6 kg in the cup.

Coordinates (in use): rail runs along X, rail top at z=0, rail outer face at y=0,
bed (inner side) toward -Y, cup outboard toward +Y.

Printing / strength: printed standing on its -X end face (print_orientation (0,-90,0) -> model +X
is up). The whole C-profile of the clamp then lies in each layer, so the bending moment from the
cup load runs along the layers, not across them. Because the cup axis is horizontal while
printing, every downward-facing pocket face in print is shaped self-supporting: cup pocket and
drain holes are teardrops pointing +X, phone slot has a 45 deg V roof at +X, bolt holes are
teardrops, the +X outer corner is chamfered 45 deg. No supports needed.

Assumptions:
- Rail is a flat board/tube with an accessible top edge; clamp needs >= INNER_JAW_DEPTH of free
  rail face on the bed side and OUTER depth (BODY_H - BRIDGE_T) on the outside.
- Bolt heads face the mattress side; tighten with a hex key / thumb screw by lifting the mattress
  edge. Hardware: 2x M6x40 bolt (or M6x40 thumb screw) + 2x M6 hex nut.
- Cup up to Ø85 straight-sided (cans, tumblers, bottles); no mug-handle notch.
- Phone up to 80 mm wide x 14 mm thick incl. case; cable slot in the slot floor.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[dict(at=(0, 68, -45), grams=600)],
    print_orientation=(0, -90, 0),   # -X end face on the bed: clamp C-profile in-layer for strength
    supports="off",
    brim="auto",
)

# Rail / clamp
RAIL_MIN = 20.0
RAIL_MAX = 40.0
RAIL_CLEAR = 2.0            # extra gap so the clamp slides over a RAIL_MAX rail
BRIDGE_T = 8.0              # clamp top over the rail
OUTER_JAW_T = 6.0           # wall between rail and phone slot (outer jaw)
INNER_JAW_T = 12.0          # bed-side jaw, holds the nut traps
INNER_JAW_DEPTH = 40.0      # how far the inner jaw reaches below the rail top
INNER_FILLET = 2.0          # inside corners of the C
OUTER_FILLET = 4.0
BOLT = "M6"
BOLT_HOLE_D = 6.6           # free clearance for M6 through the jaw
NUT_DEPTH = 5.6             # M6 nut 5.0 thick + clearance
NUT_ROOF = 8.3              # 45 deg roof over the hex (> AF/sqrt3/2 + AF/2)
NUT_ROT = 0.0               # hex vertex toward +X (print up) so the trap roof self-supports
BOLT_Z = -22.0              # bolt axis height below rail top
BOLT_INSET = 22.0           # bolt distance from the X ends

# Holder
CUP_D = 85.0
CUP_CLEAR = 1.5             # diametral clearance
CUP_DEPTH = 65.0
WALL = 3.0
FLOOR = 3.0
DRAIN_D = 8.0
DRAIN_OFFSET = 22.0         # ring of drains around the centre one
TIP_FLAT = 0.0              # >0 truncates the teardrop tip to a bridge of that width
PHONE_SLOT_W = 82.0         # along the rail
PHONE_SLOT_T = 16.0         # phone thickness incl. case + clearance
CABLE_SLOT_L = 30.0
CABLE_SLOT_W = 10.0
EDGE_CHAMFER = 0.4

# Derived
GAP = RAIL_MAX + RAIL_CLEAR
R_IN = (CUP_D + CUP_CLEAR) / 2
TOP = BRIDGE_T
BODY_H = CUP_DEPTH + FLOOR
X0 = -(R_IN + WALL)
TIP_X = R_IN * math.sqrt(2) - TIP_FLAT / 2      # truncated pocket tip
X1 = TIP_X + WALL
PHONE_Y0 = OUTER_JAW_T
CUP_YC = PHONE_Y0 + PHONE_SLOT_T + WALL + R_IN
Y_END = CUP_YC + R_IN + WALL


def teardrop2d(r: float, flat: float = 0.0) -> Sketch:
    """Circle with a 45 deg point toward +X (optionally truncated to a flat of width `flat`)."""
    s = r / math.sqrt(2)
    tip = r * math.sqrt(2)
    arc = ThreePointArc((s, s), (-r, 0), (s, -s))
    if flat > 0:
        cx = tip - flat / 2
        pts = [(s, -s), (cx, -flat / 2), (cx, flat / 2), (s, s)]
    else:
        pts = [(s, -s), (tip, 0), (s, s)]
    return Sketch() + make_face(Curve() + [arc, Polyline(*pts)])


def build() -> Part:
    zb = TOP - BODY_H
    w = X1 - X0
    # --- holder body (also the outer jaw at y 0..OUTER_JAW_T)
    c = (R_IN + WALL) * (math.sqrt(2) - 1)   # x where the 45 deg outer chamfer meets y=Y_END
    y_ch = CUP_YC + (R_IN + WALL) * math.sqrt(2) - X1
    plan = Polygon((X0, 0), (X1, 0), (X1, y_ch), (c, Y_END), (X0, Y_END), align=None)
    body = extrude(Plane.XY.offset(zb) * plan, BODY_H)

    # --- clamp: bridge + inner jaw
    yi = -GAP - INNER_JAW_T
    bridge = Pos((X0 + X1) / 2, (yi + 0) / 2, 0) * Box(w, -yi, BRIDGE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    jaw = Pos((X0 + X1) / 2, yi + INNER_JAW_T / 2, TOP) * Box(
        w, INNER_JAW_T, TOP + INNER_JAW_DEPTH, align=(Align.CENTER, Align.CENTER, Align.MAX))
    part = body + bridge + jaw

    # fillets on the C profile (edges parallel to X)
    xe = part.edges().filter_by(Axis.X)
    inner = [e for e in xe if abs(e.center().Z) < 1e-3 and (abs(e.center().Y) < 1e-3 or abs(e.center().Y + GAP) < 1e-3)]
    part = fillet(inner, INNER_FILLET)
    xe = part.edges().filter_by(Axis.X)
    outer = [e for e in xe if abs(e.center().Z - TOP) < 1e-3 and abs(e.center().Y - yi) < 1e-3]
    part = fillet(outer, OUTER_FILLET)

    # --- cup pocket (teardrop plan, tip +X) and drains
    cup = Pos(0, CUP_YC) * teardrop2d(R_IN, TIP_FLAT)
    part -= extrude(Plane.XY.offset(TOP - CUP_DEPTH) * cup, CUP_DEPTH + 1)
    drains = [(0, 0), (DRAIN_OFFSET, 0), (-DRAIN_OFFSET, 0), (0, DRAIN_OFFSET), (0, -DRAIN_OFFSET)]
    for dx, dy in drains:
        d = Pos(dx, CUP_YC + dy) * teardrop2d(DRAIN_D / 2)
        part -= extrude(Plane.XY.offset(zb - 1) * d, FLOOR + 2)

    # --- phone slot (V roof toward +X) and cable slot
    xa = X0 + WALL
    xb = xa + PHONE_SLOT_W
    h = PHONE_SLOT_T / 2
    phone = Polygon((xa, PHONE_Y0), (xb, PHONE_Y0), (xb + h, PHONE_Y0 + h), (xb, PHONE_Y0 + PHONE_SLOT_T),
                    (xa, PHONE_Y0 + PHONE_SLOT_T), align=None)
    part -= extrude(Plane.XY.offset(TOP - CUP_DEPTH) * phone, CUP_DEPTH + 1)
    cx0 = (xa + xb) / 2 - CABLE_SLOT_L / 2
    cx1 = cx0 + CABLE_SLOT_L - CABLE_SLOT_W / 2
    yc0, cw = PHONE_Y0 + h - CABLE_SLOT_W / 2, CABLE_SLOT_W
    cable = Polygon((cx0, yc0), (cx1, yc0), (cx1 + cw / 2, yc0 + cw / 2), (cx1, yc0 + cw), (cx0, yc0 + cw),
                    align=None)                      # V end toward +X = self-supporting in print
    part -= extrude(Plane.XY.offset(zb - 1) * cable, FLOOR + 2)

    # --- bolts + captive nuts in the inner jaw (bolt pushes the rail toward +Y)
    for bx in (X0 + BOLT_INSET, X1 - BOLT_INSET):
        part -= Pos(bx, yi + INNER_JAW_T / 2, BOLT_Z) * Rot(0, -90, 0) * teardrop_hole(BOLT_HOLE_D, INNER_JAW_T + 2, along="Y")
        part -= Pos(bx, -GAP, BOLT_Z) * Rot(-90, 0, 0) * nut_trap(BOLT, NUT_DEPTH, rotation=NUT_ROT)
        roof = Polygon((0, -NUT_ROOF), (NUT_ROOF, 0), (0, NUT_ROOF), align=None)   # 45 deg roof over the hex
        part -= Pos(bx, -GAP, BOLT_Z) * extrude(Plane.XZ * roof, NUT_DEPTH)

    # --- elephant-foot chamfer on the print bed face (-X end)
    if EDGE_CHAMFER: part = chamfer(part.edges().filter_by_position(Axis.X, X0 - 1e-3, X0 + 1e-3), EDGE_CHAMFER)
    return part
