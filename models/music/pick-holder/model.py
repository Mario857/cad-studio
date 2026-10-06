"""pick-holder: mic-stand clamp with 6 spring-flex guitar pick slots.

Spec: clamps onto a vertical mic-stand tube (OD 18-25 mm). The clamp is a C-frame open
toward +Y: the tube slides in between a fixed jaw with a 120 deg V-seat (centres any OD,
captures the tube) and a flexing pressure leaf. An M5 thumb screw, threaded into a
drop-in hex nut in the outer arm, pushes the leaf's rigid pad against the tube. The leaf
is a 40 mm cantilever, so its ~10 mm of travel (25 mm tube entry -> 18 mm tube clamped)
stays at ~1.5 % strain. Behind the clamp a comb holds 6 picks upright (pick plane YZ,
9.5 mm pitch): each slot is two flex leaves with staggered vertical bumps (0.4 mm
interference + pick thickness) so a pick snaps in from the top and pulls straight out.
A stop bar under each slot sets insertion depth (~14 mm in, ~16 mm exposed).

Felt: 1.0 mm deep recesses on both V faces and on the leaf pad for self-adhesive felt
(1.0-1.5 mm). Use FELT or cork, not rubber: some rubbers/plasticizers react with
nitrocellulose finishes - the same rule applies to anything that may touch a guitar.
Nothing on this part touches the guitar except the picks; exposed frame edges are
filleted >= 1 mm anyway.

Print: flat as modelled (Z up). Both the clamp leaf and the pick leaves bend in the XY
plane, i.e. along the layers. No supports needed.

Hardware: 1x M5 x 30 thumb screw (knurled/wing) or M5 x 30 bolt, 1x M5 hex nut
(dropped into the slot from the top), self-adhesive felt sheet ~1-1.5 mm.

Assumptions: tube is vertical, OD 18-25 mm; felt 1-1.5 mm thick; standard 351/teardrop
picks ~26-30 mm wide, 0.46-1.5 mm thick; ABS+ leaf strain OK for occasional re-clamping.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="Guitar Core ABS+ 0.20mm @BBL H2C",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # flat: all flex members bend along layers
    supports="off",
    brim="auto",
)

# --- Parameters ---------------------------------------------------------------------
H = 24.0                 # clamp / comb height (tube axis direction, Z)
TUBE_MAX = 25.0          # largest mic-stand OD
TUBE_MIN = 18.0          # smallest mic-stand OD
FELT_RECESS = 1.0        # depth of felt pockets
FELT_MARGIN = 2.0        # pocket inset from top/bottom faces
FILLET = 1.0             # top-edge fillet
FILLET_V = 1.2           # vertical-edge fillet (differs from FILLET: equal radii break the mesh)

BACK_T = 6.0             # back wall (Y) thickness
JAW_T = 6.0              # fixed jaw wall behind the V apex
V_DEPTH = 4.0            # V-seat depth (120 deg included)
V_HALF = V_DEPTH * 3**0.5  # half-width of the V mouth (120 deg)
TUBE_Y = 55.0            # tube / screw / pad centre line (Y)
FRAME_L = 64.0           # length of the C-frame arms (Y)

LEAF_T = 2.4             # flex leaf thickness
PAD_T = 6.0              # rigid pad thickness (X)
PAD_L = 18.0             # pad length (Y)
PAD_FACE_X = 30.5        # pad inner face at rest (V apex = x 0): 25 mm tube can enter
SCREW_GAP = 2.5          # gap pad/leaf -> screw arm
ARM_T = 10.0             # screw arm thickness (X)

SCREW_D = 5.5            # M5 clearance (nut carries the thread)
NUT_AF = 8.0             # M5 nut across flats
NUT_AC = 9.24            # M5 nut across corners
NUT_T = 4.0              # M5 nut thickness
NUT_FIT = 0.2               # extra clearance on nut slot

# Pick comb
PICKS = 6
PICK_PITCH = 9.5
PICK_SLOT = 2.8          # printed slot width between a leaf pair
PICK_LEAF_T = 1.8        # pick flex-leaf thickness
PICK_LEAF_L = 28.0       # leaf length (Y), ~pick width
BUMP_R = 1.6             # bump protrusion into slot (2x1.6 - 2.8 = 0.4 interference)
BUMP_Y = (-22.0, -14.0)  # staggered bump positions (left leaf, right leaf)
STOP_W = 1.6             # pick stop bar width (0.6 gap each side)
STOP_L = 10.0
STOP_H = 10.0            # pick bottom rests here -> ~14 mm inserted


def build() -> Part:
    x_jaw0 = -JAW_T
    x_face = V_DEPTH                                   # fixed jaw inner face
    x_pad_out = PAD_FACE_X + PAD_T
    x_arm0 = x_pad_out + SCREW_GAP
    x_arm1 = x_arm0 + ARM_T
    width = x_arm1 - x_jaw0
    xc = (x_jaw0 + x_arm1) / 2

    def box(x0, x1, y0, y1, z0=0.0, z1=H):
        return Pos((x0 + x1) / 2, (y0 + y1) / 2, z0) * Box(
            x1 - x0, y1 - y0, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # ---- C-frame + flex leaf, as one 2D profile ----
    prof = (
        Pos(xc, BACK_T / 2) * Rectangle(width, BACK_T)
        + Pos((x_jaw0 + x_face) / 2, FRAME_L / 2) * Rectangle(x_face - x_jaw0, FRAME_L)
        + Pos((x_arm0 + x_arm1) / 2, FRAME_L / 2) * Rectangle(ARM_T, FRAME_L)
        + Pos(x_pad_out - LEAF_T / 2, (BACK_T + TUBE_Y) / 2)
        * Rectangle(LEAF_T, TUBE_Y - BACK_T)
        + Pos(PAD_FACE_X + PAD_T / 2, TUBE_Y) * Rectangle(PAD_T, PAD_L)
    )
    vee = Polygon((0, TUBE_Y), (x_face + 2, TUBE_Y + V_HALF + 2 * 3**0.5),
                  (x_face + 2, TUBE_Y - V_HALF - 2 * 3**0.5), align=None)
    prof = prof - vee
    frame = extrude(prof, H)
    frame = fillet(frame.edges().filter_by(Axis.Z), FILLET_V)
    frame = fillet(frame.edges().group_by(Axis.Z)[-1], FILLET)
    frame = chamfer(frame.edges().group_by(Axis.Z)[0], 0.4)

    # ---- felt recesses ----
    felt_h = H - 2 * FELT_MARGIN
    vee_recess = offset(Polygon((0, TUBE_Y), (x_face, TUBE_Y + V_HALF - 1),
                                (x_face, TUBE_Y - V_HALF + 1), align=None), FELT_RECESS)
    vee_cut = Pos(0, 0, FELT_MARGIN) * extrude(vee_recess, felt_h)
    frame -= vee_cut - box(x_face, x_face + 3, TUBE_Y - 20, TUBE_Y + 20)
    frame -= box(PAD_FACE_X - 1, PAD_FACE_X + FELT_RECESS, TUBE_Y - PAD_L / 2 + 2,
                 TUBE_Y + PAD_L / 2 - 2, FELT_MARGIN, H - FELT_MARGIN)

    # ---- thumb screw + drop-in nut ----
    x_nut = (x_arm0 + x_arm1) / 2
    zc = H / 2
    frame -= Pos(x_nut, TUBE_Y, zc) * teardrop_hole(SCREW_D, ARM_T + 2, along="X")
    nut_z0 = zc - NUT_AF / 2 - NUT_FIT
    frame -= box(x_nut - (NUT_T + 0.4) / 2, x_nut + (NUT_T + 0.4) / 2,
                 TUBE_Y - (NUT_AC + 0.4) / 2, TUBE_Y + (NUT_AC + 0.4) / 2, nut_z0, H + 1)

    # ---- pick comb behind the back wall ----
    comb = None
    for i in range(PICKS):
        cx = xc + (i - (PICKS - 1) / 2) * PICK_PITCH
        for side, by in ((-1, BUMP_Y[0]), (1, BUMP_Y[1])):
            lx = cx + side * (PICK_SLOT / 2 + PICK_LEAF_T / 2)
            leaf = box(lx - PICK_LEAF_T / 2, lx + PICK_LEAF_T / 2, -PICK_LEAF_L, 1.5)
            face_x = cx + side * PICK_SLOT / 2
            leaf += Pos(face_x, by, 0) * Cylinder(
                BUMP_R, H, align=(Align.CENTER, Align.CENTER, Align.MIN))
            comb = leaf if comb is None else comb + leaf
        comb += box(cx - STOP_W / 2, cx + STOP_W / 2, -STOP_L, 1.5, 0, STOP_H)
    comb = chamfer(comb.edges().group_by(Axis.Z)[0], 0.3)
    return frame + comb
