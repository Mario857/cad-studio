"""abacus: 10-row x 10-bead abacus on 3 mm metal rods; frame printed as a flat kit.

Spec (assembled): two upright end plates (12 mm thick, 202 mm tall, 80 mm feet for stability)
joined by a top and a bottom 10x10 mm rail (6x10 mm tenons, glued into 6.5 mm deep mortises) and
by ten Ø3 x 196 mm rods (in 8 mm deep blind holes, pitch 16 mm). 180 mm between the plates:
10 beads (10 mm long) per rod + 80 mm travel. Beads: Ø14 bicone (45 deg cones, prints
support-free standing up), Ø3.6 bore = free sliding on 3 mm rod.
Printed as one plate: 2 end plates lying flat (rod holes and mortises vertical, head-to-toe),
2 rails, 100 beads. Model coordinates are this print layout (not the assembled pose).

MEASURE BEFORE PRINTING: rod diameter (ROD_D, 3.0 mm; ROD_HOLE 3.2 snug + glue, BEAD_BORE 3.6).
Hardware: 10x Ø3 mm steel/brass rod, cut to ROD_LEN 196 mm; CA or epoxy glue for tenons/rods.
Assumptions: no printed rods (3 mm printed rods 196 mm long would sag and snap).
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,          # kit layout; assembled abacus stands on 80 mm feet
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="auto",
)

# Parameters
ROWS = 10
BEADS = 10
ROD_D = 3.0
ROD_HOLE = 3.2           # blind hole in the end plates (snug, glue)
ROD_HOLE_DEPTH = 8.0
BEAD_BORE = 3.6          # free slide
BEAD_D = 14.0
BEAD_L = 10.0
BEAD_CONE = 3.0          # 45 deg cones top and bottom
PITCH = 16.0             # rod spacing
INNER = 180.0            # clear span between the plates
PLATE_T = 12.0
COL_W = 22.0             # end plate column width
FOOT_L = 80.0
FOOT_H = 12.0
FOOT_RAMP = 8.0          # height of the sloped shoulder between foot and column
KIT_GAP = 2.0            # min spacing between the two head-to-toe end plates on the bed
RAIL = 10.0
TENON_W = 6.0
TENON_L = 6.0
MORTISE_CLEAR = 0.3
ROD_LEN = INNER + 2 * ROD_HOLE_DEPTH - 0.0

ROD0_Y = 34.0            # first rod above the plate bottom
RAIL_BOT_Y = 18.0
RAIL_TOP_Y = ROD0_Y + (ROWS - 1) * PITCH + 16.0
PLATE_H = RAIL_TOP_Y + 8.0


def _end_plate() -> Part:
    prof = Polygon((-FOOT_L / 2, 0), (FOOT_L / 2, 0), (FOOT_L / 2, FOOT_H), (COL_W / 2 + 8, FOOT_H + FOOT_RAMP),
                   (COL_W / 2, FOOT_H + FOOT_RAMP), (COL_W / 2, PLATE_H), (-COL_W / 2, PLATE_H),
                   (-COL_W / 2, FOOT_H + FOOT_RAMP), (-COL_W / 2 - 8, FOOT_H + FOOT_RAMP), (-FOOT_L / 2, FOOT_H),
                   align=None)
    p = extrude(prof, PLATE_T)
    p = chamfer(p.edges().group_by(Axis.Z)[0], 0.4)
    for i in range(ROWS):
        p -= Pos(0, ROD0_Y + i * PITCH, PLATE_T) * Cylinder(ROD_HOLE / 2, ROD_HOLE_DEPTH, align=(Align.CENTER, Align.CENTER, Align.MAX))
    for y in (RAIL_BOT_Y, RAIL_TOP_Y):
        p -= Pos(0, y, PLATE_T) * Box(RAIL + MORTISE_CLEAR, TENON_W + MORTISE_CLEAR, TENON_L + 0.5, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return p


def _rail() -> Part:
    r = Box(RAIL, INNER, RAIL, align=ON_BED)
    for sy in (-1, 1):
        r += Pos(0, sy * (INNER + TENON_L) / 2, 0) * Box(RAIL, TENON_L + 0.02, TENON_W, align=ON_BED)
    return chamfer(r.edges().group_by(Axis.Z)[0], 0.4)


def _bead() -> Part:
    r, rc = BEAD_D / 2, BEAD_D / 2 - BEAD_CONE
    mid = BEAD_L - 2 * BEAD_CONE
    b = Cone(rc, r, BEAD_CONE, align=ON_BED)
    b += Pos(0, 0, BEAD_CONE) * Cylinder(r, mid, align=ON_BED)
    b += Pos(0, 0, BEAD_CONE + mid) * Cone(r, rc, BEAD_CONE, align=ON_BED)
    b -= Pos(0, 0, -1) * Cylinder(BEAD_BORE / 2, BEAD_L + 2, align=ON_BED)
    return b


def build():  # kit: 2 end plates, 2 rails, ROWS*BEADS beads
    parts = []
    plate = _end_plate()
    x0, y0 = -146.0 + FOOT_L / 2, -PLATE_H / 2 - 8
    parts.append(Pos(x0, y0, 0) * plate)
    xb = x0 + COL_W + 8 + 2                 # column B sits beside column A, just past A's ramp stub
    # Head-to-toe: each column end stops KIT_GAP short of the other plate's foot ramp (it used to run into it).
    parts.append(Pos(xb, y0 + PLATE_H + FOOT_H + FOOT_RAMP + KIT_GAP, 0) * Rot(0, 0, 180) * plate)
    rail = _rail()
    xr = xb + FOOT_L / 2 + 3 + RAIL / 2
    parts.append(Pos(xr, 0, 0) * rail)
    parts.append(Pos(xr + RAIL + 3, 0, 0) * rail)
    bead = _bead()
    bp = BEAD_D + 0.8
    bx0 = xr + RAIL + 3 + RAIL / 2 + 3 + BEAD_D / 2
    for i in range(ROWS):
        for j in range(BEADS):
            parts.append(Pos(bx0 + i * bp, (j - (BEADS - 1) / 2) * bp, 0) * bead)
    return parts
