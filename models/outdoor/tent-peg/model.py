"""tent-peg: 180 mm Y-profile tent peg with cord hook notch and pull hole (set of 6).

Spec: Y-profile stake for guylines / tent corners. For soft/medium ground (turf, forest
soil, sand-ish loam); use metal pegs in rocky or frozen ground. Pointed tip, solid head
collar to push/tap on, cord hook notch cut into the stem just below the head (hook angles
toward the tip so the line cannot ride up and off), and a pull hole through the head for a
short cord loop to extract the peg.

Model coords: in-use, peg vertical, tip at z=0, head at z=PEG_L. Y profile = one stem
pointing -Y plus two arms at +/-ARM_ANGLE from +Y (an asymmetric "Y" with an 80 deg V so it
prints support-free).

Printing: lies on its side, long axis horizontal (layers run along the length = bending
strength). print_orientation (90,0,0) maps model +Y -> up, so the stem edge rests on the bed
and the two arms rise at 40 deg from vertical (overhang <= 45 deg, no supports). The tip
taper keeps the bed line and narrows from the sides/top only, so the point sits on the
stem edge (slightly off-axis) rather than on the centre line - needed for zero supports.

Assumptions:
- Guyline / cord <= 3 mm diameter (hook notch NOTCH_W wide); pull loop cord <= 4 mm.
- Loaded areas (stem, arms near head, hook) are ARM_T = 2.8 mm thick (>= 2 mm rule).
- Push in by hand/foot or tap gently with a rock; do not hammer hard on ABS.
- Stem edge carries a 45 deg bead (FOOT_W) for bed contact and stiffness.
- Material ABS+ (UV/heat tolerant, less brittle than PLA in the cold).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[],
    print_orientation=(90, 0, 0),  # long axis horizontal, stem edge on bed, arms up
    supports="off",
    brim="on",      # ABS, long thin bed contact: brim against warping/lift
    copies=6,
)

# Parameters
PEG_L = 180.0        # overall length
ARM_T = 2.8          # flange thickness (stem and arms), loaded -> >= 2 mm
ARM_L = 13.0         # arm length from centre to tip
ARM_ANGLE = 40.0     # arm angle from +Y (deg); 40 -> 40 deg overhang in print
STEM_L = 11.0        # stem length from centre (points -Y, bed side in print)
FOOT_W = 6.4         # stem-edge bead width (bed contact / stability, I-beam flange)
TIP_L = 45.0         # taper length of the point
TIP_W = 0.6          # half-width of the point at z=0
TIP_H = 1.2          # height of the point above the stem edge at z=0
HEAD_L = 14.0        # solid head collar length
PULL_D = 5.0         # pull hole (teardrop) diameter, for <= 4 mm cord
PULL_Y = 1.5         # pull hole position in the collar (model Y)
NOTCH_W = 3.6        # hook notch width (cord <= 3 mm + clearance)
NOTCH_Z = 160.0      # notch entry height at the stem edge
NOTCH_INNER = 4.0    # notch inner end distance from centre (stem keeps this much)
NOTCH_SLOPE = 50.0   # notch rise angle vs. axial-normal (>45 -> support-free in print)


def _profile_pts():
    a = math.radians(ARM_ANGLE)
    d = (math.sin(a), math.cos(a))
    n = (math.cos(a), -math.sin(a))
    h = ARM_T / 2
    r_out = (ARM_L * d[0] + h * n[0], ARM_L * d[1] + h * n[1])
    r_in = (ARM_L * d[0] - h * n[0], ARM_L * d[1] - h * n[1])
    return a, r_out, r_in


def _y_section() -> Part:
    a, _, _ = _profile_pts()
    stem = Pos(0, -STEM_L / 2, 0) * Rectangle(ARM_T, STEM_L)
    arm = Pos(0, ARM_L / 2, 0) * Rectangle(ARM_T, ARM_L)
    right = Rot(0, 0, -ARM_ANGLE) * arm
    left = Rot(0, 0, ARM_ANGLE) * arm
    hub = Circle(ARM_T / 2)
    fh = (FOOT_W - ARM_T) / 2  # 45 deg flanks
    foot = Polygon((-FOOT_W / 2, -STEM_L), (FOOT_W / 2, -STEM_L), (ARM_T / 2, -STEM_L + fh),
                   (-ARM_T / 2, -STEM_L + fh), align=None)
    return stem + right + left + hub + foot


def _hull_section():
    _, r_out, r_in = _profile_pts()
    f = FOOT_W / 2
    pts = [
        (f, -STEM_L),
        r_out,
        r_in,
        (-r_in[0], r_in[1]),
        (-r_out[0], r_out[1]),
        (-f, -STEM_L),
    ]
    return Polygon(*pts, align=None)


def build() -> Part:
    body = extrude(_y_section(), PEG_L - HEAD_L)
    collar = Pos(0, 0, PEG_L - HEAD_L) * extrude(_hull_section(), HEAD_L)
    peg = body + collar

    big = 50.0
    # Side taper (planes vertical in print -> no overhang)
    side = Polygon((-TIP_W, 0), (TIP_W, 0), (big, TIP_L), (big, PEG_L + 1),
                   (-big, PEG_L + 1), (-big, TIP_L), align=None)
    side_cut = extrude(Plane.XZ * side, big, both=True)
    # Top taper (model +Y = up in print; upward-facing slope)
    y0 = -STEM_L + TIP_H
    top = Polygon((-STEM_L - 5, 0), (y0, 0), (big, TIP_L), (big, PEG_L + 1),
                  (-STEM_L - 5, PEG_L + 1), align=None)
    top_cut = extrude(Plane.YZ * top, big, both=True)
    peg = peg & side_cut & top_cut

    # Cord hook notch in the stem: enters at the stem edge, angles toward the tip.
    y_e, y_i = -STEM_L - 3, -NOTCH_INNER - NOTCH_W / 2
    dr = y_i - y_e
    dz = dr / math.tan(math.radians(NOTCH_SLOPE))
    ln = math.hypot(dr, dz)
    ang = -math.degrees(math.atan2(dz, dr))
    notch = extrude(
        Plane.YZ * Pos((y_e + y_i) / 2, NOTCH_Z - dz / 2) * Rot(0, 0, ang)
        * SlotCenterToCenter(ln, NOTCH_W),
        ARM_T + 2, both=True)
    peg = peg - notch

    # Pull hole through the head collar (horizontal in print -> teardrop, point to +Y = up)
    hole = Pos(0, PULL_Y, PEG_L - HEAD_L / 2) * Rot(-90, 0, 0) * teardrop_hole(PULL_D, 40, along="X")
    peg = peg - hole
    return peg
