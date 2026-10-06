"""toothpaste-squeezer: wind-up roller key for squeezing toothpaste tubes.

Spec: a flat bar with a through slot that takes the folded crimp end of a tube up to
TUBE_W (55 mm) wide. Push the crimp through the slot, then turn the key by its rounded
two-lobe wings (wind-up-key style) to roll the tube up around the bar.
Prints flat on the bed: the slot is a vertical through-cut, so no supports, no bridges.
Assumptions: crimp is 0.5-1 mm thick, folded maybe double -> SLOT_GAP 2.0 mm;
SLOT_CLEARANCE 3 mm extra slot length beyond tube width; bar 16 x 8 mm is stiff enough
in ABS+ for hand torque; tip end left closed so the bar does not spread open.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # flat: slot vertical, bending torque along layers
    supports="off",
    brim="auto",
)

# Parameters
TUBE_W = 55.0          # widest tube crimp accepted
SLOT_CLEARANCE = 3.0   # extra slot length beyond TUBE_W
SLOT_GAP = 2.0         # slot width (crimp 0.5-1 mm + fold/clearance)
SLOT_CHAMFER = 0.6     # lead-in chamfer on slot top edges
END_WALL = 5.0         # solid material at the tip end of the slot
BAR_W = 16.0           # bar width (Y)
THICK = 8.0            # overall thickness (Z)
NECK_LEN = 8.0         # solid length between slot and wings
WING_R = 13.0          # radius of each wing lobe
WING_SPREAD = 14.0     # lobe centre offset from axis (Y)
WING_X = 14.0          # lobe centre distance past the neck
EDGE_R = 2.5           # top-edge rounding (comfort)
BOTTOM_CHAMFER = 0.4   # elephant-foot chamfer

SLOT_L = TUBE_W + SLOT_CLEARANCE


def build() -> Part:
    bar_len = END_WALL + SLOT_L + NECK_LEN
    # bar from x=0 (tip) to x=bar_len (start of wings)
    bar = Pos(bar_len / 2, 0) * RectangleRounded(bar_len, BAR_W, BAR_W / 2 - 0.01)
    wx = bar_len + WING_X
    lobes = (Pos(wx, WING_SPREAD) * Circle(WING_R)
             + Pos(wx, -WING_SPREAD) * Circle(WING_R)
             + Pos(wx, 0) * Rectangle(2 * WING_R, 2 * WING_SPREAD)
             + Pos(bar_len, 0) * Rectangle(2 * WING_X, BAR_W))
    outline = bar + lobes
    part = extrude(Plane.XY * outline, THICK)
    part = fillet(part.edges().group_by(Axis.Z)[-1], EDGE_R)
    part = chamfer(part.edges().group_by(Axis.Z)[0], BOTTOM_CHAMFER)

    # slot: stadium, vertical through-cut
    sx = END_WALL + SLOT_L / 2
    slot_cut = extrude(Plane.XY * (Pos(sx, 0) * SlotOverall(SLOT_L, SLOT_GAP)), THICK)
    lead = loft([
        Plane.XY.offset(THICK - SLOT_CHAMFER) * (Pos(sx, 0) * SlotOverall(SLOT_L, SLOT_GAP)),
        Plane.XY.offset(THICK) * (Pos(sx, 0) * SlotOverall(SLOT_L + 2 * SLOT_CHAMFER, SLOT_GAP + 2 * SLOT_CHAMFER)),
    ])
    part = part - slot_cut - lead
    return part
