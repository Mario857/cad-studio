"""savings-thermometer: 300 mm wall goal tracker with 0-100 % scale and a sliding marker.

Spec: 70 x 300 x 5 mm wall plate. A raised 'thermometer' (36 mm bulb + 18 mm tube, 4 mm proud)
carries a 45° dovetail track; a separate marker with an arrow slides in it (snug fit, holds
by friction) and points at the raised scale: ticks every 10 %, labels 0/25/50/75/100 (2 mm
per %). Raised goal text at the top (GOAL_TEXT param). Two through-keyholes with front head
pockets hang it on 2 screws (head <= 8.5 mm, shank <= 4.5 mm).
Everything faces up when printed back-down, so no supports. Marker enters from the open top
of the track before hanging.

Assumptions: screws with pan/round heads ~8 mm, 60 mm apart (KEY_DX). Marker fit
MARKER_FIT 0.15 per side; if it slides by itself, reprint marker with -0.05.
2 bodies = plate + marker (intended).
"""

from build123d import *

from cadlib import *

# Coordinates = in-use orientation (hung on a wall at +Y, front facing -Y, Z up).
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(-90, 0, 30),  # back face on the bed, turned 30° to stay in the dual-nozzle area
    supports="off",
    brim="on",                       # 300 mm long flat ABS plate
)

GOAL_TEXT = "GOAL €1000"

# Plate
W = 70.0
H = 300.0
T = 5.0
CORNER_R = 8.0

# Thermometer
TUBE_X = 10.0
BULB_D = 36.0
BULB_Z = 25.0
TUBE_W = 18.0
TUBE_TOP = 272.0
RAISE = 4.0
Z0 = 55.0                   # 0 %
Z100 = 255.0                # 100 %

# Dovetail track + marker
TRACK_OPEN = 6.0            # width at the tube face
TRACK_DEPTH = 2.5           # 45° flanks: widens by 2 x depth
MARKER_FIT = 0.15           # per side
MARKER_LEN = 12.0
NECK = 1.5
HEAD_T = 3.0
ARROW_L = 24.0
ARROW_H = 9.0

# Scale + text
TICK_X0 = -8.0
TICK_X1 = -2.0
TICK_MAJOR_X0 = -11.0
TICK_W = 1.2
TICK_H = 0.8
LABEL_X = -21.0
TEXT_SIZE = 7.0
TEXT_RAISE = 0.6
GOAL_Z = 279.0

# Keyholes
KEY_DX = 60.0
KEY_Z = 290.0
KEY_HEAD_D = 9.0
KEY_SHANK_W = 4.6
KEY_TRAVEL = 8.0
KEY_POCKET_D = 11.0
KEY_POCKET_DEPTH = 2.5


def text_at(txt, x, y, size=TEXT_SIZE):
    t = label(txt, size=size, depth=TEXT_RAISE + 0.2)
    bb = t.bounding_box()
    return Pos(x - (bb.min.X + bb.max.X) / 2, y - (bb.min.Y + bb.max.Y) / 2, T - 0.2) * t


def z_of(p):
    return Z0 + (Z100 - Z0) * p / 100


def build_flat_plate():
    """built flat: X = width, Y = height (in-use Z), Z = thickness (front up)"""
    plate = extrude(Pos(0, H / 2) * RectangleRounded(W, H, CORNER_R), T)
    plate = chamfer(plate.edges().group_by(Axis.Z)[0], 0.4)
    therm = Pos(TUBE_X, BULB_Z) * Circle(BULB_D / 2) + Pos(TUBE_X, (BULB_Z + TUBE_TOP) / 2) * RectangleRounded(
        TUBE_W, TUBE_TOP - BULB_Z, TUBE_W / 2 - 0.01)
    therm = Pos(0, 0, T - 0.01) * extrude(therm, RAISE + 0.01)
    plate += therm
    # dovetail track: open at the tube face, wider below, open out of the tube top
    top = T + RAISE
    hw = TRACK_OPEN / 2
    dove = Polygon((-hw, top + 0.01), (hw, top + 0.01), (hw + TRACK_DEPTH, top - TRACK_DEPTH),
                   (-hw - TRACK_DEPTH, top - TRACK_DEPTH), align=None)
    y_lo = z_of(0) - MARKER_LEN / 2 - 2
    plate -= Pos(TUBE_X, y_lo, 0) * extrude(Plane.XZ * dove, -(H - y_lo))
    # scale
    for p in range(0, 101, 10):
        y = z_of(p)
        x0 = TICK_MAJOR_X0 if p % 25 == 0 else TICK_X0
        plate += Pos((x0 + TICK_X1) / 2, y, T - 0.2) * Box(TICK_X1 - x0, TICK_W, TICK_H + 0.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for p in (0, 25, 50, 75, 100):
        plate += text_at(str(p), LABEL_X, z_of(p))
    plate += text_at("%", LABEL_X, z_of(100) + 11)
    plate += text_at(GOAL_TEXT, 0, GOAL_Z)
    # keyholes: head hole + shank slot upward, through; head pockets on the front
    for sx in (-1, 1):
        x = sx * KEY_DX / 2
        plate -= Pos(x, KEY_Z - KEY_TRAVEL, -1) * Cylinder(KEY_HEAD_D / 2, T + 2, align=ON_BED)
        plate -= Pos(x, KEY_Z - KEY_TRAVEL / 2, -1) * Box(KEY_SHANK_W, KEY_TRAVEL, T + 2, align=ON_BED)
        plate -= Pos(x, KEY_Z, -1) * Cylinder(KEY_SHANK_W / 2, T + 2, align=ON_BED)
        pocket = Pos(x, KEY_Z - KEY_TRAVEL / 2) * SlotCenterToCenter(KEY_TRAVEL, KEY_POCKET_D, rotation=90)
        plate -= Pos(0, 0, T - KEY_POCKET_DEPTH) * extrude(pocket, KEY_POCKET_DEPTH + 1)
    return plate


def build_flat_marker():
    """built in print pose: arrow head on the bed, neck + dovetail shoe upward"""
    hw = TRACK_OPEN / 2 - MARKER_FIT
    d = TRACK_DEPTH - 0.2
    arrow = Polygon((-ARROW_L + 6, -ARROW_H / 2), (6, -ARROW_H / 2), (6, ARROW_H / 2), (-ARROW_L + 6, ARROW_H / 2),
                    (-ARROW_L, 0), align=None)
    m = extrude(arrow, HEAD_T)
    m = chamfer(m.edges().group_by(Axis.Z)[0], 0.4)
    m += Pos(0, 0, HEAD_T) * Box(2 * hw, MARKER_LEN, NECK + 0.2, align=ON_BED)
    shoe = Polygon((-hw, 0), (hw, 0), (hw + d, d), (-hw - d, d), align=None)
    m += Pos(0, MARKER_LEN / 2, HEAD_T + NECK) * extrude(Plane.XZ * shoe, MARKER_LEN)
    return m


def build():
    plate = build_flat_plate()
    marker = Pos(W / 2 + 10 + ARROW_L, 150, 0) * build_flat_marker()
    to_use = Rot(90, 0, 0)          # flat build -> hung on the wall, front toward -Y
    return [to_use * plate, to_use * marker]
