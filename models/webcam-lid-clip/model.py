"""webcam-lid-clip: clip-on external webcam mount for laptop lids, 1/4"-20 stud, tilt hinge.

Spec: a U-clip hooks over the top edge of a laptop lid (lid plane = XZ, lid between y=0 and
y=GAP). The short front jaw rests on the screen bezel, the long back jaw carries an M4 heat-set
insert + M4 thumb screw that clamps lids 4-12 mm thick (GAP 13 mm, screw travel ~9 mm).
One hinge ear on top (+X edge) carries a separate tilting platform: lap-type friction hinge
(axis along X), M4 bolt through the ear into an M4 heat-set insert in the platform knuckle;
tighten to set tilt friction. The platform captures a 1/4"-20 hex-head bolt head in a hex
pocket on its underside; the shank pokes up as the camera stud.
Two separate bodies (clip + platform) are intended; both print together lying on their side
(model X up) so the jaws, ear and platform bend along the layers and print support-free.

Hardware: 2x M4 heat-set insert (M4 x 5 mm); 1x M4 x 16 thumb screw (lid clamp) with a felt or
rubber pad on its tip; 1x M4 x 12 socket/thumb screw + washer (hinge);
1x 1/4"-20 x 3/8" hex-head bolt (stud ~6 mm) (7/16" AF head, glue/epoxy in the pocket); felt on the jaws.
Assumptions: lid 4-12 mm thick, bezel >= 8 mm tall (front jaw drop FRONT_DROP); webcam <= 150 g;
1/4"-20 hex bolt head 11.1 mm AF x 4.4 mm high.
"""

from build123d import *

from cadlib import *

META = dict(
    material="PLA",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 90, 0),  # lie on side: U-profile on the bed, jaws bend along layers
    supports="off",
    brim="auto",
)

# Parameters - clip
W = 30.0            # clip width along the lid edge (X)
GAP = 13.0          # jaw opening (lid 4-12 mm + pad)
FRONT_T = 4.0       # front (screen-side) jaw thickness
FRONT_DROP = 8.0    # front jaw length below the lid edge
BACK_T = 8.0        # back jaw thickness (holds the M4 insert)
BACK_DROP = 32.0    # back jaw length below the lid edge
BRIDGE_T = 5.0      # top bridge thickness
SCREW_Z = 12.0      # thumb screw height above the back jaw bottom
# Parameters - hinge
EAR_T = 6.0         # hinge ear thickness (X)
EAR_R = 7.0         # ear / knuckle radius around the hinge axis
AXIS_H = 9.0        # hinge axis height above bridge top
HINGE_CLR = 0.25    # side clearance knuckle-to-ear
# Parameters - platform
PLATE_L = 36.0      # platform length (Y)
PLATE_T = 8.0       # platform thickness
PLATE_GAP = 2.0     # plate underside clearance above the knuckle
STUD_OFFSET = 13.0  # 1/4" stud offset from hinge axis (Y, toward screen side)
NECK_W = 8.0        # neck between knuckle and plate (Y)
QTR_AF = 11.5       # 1/4"-20 hex head pocket across flats (11.1 + clearance)
QTR_HEAD_H = 4.6    # pocket depth
QTR_CLEAR = 6.8     # 1/4" shank clearance
PLATFORM_SHIFT = 45.0  # platform placed beside the clip on the bed (Y)

TOP = BACK_DROP + BRIDGE_T  # bridge top (z)
Y0 = -FRONT_T               # clip front face
Y1 = GAP + BACK_T           # clip back face
YC = (Y0 + Y1) / 2          # hinge axis y
ZC = TOP + AXIS_H           # hinge axis z


def _yz_extrude(sketch_pts, width):
    """Polygon in the YZ plane, extruded symmetric along X."""
    prof = Polygon(*sketch_pts, align=None)
    return extrude(Plane.YZ * prof, width / 2, both=True)


def _clip() -> Part:
    # U profile: front jaw, bridge, back jaw (Y, Z) with 45-degree chamfers on outer corners
    c = 2.0
    pts = [
        (Y0, BACK_DROP - FRONT_DROP), (0, BACK_DROP - FRONT_DROP), (0, BACK_DROP),
        (GAP, BACK_DROP), (GAP, 0), (Y1, 0), (Y1, TOP - c), (Y1 - c, TOP),
        (Y0 + c, TOP), (Y0, TOP - c),
    ]
    clip = _yz_extrude(pts, W)
    # single hinge ear on the +X edge (sits on the bed when printed -> no overhang)
    ear_sk = Pos(YC, (TOP - 1 + ZC) / 2) * Rectangle(2 * EAR_R, ZC - TOP + 1)
    ear_sk += Pos(YC, ZC) * Circle(EAR_R)
    clip += Pos(W / 2 - EAR_T / 2, 0, 0) * extrude(Plane.YZ * ear_sk, EAR_T / 2, both=True)
    # M4 hinge bolt clearance hole through the ear (head on the outer +X face)
    clip -= Pos(0, YC, ZC) * Rot(0, 90, 0) * Cylinder(hole_d(4.5) / 2, W + 2)
    # thumb screw insert in the back jaw, entering from the back face
    # (teardrop, tip toward model -X = up when printed; insert melts into the round part)
    clip -= Pos(0, (GAP + Y1) / 2, SCREW_Z) * teardrop_hole(
        METRIC["M4"]["insert_d"], BACK_T + 2, along="Y", tip="-X")
    return clip


def _platform() -> Part:
    """Lap-hinge platform: knuckle + neck + plate, one profile extruded along X."""
    x1 = W / 2 - EAR_T - HINGE_CLR  # face that bears on the ear
    x0 = -W / 2
    zb = ZC + EAR_R + PLATE_GAP     # plate underside
    ys = YC - STUD_OFFSET           # stud position (screen side of the axis)
    y_front = ys - PLATE_L / 2
    y_back = YC + NECK_W / 2 + 3
    c = 1.5
    plate = Polygon((y_front + c, zb), (y_back - c, zb), (y_back, zb + c),
                    (y_back, zb + PLATE_T - c), (y_back - c, zb + PLATE_T),
                    (y_front + c, zb + PLATE_T), (y_front, zb + PLATE_T - c),
                    (y_front, zb + c), align=None)
    sk = plate + Pos(YC, ZC) * Circle(EAR_R)
    sk += Pos(YC, (ZC + zb) / 2 + 0.5) * Rectangle(NECK_W, zb - ZC + 1)
    p = Pos((x0 + x1) / 2, 0, 0) * extrude(Plane.YZ * sk, (x1 - x0) / 2, both=True)
    # M4 hinge: clearance through the knuckle, heat-set insert from the ear-facing face
    p -= Pos(0, YC, ZC) * Rot(0, 90, 0) * Cylinder(hole_d(4.5) / 2, W + 2)
    p -= Pos(x1, YC, ZC) * Rot(0, -90, 0) * insert_hole("M4")
    # 1/4"-20 stud: shank hole + hex head pocket from below (vertex along X = up when printed)
    p -= Pos(0, ys, zb + PLATE_T + 1) * Cylinder(QTR_CLEAR / 2, PLATE_T + 2,
                                                 align=(Align.CENTER, Align.CENTER, Align.MAX))
    rc = QTR_AF / 2 / 0.8660254  # hex circumradius
    hex_sk = Rot(0, 0, 30) * RegularPolygon(rc, 6)  # flats face +/-X
    hex_sk += Polygon((QTR_AF / 2 - 0.01, rc / 2), (QTR_AF / 2 + rc / 2, 0),
                      (QTR_AF / 2 - 0.01, -rc / 2), align=None)  # 45 deg roof (print ceiling)
    p -= Pos(0, ys, zb - 0.01) * extrude(hex_sk, QTR_HEAD_H)
    # print layout: flip 180 deg about Z so the far (-X) face lands on the bed beside the clip
    p = Rot(0, 0, 180) * Pos(0, -YC, -zb) * p
    return Pos(W / 2 - (-x0), PLATFORM_SHIFT, 0) * p


def build():
    return [_clip(), _platform()]
