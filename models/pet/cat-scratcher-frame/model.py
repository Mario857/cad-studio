"""cat-scratcher-frame: slanted floor frame for a replaceable corrugated-cardboard scratch insert.

Spec:
- Holds a 300 x 100 x 50 mm corrugated-cardboard strip stack (replaceable insert) tilted
  10 deg along its length (ramp). Pocket 301 x 101 mm (0.5 mm clearance per side); side rails
  and end walls hold the bottom LIP_H = 15 mm of the insert, the rest is free to scratch.
- Ladder structure, all walls vertical (or 10 deg off vertical), open bottom: two wedge side
  rails (4 mm), six 3 mm cross plates under the insert and two end walls. Prints without
  supports in the in-use orientation; no bridges except the foot-recess ceilings (12.7 mm).
- Finger notches in both end walls make it easy to lift the insert out for replacement.
- Anti-slip: 4 corner pads with 13.3 mm x 1.6 mm recesses for standard self-adhesive
  12.7 mm rubber/silicone bumpers (bumper sticks out ~1.5 mm and carries the frame).
- Long axis along Y: the frame is ~314 mm long, so it fits the 320 mm Y axis (bbox 143 x 315.5 x 75.4 mm) of the H2C in
  one piece (no split needed); print_orientation is fixed to the in-use pose for that reason.

Hardware: corrugated-cardboard strips glued/banded into a 300 x 100 x 50 mm stack (or a
commercial refill of that size); 4 self-adhesive rubber/silicone bumpers 12.7 mm dia.

Pet safety: ABS must not hold food or water directly and is NOT a chew toy. All top/outer
edges are filleted, the bed edges have a 0.4 mm chamfer, every feature is >= 3 mm, and there are
no gaps a paw can get stuck in (cross-plate spaces are covered by the insert and open at the bottom).
Replace the cardboard before the cat scratches down to the plastic.

Assumptions: cat up to ~6 kg jumping on it (4 mm rails / 3 mm plates are ample in ABS);
insert of nominal 300 x 100 x 50 mm (real cardboard varies +-1 mm, POCKET_CLR covers that);
bumper size 12.7 mm (most common); low end of the insert 8 mm above the floor.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=True,
    loads=[dict(at=(0, 0, 60), grams=4000)],   # cat standing on the middle of the ramp
    print_orientation=(0, 0, 0),   # in-use pose: long axis on the 320 mm Y axis, walls vertical
    supports="off",                 # only the 12.7 mm foot-recess ceilings bridge (<= 15 mm)
    brim="on",                      # long thin ABS rails on the bed: brim against warping
)

# Parameters
INSERT_L = 300.0
INSERT_W = 100.0
INSERT_H = 50.0
POCKET_CLR = 0.5          # clearance per side around the insert
SLOPE = 10.0              # deg, insert tilt along its length
LOW_CLEAR = 8.0           # insert bottom height above floor at the low end
LIP_H = 15.0              # how much of the insert height the walls hold
RAIL_T = 4.0              # side rail thickness
END_T = 3.0               # end wall thickness
PLATE_T = 3.0             # cross plate thickness
PLATES = 6                # cross plates under the insert
NOTCH_W = 40.0            # finger notch width in the end walls
NOTCH_D = 11.0            # finger notch depth (from wall top)
FOOT_D = 12.7             # bumper diameter
FOOT_RECESS_D = FOOT_D + 0.6
FOOT_RECESS_H = 1.6
PAD_D = 22.0              # foot pad (boss) diameter
PAD_H = 6.0               # pad height
FILLET_R = 1.2            # top edge rounding (<= half the 3 mm end wall)
CORNER_R = 4.0            # outer vertical corner radius
BED_CH = 0.4

L_IN = INSERT_L + 2 * POCKET_CLR
W_IN = INSERT_W + 2 * POCKET_CLR
L_OUT = L_IN + 2 * END_T
W_OUT = W_IN + 2 * RAIL_T
DEEP = 120.0              # how far walls extend below the insert (trimmed by the floor)


def _tray() -> Part:
    """Frame in insert coordinates: insert bottom on w=0, length along Y, centred."""
    outer = Box(W_OUT, L_OUT, DEEP + LIP_H, align=(Align.CENTER, Align.CENTER, Align.MAX))
    outer = Pos(0, 0, LIP_H) * fillet(outer.edges().filter_by(Axis.Z), CORNER_R)
    pocket = Box(W_IN, L_IN, DEEP + LIP_H + 2, align=(Align.CENTER, Align.CENTER, Align.MAX))
    body = outer - Pos(0, 0, LIP_H + 1) * pocket
    body = fillet(body.edges().group_by(Axis.Z)[-1], FILLET_R)          # top rim edges
    # cross plates supporting the insert bottom
    pitch = L_IN / PLATES
    for i in range(PLATES):
        y = -L_IN / 2 + pitch * (i + 0.5)
        body += Pos(0, y, 0) * Box(W_IN + 0.2, PLATE_T, DEEP, align=(Align.CENTER, Align.CENTER, Align.MAX))
    # finger notches (U shaped) in both end walls
    for s in (-1, 1):
        r = NOTCH_W / 2
        cut = Pos(0, 0, LIP_H - NOTCH_D + r) * Box(NOTCH_W, END_T * 3, NOTCH_D + 5,
                                                   align=(Align.CENTER, Align.CENTER, Align.MIN))
        cut += Pos(0, 0, LIP_H - NOTCH_D + r) * Rot(90, 0, 0) * Cylinder(r, END_T * 3)
        body -= Pos(0, s * (L_OUT - END_T) / 2, 0) * cut
    return body


def build() -> Part:
    body = Rot(SLOPE, 0, 0) * _tray()   # +X rotation lifts the +Y end
    # put the low end of the insert bottom at LOW_CLEAR above the floor
    y_low = -L_IN / 2
    z_low = y_low * math.sin(math.radians(SLOPE))
    body = Pos(0, 0, LOW_CLEAR - z_low) * body
    body = body & Box(1000, 1000, 1000, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # foot pads at the four corners, outside the rails
    yb = body.bounding_box()
    pads = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            x = sx * (W_OUT / 2 + PAD_D / 2 - RAIL_T - 1)
            y = sy * ((yb.max.Y - yb.min.Y) / 2 - PAD_D / 2) + (yb.max.Y + yb.min.Y) / 2
            pads.append((x, y))
    body = chamfer(body.edges().group_by(Axis.Z)[0], BED_CH)
    for x, y in pads:
        pad = Cylinder(PAD_D / 2, PAD_H, align=ON_BED)
        pad = fillet(pad.edges().group_by(Axis.Z)[-1], FILLET_R)
        pad = chamfer(pad.edges().group_by(Axis.Z)[0], BED_CH)
        body += Pos(x, y, 0) * pad
    for x, y in pads:
        body -= Pos(x, y, -0.01) * Cylinder(FOOT_RECESS_D / 2, FOOT_RECESS_H + 0.01, align=ON_BED)
    return body
