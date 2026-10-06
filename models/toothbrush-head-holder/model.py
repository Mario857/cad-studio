"""toothbrush-head-holder: wall rack for 4 Oral-B-style electric toothbrush replacement heads.

Spec: a back plate screwed (2x countersunk M4 wood screws) or taped (flat back, adhesive pad)
to the wall, with a drained ledge at its foot. Four vertical, slightly tapered pegs stand on
the ledge; each replacement head slides down over a peg like it does on the handle shaft.
Water drains everywhere:
  - ledge top slopes LEDGE_SLOPE_DEG away from the wall and ends in an open front edge (no lip);
  - two through-slots beside every peg (DRAIN_*), right under the head's skirt, so drips fall
    straight through;
  - back-plate top is a 45 deg ridge, peg collars and tips are conical: no flat pads anywhere.
Coordinates: wall plane = XZ at y=0, part extends to +Y, Z up, bottom of the ledge on z=0.

MEASURE BEFORE PRINTING (stem / peg fit):
  Measure the bore of one of YOUR heads with calipers (and its D-flat, if any) and adjust:
  - PEG_D_TIP / PEG_D_BASE: peg diameter at top / at the collar. Default 4.9 -> 5.3 mm for a
    ~5.5 mm bore (head should slide on with light friction, stop on the taper, not wobble).
    Too tight -> reduce both by 0.1-0.2; too loose -> raise PEG_D_BASE.
  - PEG_FLAT: distance from peg axis to the key flat (2.1 mm). Set PEG_FLAT >= PEG_D_BASE/2
    (e.g. 9) to make a plain round peg if the head has no D-flat or won't go on.
  - PEG_FLAT_ANGLE: direction the flat faces (0 = toward the wall, 180 = away) so the
    bristles face the way you want.
  - PEG_H: peg length above the collar; must be <= bore depth of the head (default 16 mm).
  Tip: print one copy with only the pegs (or test on the full part, it is ~1.5 h) before a batch.

Assumptions: heads are ~Oral-B size (skirt Ø ~14-17 mm, ~60 mm tall); PEG_PITCH 28 mm keeps
neighbouring heads apart. Screws: 2x M4 (or #8) countersunk, 30-40 mm, with wall plugs.
Printed upright (in-use orientation): pegs vertical (round & accurate), all drain slots vertical.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,            # wall mounted
    loads=[],                  # heads weigh ~3 g each, negligible
    print_orientation=(0, 0, 0),  # upright: pegs vertical for a round, accurate fit
    supports="auto",
    brim="auto",
)

# Layout
N_PEGS = 4
PEG_PITCH = 28.0          # centre-to-centre of the pegs
SIDE_MARGIN = 14.0        # peg centre to side edge
WIDTH = N_PEGS * PEG_PITCH - PEG_PITCH + 2 * SIDE_MARGIN

# Back plate
BACK_T = 4.0              # plate thickness
BACK_H = 64.0             # total height (top ridge point)
SCREW_HOLES = True        # False -> plain flat back for an adhesive pad
SCREW = "M4"
SCREW_Z = 50.0            # height of the screw holes
SCREW_X = PEG_PITCH       # +- from centre (between pegs 1/2 and 3/4)

# Ledge
LEDGE_D = 34.0            # depth from the wall
LEDGE_T_BACK = 7.0        # thickness at the back plate
LEDGE_SLOPE_DEG = 6.0     # top slopes down away from the wall
PEG_Y = BACK_T + 15.0     # peg axis distance from the wall

# Drains: two slots beside each peg, running front-to-back
DRAIN_W = 5.0             # slot width (X)
DRAIN_GAP = 4.5           # peg axis to inner slot edge (leaves a 9 mm spine under the peg)
DRAIN_Y0 = BACK_T + 3.0   # slot start (from wall)
DRAIN_Y1 = LEDGE_D - 4.0  # slot end

# Peg (see MEASURE BEFORE PRINTING)
PEG_D_BASE = 5.3
PEG_D_TIP = 4.9
PEG_H = 16.0              # above the collar
PEG_FLAT = 2.1            # axis-to-flat distance; >= PEG_D_BASE/2 disables the flat
PEG_FLAT_ANGLE = 0.0      # 0: flat faces the wall
PEG_TIP_CHAMFER = 1.2     # conical lead-in at the top
COLLAR_D = 9.0            # conical collar at the peg root (no flat shelf)
COLLAR_H = 2.0

CHAMFER_BED = 0.4


def ledge_top_z(y: float) -> float:
    return LEDGE_T_BACK - (y - BACK_T) * math.tan(math.radians(LEDGE_SLOPE_DEG))


def peg(x: float) -> Part:
    z0 = ledge_top_z(PEG_Y + COLLAR_D / 2) - 0.5   # root sunk into the sloped ledge
    zc = ledge_top_z(PEG_Y - COLLAR_D / 2) + COLLAR_H  # collar top above highest ledge point
    body_h = PEG_H - PEG_TIP_CHAMFER
    r_b, r_t = PEG_D_BASE / 2, PEG_D_TIP / 2
    collar = Pos(0, 0, z0) * Cone(COLLAR_D / 2, r_b, zc - z0, align=ON_BED)
    shaft = Pos(0, 0, zc) * Cone(r_b, r_t, body_h, align=ON_BED)
    tip = Pos(0, 0, zc + body_h) * Cone(r_t, max(r_t - PEG_TIP_CHAMFER, 0.6),
                                        PEG_TIP_CHAMFER, align=ON_BED)
    p = collar + shaft + tip
    if PEG_FLAT < r_b:
        # remove material beyond the flat, only on the shaft (collar stays round)
        cut = Pos(PEG_FLAT + 5, 0, zc + 0.01) * Box(10, 20, PEG_H + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
        cut = Rot(0, 0, -90 - PEG_FLAT_ANGLE) * cut   # angle 0 -> flat toward -Y (wall)
        p = p - cut
    return Pos(x, PEG_Y, 0) * p


def build() -> Part:
    yf = LEDGE_D
    zf = ledge_top_z(yf)
    prof = Polygon(
        (0, 0), (yf, 0), (yf, zf), (BACK_T, LEDGE_T_BACK),
        (BACK_T, BACK_H - BACK_T), (0, BACK_H), align=None,
    )
    body = extrude(Plane.YZ * prof, WIDTH / 2, both=True)
    body = chamfer(body.edges().group_by(Axis.Z)[0], CHAMFER_BED)

    xs = [(i - (N_PEGS - 1) / 2) * PEG_PITCH for i in range(N_PEGS)]
    for x in xs:
        body = body + peg(x)

    slot_l = DRAIN_Y1 - DRAIN_Y0
    for x in xs:
        for s in (-1, 1):
            cx = x + s * (DRAIN_GAP + DRAIN_W / 2)
            cutter = Pos(cx, (DRAIN_Y0 + DRAIN_Y1) / 2, LEDGE_T_BACK + 1) * Rot(0, 0, 90) * slot(slot_l, DRAIN_W, LEDGE_T_BACK + 2)
            body = body - cutter

    if SCREW_HOLES:
        for sx in (-SCREW_X, SCREW_X):
            body = body - Pos(sx, BACK_T, SCREW_Z) * Rot(-90, 0, 0) * bolt_hole(SCREW, BACK_T + 1, head="csk")
    return body
