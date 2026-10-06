"""bug-crank-eater: hand-crank stink-bug eater (sweep-in, never squeeze).

Hold the comb-mouth against a wall/window and turn the crank. A 4-vane paddle wheel (D60) sweeps
the bug along the raised sill, off the 45 deg ramp and into the bin behind. The drop + 45 deg ramp is
the one-way baffle. To empty: slide the lid out backwards and dump outside.

Parts (laid out as printed, zero supports, nothing in-use oriented):
  1 box  - housing + bin, 130x120x92, 2.4 walls, 5-gap comb mouth (gaps 15 wide, 45 deg gable tops,
           total mouth ~90x29), teardrop axle holes, lid rails
  2 lid  - slides in from the back on rails, pull tab
  3 wheel- D60 4 vanes, hub with D-bore, printed standing (axis Z)
  4 crank- crank arm 60 mm + integral 8 mm D-axle (printed standing) + split snap pin
  5 knob - rotating grip, snaps onto the pin
Assumptions: axle is PRINTED, 8 mm (not 6) D-profile, round 8.25 mm teardrop holes in the box walls;
 wheel presses on the D-axle (press fit, add a drop of CA glue if it slips). Assembly: drop wheel in,
 push axle through right wall -> wheel -> left wall (flush), snap knob on. Wheel tips 1 mm off the sill.
 Mouth has no lead-in chamfer (pillars too thin), gable tops instead of a flat ceiling.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # parts already modelled exactly as printed
    supports="off",
    brim="auto",
)

# Box
W, D, H = 130.0, 120.0, 92.0
T = 2.4
SILL_Z = 22.4            # raised platform top (wheel floor)
PLAT_Y = 66.0            # platform ends, 45 deg drop into bin
RW = 4.4                 # lid rail width
LID_Z = H - 6.6          # lid underside
LID_T = 2.4
GROOVE_H = 2.6
GD = 2.4                 # groove depth into rail
# Mouth
GAPS, GAP_W, GAP_H, MOUTH_W = 5, 15.0, 22.0, 90.0
# Wheel / axle
WR = 30.0
AX_Y = 34.0
AX_Z = SILL_Z + 1.0 + WR     # 53.4
AXLE_D = 8.0
FLAT = 3.2
HOLE_D = AXLE_D + 0.25
WHEEL_HUB_D = 16.0
VANE_T = 2.4
WHEEL_L = W - 2 * T - 2.0     # 123.2 (1 mm to each wall)
VANE_L = W - 2 * T - 2 * (RW + 1.0)  # 114.4
# Crank
ARM_L, ARM_T = 60.0, 6.0
ROD_L = 1.0 + T + WHEEL_L + 1.0 + T   # 131
PIN_D, PIN_L = 8.0, 22.0
KNOB_D, KNOB_H = 18.0, 24.0


def bx(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=Align.MIN)


def d_shape(r, h):
    return Cylinder(r, h, align=ON_BED) & (Pos(FLAT - 5 - (r - 4.0) * 0, 0, 0) * Box(10, 12, h, align=ON_BED))


def make_box():
    body = bx(0, W, 0, D, 0, H)
    body = chamfer(body.edges().group_by(Axis.Z)[0], 0.4)
    body -= bx(T, W - T, T, D - T, T, H + 1)
    # platform + 45 deg ramp into bin
    body += bx(T, W - T, T, PLAT_Y, 0, SILL_Z)
    ramp = Polygon((PLAT_Y, SILL_Z), (PLAT_Y + SILL_Z - T, T), (PLAT_Y, T), align=None)
    body += Pos(W - T, 0, 0) * extrude(Plane.YZ * ramp, W - 2 * T)
    # rails: 45 deg underside, full length from front wall to back
    # side rails built from boxes + chamfer wedge via extrusion along Y
    prof = Polygon((0, LID_Z - 1.0 - RW - 0.8), (RW, LID_Z - 1.0), (RW, H), (0, H), align=None)
    railL = Pos(T, D - T, 0) * extrude(Plane.XZ * prof, D - 2 * T)
    profR = Polygon((0, LID_Z - 1.0 - RW - 0.8), (-RW, LID_Z - 1.0), (-RW, H), (0, H), align=None)
    railR = Pos(W - T, D - T, 0) * extrude(Plane.XZ * profR, D - 2 * T)
    body += railL + railR
    # front zone: lid rests on ledge, so cut side walls + rails down to lid underside
    body -= bx(0, W, T, PLAT_Y, LID_Z, H + 1)
    # back wall lowered so lid slides in
    body -= bx(-1, W + 1, D - T - 0.01, D + 1, LID_Z, H + 1)
    # lid grooves in rails (rear section)
    gl = Polygon((RW + 0.01, LID_Z), (RW + 0.01, LID_Z + GROOVE_H), (RW - GD, LID_Z + GROOVE_H + GD),
                 (RW - GD, LID_Z), align=None)
    body -= Pos(T, D + 1, 0) * extrude(Plane.XZ * gl, D + 1 - PLAT_Y)
    glr = Polygon((-RW - 0.01, LID_Z), (-RW - 0.01, LID_Z + GROOVE_H), (-RW + GD, LID_Z + GROOVE_H + GD),
                  (-RW + GD, LID_Z), align=None)
    body -= Pos(W - T, D + 1, 0) * extrude(Plane.XZ * glr, D + 1 - PLAT_Y)
    # comb mouth: gaps with 45 deg gable tops
    pitch = (MOUTH_W - GAP_W) / (GAPS - 1) + 0.0
    pillar = (MOUTH_W - GAPS * GAP_W) / (GAPS - 1)
    x0 = (W - MOUTH_W) / 2
    z0 = SILL_Z
    for i in range(GAPS):
        xa = x0 + i * (GAP_W + pillar)
        g = Polygon((xa, z0), (xa + GAP_W, z0), (xa + GAP_W, z0 + GAP_H),
                    (xa + GAP_W / 2, z0 + GAP_H + GAP_W / 2), (xa, z0 + GAP_H), align=None)
        body -= Pos(0, T + 0.01, 0) * extrude(Plane.XZ * g, T + 1.0)
    # axle holes (teardrop, horizontal)
    body -= Pos(W / 2, AX_Y, AX_Z) * teardrop_hole(HOLE_D, W + 4, along="X")
    return body


def make_lid():
    lw = W - 2 * (T + RW - GD + 0.3)
    ll = D - T - 0.3
    lid = Box(lw, ll, LID_T, align=ON_BED)
    lid = chamfer(lid.edges().group_by(Axis.Z)[0], 0.4)
    tab = Pos(0, ll / 2 - 4, LID_T) * Box(24, 8, 5, align=ON_BED)
    return lid + tab


def make_wheel():
    hub = Cylinder(WHEEL_HUB_D / 2, WHEEL_L, align=ON_BED)
    c = RW
    L = WHEEL_L
    vp = Polygon((-WR, c), (-WR + c, 0), (WR - c, 0), (WR, c), (WR, L - c), (WR - c, L), (-WR + c, L),
                 (-WR, L - c), align=None)
    v1 = Pos(0, VANE_T / 2, 0) * extrude(Plane.XZ * vp, VANE_T)
    v2 = Rot(0, 0, 90) * v1
    w = hub + v1 + v2
    w = chamfer(w.edges().group_by(Axis.Z)[0].filter_by(GeomType.CIRCLE), 0.4) if False else w
    bore = Pos(0, 0, -1) * d_shape(AXLE_D / 2 + 0.05, WHEEL_L + 2)
    return w - bore


def make_crank():
    arm = Cylinder(10, ARM_T, align=ON_BED) + Pos(0, ARM_L, 0) * Cylinder(8, ARM_T, align=ON_BED)
    arm += Pos(0, ARM_L / 2, 0) * Box(14, ARM_L, ARM_T, align=ON_BED)
    rod = Pos(0, 0, ARM_T) * d_shape(AXLE_D / 2, ROD_L)
    pin = Pos(0, ARM_L, ARM_T) * Cylinder(PIN_D / 2, PIN_L, align=ON_BED)
    head = Pos(0, ARM_L, ARM_T + PIN_L - 2.0) * (
        Cylinder(PIN_D / 2 + 0.6, 0.8, align=ON_BED) + Pos(0, 0, 0.8) * Cone(PIN_D / 2 + 0.6, 3.4, 1.2, align=ON_BED))
    slit = Pos(0, ARM_L, ARM_T + PIN_L - 12) * Box(1.2, 12, 12.1, align=ON_BED)
    return arm + rod + pin + head - slit


def make_knob():
    k = Cylinder(KNOB_D / 2, KNOB_H, align=ON_BED)
    k = chamfer(k.edges().group_by(Axis.Z)[0], 0.4)
    k = chamfer(k.edges().group_by(Axis.Z)[-1], 1.5)
    bore = Cylinder(PIN_D / 2 + 0.2, PIN_L + 0.3, align=ON_BED) + Pos(0, 0, PIN_L + 0.3) * Cone(PIN_D / 2 + 0.2, 0.5, PIN_D / 2 - 0.3, align=ON_BED)
    return k - Pos(0, 0, -0.01) * bore


def build():
    box = Pos(-W / 2, -D / 2, 0) * make_box()
    lid = Pos(0, D / 2 + 10 + (D - T - 0.3) / 2, 0) * make_lid()
    wheel = Pos(W / 2 + 40, 0, 0) * make_wheel()
    crank = Pos(W / 2 + 90, -30, 0) * make_crank()
    knob = Pos(W / 2 + 125, -30, 0) * make_knob()
    return [box, lid, wheel, crank, knob]
