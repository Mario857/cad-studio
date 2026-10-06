"""mic-boom-clamp: C-clamp for a 15-25 mm boom tube with a flat tab for a clip-on mic.

Spec: C-shaped clamp, tube runs along X through the C (opening on +Y, tube slides in sideways).
An M5 thumb screw in a heat-set insert in the lower arm pushes the tube up into a 90-degree
V-groove in the upper arm, which self-centres any tube from 15 to 25 mm diameter.
On top stands a flat tab (TAB_T thick, TAB_H tall, full clamp width) for the mic's spring clip,
with a chamfered bead at its top edge so the clip cannot slide off.
Printed lying on its side (model X up): the whole C + tab is one in-plane profile, so the arms
and tab bend along the layers and it prints support-free.

Hardware: 1x M5 heat-set insert (M5 x 6 mm), 1x M5 x 30 thumb screw (reach 15-25 mm tubes)
with a rubber cap / felt pad on its tip so it does not mark the boom.
Assumptions: mic spring clip opens >= 9 mm (tab 5 mm, bead 8 mm) and is <= 24 mm wide;
mic + clip <= 300 g; boom tube round, 15-25 mm.
"""

from build123d import *

from cadlib import *

META = dict(
    material="PETG",
    quality="strong",
    standing=False,
    loads=[],
    print_orientation=(0, 90, 0),  # on its side: C-profile on the bed, arms bend along layers
    supports="off",
    brim="auto",
)

# Parameters
W = 24.0            # clamp width along the tube (X)
TUBE_MAX = 25.0     # largest boom tube diameter
SPINE_T = 7.0       # back spine thickness (Y)
BOT_T = 9.0         # lower arm thickness (holds M5 insert)
TOP_T = 6.0         # upper arm material above the V apex
V_DEPTH = 9.0       # V-groove depth into the upper arm (90 deg V)
GAP = 27.0          # opening between lower arm and upper arm underside (>= TUBE_MAX + 2)
TUBE_Y = 15.0       # tube / screw axis distance from the spine inner face
ARM_L = 27.0        # arm length from the spine inner face
CORNER = 3.0        # 45-deg inner-corner gussets
OUT_C = 2.0         # outer corner chamfers
TAB_T = 5.0         # mic tab thickness (Y)
TAB_H = 30.0        # mic tab height above the clamp top
BEAD_T = 8.0        # retaining bead thickness at the tab top
BEAD_H = 4.0        # bead straight height
TAB_GUSSET = 3.0    # 45-deg fillets at the tab root

Z_UND = BOT_T + GAP           # upper arm underside
Z_APEX = Z_UND + V_DEPTH      # V apex
Z_TOP = Z_APEX + TOP_T        # clamp top


def build() -> Part:
    yv = TUBE_Y
    c, g = OUT_C, CORNER
    body = [
        (-SPINE_T + c, 0), (ARM_L - c, 0), (ARM_L, c), (ARM_L, BOT_T),
        (g, BOT_T), (0, BOT_T + g), (0, Z_UND - g), (g, Z_UND),
        (yv - V_DEPTH, Z_UND), (yv, Z_APEX), (yv + V_DEPTH, Z_UND),
        (ARM_L, Z_UND), (ARM_L, Z_TOP - c), (ARM_L - c, Z_TOP),
        (-SPINE_T + c, Z_TOP), (-SPINE_T, Z_TOP - c), (-SPINE_T, c),
    ]
    sk = Polygon(*body, align=None)
    # mic tab centred over the V apex, with root gussets and a chamfered retaining bead
    t, b = TAB_T / 2, BEAD_T / 2
    zb = Z_TOP + TAB_H - BEAD_H - (b - t)  # bead flare start
    tab = [
        (yv - t - TAB_GUSSET, Z_TOP - 0.5), (yv + t + TAB_GUSSET, Z_TOP - 0.5),
        (yv + t + TAB_GUSSET, Z_TOP), (yv + t, Z_TOP + TAB_GUSSET), (yv + t, zb),
        (yv + b, zb + (b - t)), (yv + b, Z_TOP + TAB_H - 1), (yv + b - 1, Z_TOP + TAB_H),
        (yv - b + 1, Z_TOP + TAB_H), (yv - b, Z_TOP + TAB_H - 1), (yv - b, zb + (b - t)),
        (yv - t, zb), (yv - t, Z_TOP + TAB_GUSSET), (yv - t - TAB_GUSSET, Z_TOP),
    ]
    sk += Polygon(*tab, align=None)
    part = extrude(Plane.YZ * sk, W / 2, both=True)
    # M5 thumb screw: heat-set insert from the bottom face, axis vertical at the tube centre.
    # Horizontal when printed -> teardrop with tip toward model -X (= up on the bed).
    td = teardrop_hole(METRIC["M5"]["insert_d"], 2 * BOT_T + 2, along="Y", tip="-X")
    part -= Pos(0, yv, 0) * Rot(90, 0, 0) * td
    return part
