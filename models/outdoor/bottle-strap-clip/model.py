"""bottle-strap-clip: backpack-strap holder that hangs a 1 L soft bottle / Smartwater by its neck.

Spec: a rectangular loop slides onto a shoulder-strap webbing (strap runs vertically through the
loop, along Z). From the loop's front wall a horizontal fork plate sticks out (+Y, away from the
wearer) ending in an open C-clip. The bottle neck is pushed horizontally into the C (snap past the
arm tips, lead-in chamfered); the neck ring then rests on top of the plate and the bottle hangs
below. Two gussets tie the plate to the loop's front wall. Load 1 kg.

Coordinates (in use): Z up along the strap, -Y = wearer, webbing slot at y 0..SLOT_T.

Strength / orientation: printed flat as modelled (plate on the bed). Then the C arms flex in-plane
during snap-in (stress along the arm = along layers), the plate bends as a cantilever under the
bottle with stress along Y (in-layer), and the gussets + 4 mm front wall carry the moment.

Snap sizing (ABS): arm radial width 4.5 mm, 6 mm tall; opening = neck - 2.5 mm -> ~1.25 mm tip
deflection per arm over ~25 mm arm => ~1.3 % strain, below ABS yield (~3 %).

Assumptions:
- Webbing 50 mm x up to 3 mm thick (WEB_W 25..50 param); slot adds 1 mm (W) / 1 mm (T) clearance.
  The strap end must be threaded through the closed loop once (stronger than an open hook; it can't
  drop off in the field).
- Neck below the ring 29 mm (NECK_D, 28..32 param), ring ~34 mm; free neck height between ring and
  bottle shoulder >= 6 mm (FORK_T = 6). Smartwater 1 L fits these.
- 1 kg static; sections >= 3 mm everywhere loaded.
"""

from build123d import *

from cadlib import *

# Parameters --------------------------------------------------------------------------------
WEB_W = 50.0          # webbing width (25..50)
WEB_T = 3.0           # webbing thickness
WEB_CLR_W = 1.0       # slot extra width
WEB_CLR_T = 1.0       # slot extra thickness
LOOP_H = 22.0         # loop height along strap (Z)
BACK_T = 3.0          # back bar (between strap and wearer)
FRONT_T = 4.0         # front wall (carries fork moment)
SIDE_T = 3.5          # loop side walls

NECK_D = 29.0         # bottle neck diameter under the ring (28..32)
NECK_CLR = 0.6        # diametral clearance of the C bore
SNAP = 2.5            # opening is this much narrower than NECK_D
RING_W = 4.5          # radial width of the C arms
FORK_T = 6.0          # plate / C thickness (Z)
LEAD = 3.0            # lead-in flare at the mouth (per side)
RING_D = 34.0         # bottle neck-ring diameter (kept clear of gussets)

RIB_T = 3.0           # gusset thickness
RIB_H = 14.5          # gusset height above the plate (>= rib length -> face <= 45 deg)

# Derived
SLOT_W = WEB_W + WEB_CLR_W
SLOT_T = WEB_T + WEB_CLR_T
LOOP_X = SLOT_W + 2 * SIDE_T
LOOP_Y = BACK_T + SLOT_T + FRONT_T
Y_FRONT = SLOT_T + FRONT_T                 # outer face of the front wall
R_IN = (NECK_D + NECK_CLR) / 2
R_OUT = R_IN + RING_W
YC = Y_FRONT + R_OUT + 2.0                 # C centre
OPEN_W = NECK_D - SNAP

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[dict(at=(0, YC, FORK_T), grams=1000)],
    print_orientation=(0, 0, 0),   # flat: arms + plate bend along layers
    supports="off",
    brim="auto",
)


def build() -> Part:
    # Strap loop
    loop = Pos(0, (Y_FRONT - BACK_T) / 2, 0) * rounded_box(LOOP_X, LOOP_Y, LOOP_H, radius=2)
    slot_cut = Pos(0, SLOT_T / 2, -1) * Box(SLOT_W, SLOT_T, LOOP_H + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    loop = loop - slot_cut

    # Fork plate with C-clip
    y0 = Y_FRONT - 1.0
    plate_sk = Pos(0, (y0 + YC) / 2) * Rectangle(2 * R_OUT, YC - y0) + Pos(0, YC) * Circle(R_OUT)
    plate_sk -= Pos(0, YC) * Circle(R_IN)
    ys = YC + (R_IN**2 - (OPEN_W / 2) ** 2) ** 0.5 - 0.5
    ye = YC + R_OUT + 1.0
    plate_sk -= Polygon(
        (-OPEN_W / 2, ys), (OPEN_W / 2, ys), (OPEN_W / 2 + LEAD, ye), (-OPEN_W / 2 - LEAD, ye), align=None
    )
    plate = extrude(plate_sk, FORK_T)
    plate = chamfer(plate.edges().group_by(Axis.Z)[0], 0.4)
    # round the arm tips / outer top edge lightly for comfort
    try:
        plate = fillet(plate.edges().group_by(Axis.Z)[-1], 0.8)
    except Exception:
        pass

    # Gussets on top of the plate, outside the neck-ring footprint
    rib_len = max(4.0, YC - Y_FRONT - ((RING_D / 2 + 1.5) ** 2 - (R_OUT - RIB_T) ** 2) ** 0.5 if (RING_D / 2 + 1.5) > (R_OUT - RIB_T) else YC - Y_FRONT - 2)
    ribs = Part()
    for sx in (-1, 1):
        ribs += Pos(sx * (R_OUT - RIB_T / 2), Y_FRONT - 0.5, FORK_T - 0.5) * Rot(0, 0, 90) * rib(rib_len + 0.5, RIB_H + 0.5, RIB_T)

    return loop + plate + ribs
