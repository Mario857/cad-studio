"""advent-calendar: tree-shaped wall advent calendar with 24 numbered open-top pockets.

Spec: Christmas-tree board (stepped branch outline + trunk + star) carrying 24 open-top pockets,
each sized for a 40 x 40 x 25 mm sweet/gift lying flat (40 wide, 40 deep, 25 tall). Rows from the
top: 1, 2, 3, 4, 5, 6 pockets + a 3-pocket trunk row = 24. Numbers 1..24 (shuffled) are raised
0.8 mm on the board above each pocket, ~6.5 mm tall digits. The board is too tall for the
300 x 320 plate, so it is split into two stacked tiers at a thickened joint rail: 3 alignment
pins (3 mm dowel) in teardrop holes along Z, and each tier half of the rail has 2 counterbored M3
holes so both tiers screw to the wall independently. The star has a 5 mm nail hole.
Print: back face down (print_orientation (-90,0,0)); pockets rise straight up, their front faces
are full 45-degree gables (no bridges), so it prints with zero supports. Numbers sit on the board
just above each pocket (visible above the sweet). One tier per plate: TIER = 1 is the committed
out/*.3mf; set TIER = 2 and re-run ./cad check advent-calendar for plate 2 (PASS: 3h10m, 89.6 g).

Assumptions:
- Wall-hung (standing=False): screws/nails hold it; the brief allowed wall OR standing.
- Sweet lies flat 40x40 footprint, 25 tall; 1 mm clearance per side; it slides in over the 14 mm
  lip, so each row leaves 41.4 mm insertion height below the next row.
- Pins: 3 mm steel dowel / cut 3 mm rod, 20 mm long, glued (CA/epoxy) after alignment.
- Pocket floor is a short cantilever with layer lines across its root; loads are ~50 g per
  pocket, the U-shaped wall/floor channel is plenty for that.
- Number order is a fixed shuffle (NUMBERS list), edit it to taste.
- The two tiers do not fit one 300x320 plate together (tier 1 alone 296 mm wide), so TIER selects
  which one build() returns; print both.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,            # wall-hung
    loads=[],
    print_orientation=(-90, 0, 0),  # back face on the bed, pockets up
    supports="off",
    brim="auto",
)

# --- Sweet / pocket -----------------------------------------------------------------
SWEET_W = 40.0          # X
SWEET_D = 40.0          # Y (depth from wall)
SWEET_H = 25.0          # Z
POCKET_CLEAR = 1.0      # per side
WALL = 2.0              # pocket wall thickness
FLOOR = 2.4             # pocket floor thickness
LIP_H = 14.0            # pocket wall height above floor
FRONT_FLAT = 0.0        # inner flat front width (0 = full 45-degree gable, no bridge)
POCKET_GAP = 2.0        # gap between neighbouring pockets
INSERT_CLEAR = 2.6      # space above sweet-over-lip envelope to next row

# --- Board --------------------------------------------------------------------------
PLATE_T = 2.4           # back plate thickness
EDGE_M = 5.0            # plate margin beside pockets
BASE_M = 3.0            # plate margin below trunk pockets
CHAMFER = 0.4           # elephant-foot chamfer (back edges, on bed)
ROWS = [1, 2, 3, 4, 5, 6]   # pockets per branch row, top to bottom
TRUNK = 3                   # pockets in the trunk row
SPLIT_AFTER_ROW = 4         # tier joint sits above this branch row
STAR_R = 30.0
STAR_RI = 13.0
STAR_T = 4.0
NAIL_D = 5.0

# --- Joint rail / pins / screws ------------------------------------------------------
RAIL_T = 8.0            # rail thickness (Y) incl. back plate
RAIL_HALF = 12.0        # rail height per tier (Z)
PIN_D = 3.0             # dowel diameter
PIN_FIT = "snug"
PIN_DEPTH = 10.0        # into each tier
PIN_X = (-55.0, 0.0, 55.0)
SCREW = "M3"
SCREW_X = (-28.0, 28.0)
TIER = 1                # which tier to build/print: 1 = trunk + rows 6-4, 2 = rows 3-1 + star

# --- Numbers ------------------------------------------------------------------------
NUM_SIZE = 9.0          # font size -> ~6.5 mm digits
NUM_DEPTH = 0.8
NUM_Z = FLOOR + SWEET_H + 8.3   # number centre above pocket bottom, on the board above the sweet
NUMBERS = [17,
           3, 22,
           9, 14, 1,
           20, 6, 11, 24,
           2, 15, 8, 19, 5,
           12, 23, 4, 16, 10, 21,
           7, 18, 13]   # top row first, left to right, trunk last

# --- derived -------------------------------------------------------------------------
IN_W = SWEET_W + 2 * POCKET_CLEAR
IN_D = SWEET_D + 2 * POCKET_CLEAR
POCKET_H = FLOOR + LIP_H
PITCH_X = IN_W + 2 * WALL + POCKET_GAP
PITCH_Z = FLOOR + LIP_H + SWEET_H + INSERT_CLEAR   # 44.0
JOINT_Z = FLOOR + LIP_H + SWEET_H + 1.6 + 2 * RAIL_HALF


def _pocket():
    """Pocket at origin: back at y=-PLATE_T, centered X, bottom z=0, opening up."""
    ch = (IN_W - FRONT_FLAT) / 2
    y0 = -PLATE_T + 3.0  # inner extends into the plate, trimmed later
    yb = -PLATE_T - IN_D
    tip = [(0, yb - ch)] if FRONT_FLAT <= 0 else [(-FRONT_FLAT / 2, yb - ch), (FRONT_FLAT / 2, yb - ch)]
    inner = Polygon((-IN_W / 2, y0), (-IN_W / 2, yb), *tip, (IN_W / 2, yb), (IN_W / 2, y0), align=None)
    outer = offset(inner, WALL, kind=Kind.INTERSECTION)
    walls = extrude(outer - inner, POCKET_H)
    floor = extrude(outer, FLOOR)
    p = walls + floor
    trim = Pos(0, -PLATE_T - 100, 0) * Box(300, 200, 100, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return p & trim


def _row_positions():
    """[(z_bottom, [x...])] for every row, bottom (trunk) first, plus joint z."""
    rows = []
    z = BASE_M
    rows.append((z, [(i - (TRUNK - 1) / 2) * PITCH_X for i in range(TRUNK)]))
    joint = None
    for k in reversed(ROWS):
        z += PITCH_Z
        if k == SPLIT_AFTER_ROW - 1:
            z += JOINT_Z - PITCH_Z
        rows.append((z, [(i - (k - 1) / 2) * PITCH_X for i in range(k)]))
    zs = {len(xs): zb for zb, xs in rows[1:]}
    joint = zs[SPLIT_AFTER_ROW] + FLOOR + LIP_H + SWEET_H + 1.6 + RAIL_HALF
    return rows, joint


def _outline(rows):
    """Stepped tree outline in XZ (list of faces)."""
    shapes = []
    zb0, xs0 = rows[0]
    hw = max(xs0) + PITCH_X / 2 - POCKET_GAP / 2 + EDGE_M
    shapes.append(Polygon((-hw, 0), (hw, 0), (hw, rows[1][0]), (-hw, rows[1][0]), align=None))
    for idx in range(1, len(rows)):
        zb, xs = rows[idx]
        hw = max(xs) + PITCH_X / 2 - POCKET_GAP / 2 + EDGE_M
        z_top = rows[idx + 1][0] - BASE_M + 1 if idx + 1 < len(rows) else zb + PITCH_Z + 10
        nxt = (len(xs) - 1) * PITCH_X / 2 - PITCH_X / 2 if len(xs) > 1 else 0
        top_hw = max(nxt + 6, 6)
        z_sh = min(zb + NUM_Z + 5, z_top - 1)   # keep full width behind the numbers
        shapes.append(Polygon((-hw, zb - BASE_M), (hw, zb - BASE_M), (hw, z_sh),
                              (top_hw, z_top), (-top_hw, z_top), (-hw, z_sh), align=None))
    return shapes


def _star(cz):
    import math
    pts = []
    for i in range(10):
        r = STAR_R if i % 2 == 0 else STAR_RI
        a = math.radians(90 + 36 * i)
        pts.append((r * math.cos(a), cz + r * math.sin(a)))
    return Polygon(*pts, align=None)


def build():
    rows, z_joint = _row_positions()
    sk = _outline(rows)
    outline = Sketch() + sk
    try:
        plate = chamfer(extrude(Plane.XZ * outline, PLATE_T).edges().group_by(Axis.Y)[-1], CHAMFER)
    except Exception:  # stepped relief instead of a chamfer
        plate = extrude(Plane.XZ * offset(outline, -CHAMFER), CHAMFER) + \
            Pos(0, -CHAMFER, 0) * extrude(Plane.XZ * outline, PLATE_T - CHAMFER)
    top_z = rows[-1][0] + PITCH_Z + 10
    star_cz = top_z + STAR_R * 0.55
    star = extrude(Plane.XZ * _star(star_cz), STAR_T)
    star = chamfer(star.edges().group_by(Axis.Y)[-1], CHAMFER)
    plate = plate + star
    plate = plate - Pos(0, 0, star_cz) * Rot(90, 0, 0) * Pos(0, 0, -50) * Cylinder(
        hole_d(NAIL_D) / 2, 100, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # joint rail: thickened band of the plate outline
    band = Pos(0, 0, z_joint - RAIL_HALF) * Box(400, 100, 2 * RAIL_HALF,
                                                align=(Align.CENTER, Align.CENTER, Align.MIN))
    rail_full = Pos(0, -CHAMFER, 0) * extrude(Plane.XZ * outline, RAIL_T - CHAMFER)
    plate = plate + (rail_full & band)

    pocket = _pocket()
    body = plate
    nums = list(NUMBERS)
    order = [rows[i] for i in range(len(rows) - 1, 0, -1)] + [rows[0]]  # top row first, trunk last
    labels = []
    for zb, xs in order:
        for x in xs:
            body = body + Pos(x, 0, zb) * pocket
            n = str(nums.pop(0))
            t = Rot(90, 0, 0) * label(n, size=NUM_SIZE, depth=NUM_DEPTH)
            bb = t.bounding_box()
            cx, cz = (bb.min.X + bb.max.X) / 2, (bb.min.Z + bb.max.Z) / 2
            labels.append(Pos(x - cx, -PLATE_T + 0.01, zb + NUM_Z - cz) * t)
    for t in labels:
        body = body + t

    # split into tiers
    big = 2000
    lower = body & Box(big, big, z_joint, align=(Align.CENTER, Align.CENTER, Align.MIN))
    upper = body & Pos(0, 0, z_joint) * Box(big, big, big, align=(Align.CENTER, Align.CENTER, Align.MIN))

    pin_cd = clearance(PIN_D, PIN_FIT)
    for px in PIN_X:
        h = Pos(px, -RAIL_T / 2, z_joint) * teardrop_hole(pin_cd, 2 * PIN_DEPTH, along="Z", tip="-Y")
        lower = lower - h
        upper = upper - h
    for sx in SCREW_X:
        for zz, which in ((z_joint - RAIL_HALF / 2, "l"), (z_joint + RAIL_HALF / 2, "u")):
            c = Pos(sx, -RAIL_T, zz) * Rot(90, 0, 0) * bolt_hole(SCREW, RAIL_T, head="socket")
            if which == "l":
                lower = lower - c
            else:
                upper = upper - c

    # one tier per plate (both together exceed 300 x 320)
    return lower if TIER == 1 else Pos(0, 0, -z_joint) * upper
