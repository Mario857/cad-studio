"""vinyl-record-shelf: "now playing" wall ledge for 12" LP sleeves, printed as 2 halves.

Spec: wall-mounted L-profile ledge (back plate + floor + front lip) that holds up to 3
12" LP sleeves (315 mm square) leaning against the wall. Total length 320 mm > 300 mm bed,
so it is split at the middle into a LEFT half (with 2 integrated alignment pegs on its split
face) and a RIGHT half (with matching pin_hole sockets). Each half has 2 countersunk M4
screw holes through the back plate (4 screws total). Design load 1 kg of sleeves.

Print orientation (strength): each half stands on its end face (model X -> print Z), so the
L-profile lies in every layer; the bending moment at the back/floor and floor/lip corners runs
along the layers instead of across them. Left half prints with its pegs pointing up, right half
with its sockets on the bed.

Assumptions:
- LP sleeve 315 mm wide, single sleeve ~3-4 mm, 3 sleeves (or 1 gatefold + 1) fit a 17 mm channel.
- Fixings: 4x M4 countersunk wood/plug screws (~30-40 mm) into wall plugs; screw heads end up
  hidden behind the sleeves. Halves may additionally be glued at the split face.
- Both halves are modeled side by side (right half offset in Y by DEPTH + LAYOUT_GAP) so the
  shared print rotation puts both on the bed; in use the right half's socket face (x=0) is
  pushed onto the left half's pegs (x=HALF_W).
- Corner chamfer inside the channel (CORNER_CH) is both a gusset and the body for the lower peg.
"""

from build123d import *

from cadlib import *

# Parameters
TOTAL_W = 320.0          # 315 mm sleeve + 5 mm
HALF_W = TOTAL_W / 2     # 160 mm per printed part
BACK_T = 8.0             # back plate thickness (Y)
BACK_H = 80.0            # back plate height (Z)
FLOOR_T = 6.0            # floor thickness (Z)
CHANNEL = 17.0           # clear depth for sleeves between back plate and lip
LIP_T = 5.0              # front lip thickness
LIP_H = 30.0             # lip top height above z=0
CORNER_CH = 10.0         # 45 deg gusset in back/floor inner corner
LIP_CH = 3.0             # 45 deg gusset in floor/lip inner corner
DEPTH = BACK_T + CHANNEL + LIP_T

SCREW = "M4"
SCREW_Z = 60.0           # screw height on back plate
SCREW_INSET = 35.0       # screw distance from each end of a half

CSK_EXTRA = 0.2          # radial clearance on the countersink

PEG_D = 5.0
PEG_L = 8.0
PEG_HOLE_DEPTH = PEG_L + 1.0
PEG_LOCS = [(BACK_T / 2, BACK_H - 15.0), (BACK_T + 2.5, FLOOR_T + 2.5)]  # (y, z)
PEG_CH = 0.6             # lead-in chamfer on peg tip
EDGE_CH = 0.4            # elephant-foot chamfer on bed (end) faces
LAYOUT_GAP = 15.0        # print layout gap between the halves (Y)

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,          # wall mounted with screws
    loads=[dict(at=(HALF_W, BACK_T + CHANNEL / 2, 160.0), grams=1000)],  # 1 kg of sleeves
    print_orientation=(0, -90, 0),  # model X -> print Z: profile in layers (strength)
    supports="auto",
    brim="on",               # tall (160 mm) narrow parts standing on end
)


def teardrop_sketch(r: float) -> Sketch:
    """Circle with a 45 deg point toward local +X (= print +Z after print rotation)."""
    sq = Pos(r * 2**0.5 / 2, 0) * Rot(0, 0, 45) * Rectangle(r, r)
    return Circle(r) + sq


def csk_teardrop() -> Part:
    """Countersunk M4 cutter pointing -Z from z=0, teardrop-shaped (tip +X) so it prints
    without supports when the hole axis is horizontal."""
    r_head = METRIC[SCREW]["csk_d"] / 2 + CSK_EXTRA
    r_shank = METRIC[SCREW]["clear"] / 2
    sink = extrude(Plane.XY * teardrop_sketch(r_head), r_head - r_shank, dir=(0, 0, -1), taper=45)
    shank = extrude(Plane.XY.offset(1) * teardrop_sketch(r_shank), BACK_T + 2, dir=(0, 0, -1))
    return sink + shank


def profile_half(length: float) -> Part:
    y0, y1, y2 = BACK_T, BACK_T + CHANNEL, DEPTH
    pts = [
        (0, 0), (y2, 0), (y2, LIP_H), (y1, LIP_H), (y1, FLOOR_T + LIP_CH),
        (y1 - LIP_CH, FLOOR_T), (y0 + CORNER_CH, FLOOR_T), (y0, FLOOR_T + CORNER_CH),
        (y0, BACK_H), (0, BACK_H),
    ]
    sk = Polygon(*pts, align=None)
    body = extrude(Plane.YZ * sk, length)  # along +X from x=0
    # countersunk screw holes from the front face of the back plate toward the wall
    for x in (SCREW_INSET, length - SCREW_INSET):
        body -= Pos(x, BACK_T, SCREW_Z) * Rot(-90, 0, 0) * csk_teardrop()
    return body


def end_chamfer(part: Part) -> Part:
    return chamfer(part.edges().group_by(Axis.X)[0], EDGE_CH)


def build():
    left = end_chamfer(profile_half(HALF_W))  # bed face of the left half = outer end
    for y, z in PEG_LOCS:
        peg = Rot(0, 90, 0) * Cylinder(PEG_D / 2, PEG_L, align=(Align.CENTER, Align.CENTER, Align.MIN))
        peg = chamfer(peg.edges().group_by(Axis.X)[-1], PEG_CH)
        left += Pos(HALF_W, y, z) * peg

    right = end_chamfer(profile_half(HALF_W))  # bed face of the right half = split face
    for y, z in PEG_LOCS:
        right -= Pos(0, y, z) * Rot(0, -90, 0) * pin_hole(PEG_D, PEG_HOLE_DEPTH)
    right = Pos(0, DEPTH + LAYOUT_GAP, 0) * right  # placed beside, both print on the bed
    return [left, right]
