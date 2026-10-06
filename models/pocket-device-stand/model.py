"""pocket-device-stand: fold-flat pocket stand for a phone or 10 in tablet, 3 click angles.

Spec:
- Base = U-frame lying flat on the table: front floor + lip (device seat) and two side rails
  that carry the outer hinge knuckles. The backrest ("leg") is hinged just behind the seat and
  folds back flat INTO the U opening, so folded the pack is 68 x 68 x 12 mm (fits 70x70x15).
- Backrest angles 45 / 60 / 75 deg from horizontal (plus a 0 deg folded click). The centre
  knuckle is a 24-gon (15 deg facets, so it sits flat on the table at every click) with axial
  detent grooves; a 2.2 mm spring beam spanning between the rails carries a bump that snaps
  into the grooves. Modelled deployed at 60 deg.
- Device seat 17 mm deep (lip inner face -> spring beam): takes a 13 mm thick phone+case
  leaning at 45..75 deg. Lip 9 mm above the floor.
- Cable slot: 14 mm notch through the lip + 12 mm channel through the floor under the seat,
  so a charging cable can exit to the front.
- Prints in one go, as modelled (in-use = print orientation, no supports): the two parts are
  separate bodies with 0.5-0.6 mm clearances; push the pin in after printing.

Hardware: 1x M3 x 70 socket screw + M3 nyloc nut as hinge pin (tighten the nut to add
friction - recommended for a 10 in tablet), or a 70 mm length of 1.75 mm filament
(melt-mushroom both ends) for a phone-only stand.

Assumptions:
- Device <= 13 mm thick incl. case, <= ~500 g (10 in tablet); load taken at the seat.
- Detent holding torque is limited (printed spring); for a heavy tablet use the M3 screw
  with the nyloc nut snugged for friction, and prefer 60/75 deg.
- PETG chosen for the spring beam (tougher than PLA under repeated flex).
- Charging cable uses a right-angle (L) plug or a slim straight plug that can bend forward
  through the floor channel.
"""

from build123d import *

from cadlib import *

META = dict(
    material="PETG",
    quality="standard",
    standing=True,
    loads=[dict(at=(0.0, -23.0, 10.0), grams=500)],  # tablet resting in the seat / on the lip
    print_orientation=(0, 0, 0),  # 2 bodies intended: base + backrest printed assembled
    supports="auto",
    brim="auto",
)

# Parameters
W = 68.0             # overall width (X)
D = 68.0             # overall depth (Y), front at -D/2
FLOOR_T = 3.0        # front floor thickness
LIP_T = 3.0          # lip wall thickness (Y)
LIP_H = 12.0         # lip top height above table
SEAT = 17.0          # device seat depth (13 mm device + margin for lean)
BEAM_T = 2.2         # detent spring beam thickness (Y)
BEAM_H = 8.0         # spring beam height
GAP = 0.5            # beam -> knuckle clearance
SIDE_GAP = 0.6       # rail -> backrest clearance
RAIL_W = 6.0         # side rail width
RAIL_H = 5.0         # side rail height
KN_A = 4.7           # knuckle apothem (= hinge axis height)
KN_SIDES = 24        # 15 deg facets
PIN_D_BASE = 3.2     # M3 pin, snug in base knuckles
PIN_D_LEG = 3.5      # M3 pin, free in backrest knuckle
LEG_T = 4.0          # backrest plate thickness
THETA = 60.0         # modelled backrest angle
CLICKS = (0.0, 45.0, 60.0, 75.0)
GROOVE_R = 1.0       # detent groove radius
BUMP_R = 0.7         # detent bump radius
CABLE_NOTCH = 14.0   # cable notch in lip
CABLE_SLOT = 12.0    # cable channel in floor
CABLE_SLOT_END = -20.0

# Derived
Y_FRONT = -D / 2
Y_LIP_IN = Y_FRONT + LIP_T
Y_BEAM_F = Y_LIP_IN + SEAT
Y_BEAM_B = Y_BEAM_F + BEAM_T
KN_R = KN_A / 0.9914448613738104          # circumradius of 24-gon (cos 7.5 deg)
Y_H = Y_BEAM_B + GAP + KN_A               # hinge axis Y
Z_H = KN_A                                # hinge axis Z
LEG_W = W - 2 * RAIL_W - 2 * SIDE_GAP     # backrest width
LEG_L = D / 2 - Y_H - 0.5                 # backrest length from axis


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, z0) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0),
                                                        align=(Align.CENTER, Align.CENTER, Align.MIN))


def knuckle(x0, x1):
    """24-gon prism along X, axis at (Y_H, Z_H), one flat facing straight down."""
    prof = RegularPolygon(KN_R, KN_SIDES, rotation=7.5)
    k = extrude(Plane.YZ * prof, x1 - x0)
    return Pos(x0, Y_H, Z_H) * k


def build_base() -> Part:
    hw = W / 2
    floor = box(-hw, hw, Y_FRONT, Y_BEAM_F - GAP - 0.1, 0, FLOOR_T)
    lip = box(-hw, hw, Y_FRONT, Y_LIP_IN, 0, LIP_H)
    rails = [box(s * (hw - RAIL_W), s * hw, Y_FRONT, D / 2, 0, RAIL_H) for s in (-1, 1)]
    beam = box(-hw + RAIL_W, hw - RAIL_W, Y_BEAM_F, Y_BEAM_B, 0, BEAM_H)
    base = floor + lip + rails[0] + rails[1] + beam
    base += knuckle(-hw, -hw + RAIL_W) + knuckle(hw - RAIL_W, hw)
    # detent bump on the back face of the beam, engaging the groove at THETA
    bump = Pos(0, Y_BEAM_B + 0.2, Z_H) * Rot(45, 0, 0) * Box(LEG_W - 4, BUMP_R * 1.4142, BUMP_R * 1.4142)
    base += bump
    # beam is a spring: free from the floor (slot in front of it handled by the GAP above)
    # cable notch + channel
    base -= box(-CABLE_NOTCH / 2, CABLE_NOTCH / 2, Y_FRONT - 1, Y_LIP_IN + 0.01, FLOOR_T, LIP_H + 1)
    base -= box(-CABLE_SLOT / 2, CABLE_SLOT / 2, Y_FRONT - 1, CABLE_SLOT_END, -1, FLOOR_T + 1)
    # pin hole (teardrop, horizontal along X)
    base -= Pos(0, Y_H, Z_H) * teardrop_hole(PIN_D_BASE, W + 2, along="X")
    # lip top chamfer
    try:
        base = chamfer(base.edges().group_by(Axis.Z)[-1], 1.0)
    except Exception:
        pass
    return base


def build_leg() -> Part:
    """Backrest in its local folded frame: axis on X through origin, plate along +Y."""
    hl = LEG_W / 2
    kn = Pos(-hl, 0, 0) * extrude(Plane.YZ * RegularPolygon(KN_R, KN_SIDES, rotation=7.5), LEG_W)
    plate = box(-hl, hl, 0, LEG_L, -KN_A, -KN_A + LEG_T)
    leg = kn + plate
    try:
        leg = fillet(leg.edges().filter_by(Axis.X).group_by(Axis.Y)[-1], 1.5)
    except Exception:
        pass
    for c in CLICKS:
        sq = GROOVE_R * 1.4142
        g = Rot(-c, 0, 0) * Pos(0, -(KN_A + 0.3), 0) * Rot(45 - THETA + c, 0, 0) * Box(LEG_W + 2, sq, sq)
        leg -= g
    return Pos(0, Y_H, Z_H) * Rot(THETA, 0, 0) * leg


def build():
    base = build_base()
    leg = build_leg()
    leg -= Pos(0, Y_H, Z_H) * teardrop_hole(PIN_D_LEG, W + 2, along="X")
    # 45 deg chamfer under the knuckle in the print/in-use pose (no support needed)
    for sgn in (-1, 1):
        a, b = Y_H + sgn * 0.62, Y_H + sgn * 12
        tri = Polygon((a - sgn * 1, -1), (b, -1), (b, abs(b - a)), align=None)  # 45 deg
        leg -= Pos(-W, 0, 0) * extrude(Plane.YZ * tri, 2 * W)
    leg = leg - base  # guarantee no overlap
    return [base, leg]
