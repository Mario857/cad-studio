"""seed-dispenser: handheld seed dispenser with a 4-size rotating outlet dial and a lid.

Spec: a Ø36 mm hopper body (≈ 40 ml) whose floor is a 45° funnel leading to an off-centre
Ø5 mm outlet. A dial cup snaps over the bottom of the body (V-bead in a V-groove, 4 flex
fingers) and rotates on it; its floor has four holes Ø0.8 / 1.5 / 2.5 / 4 mm on the outlet
radius. Turn the dial until the wanted size label lines up with the arrow rib on the body; small
detent bumps click into a dimple under the body. Hold it tilted over the row and tap the body:
seeds drop one at a time through the selected hole. A slip-on lid closes the top for storage.
3 parts, printed together in the layout below (body upright, dial floor-down, lid top-down),
so model coordinates are the print poses, not the assembled pose.
Material: AzureFilm ABS PLUS. ABS+ yellows/embrittles after a season or two in full sun; the
user's "AzureFilm ASA @BBL H2C 0.4 nozzle" preset is the long-life swap (same geometry).

Assumptions:
- Dial rotates on a slide fit (DIAL_FIT) around the body; snap bead interference SNAP_BEAD.
- Lid is a snug slip fit (LID_FIT) over the body rim.
- Hole sizes cover carrot/lettuce (0.8), radish/beet (1.5-2.5) and pea/bean-sized seed (4).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),   # parts are already laid out in their print poses
    supports="off",
    brim="auto",
    copies=1,
)

# Body / hopper
BODY_OD = 36.0
BODY_WALL = 2.0
BODY_H = 78.0
OUTLET_R = 8.0          # outlet radius from the axis (= dial hole circle)
OUTLET_D = 5.0
FUNNEL_TOP_Z = 26.0     # where the 45° funnel meets the hopper wall
GROOVE_Z = 3.0          # snap groove centre above the body bottom
GROOVE_DEPTH = 0.8

# Dial
HOLES = (0.8, 1.5, 2.5, 4.0)
DIAL_FIT = "slide"
DIAL_FLOOR = 2.0
DIAL_WALL = 2.0
DIAL_RIM_H = 6.0        # cup wall height above the floor
SNAP_BEAD = 0.6         # V-bead depth on the cup inside
FINGER_SLITS = 4
SLIT_W = 1.2
FLANGE_W = 10.0         # label ring outside the cup
DETENT_R = 13.0
DETENT_D = 2.0
DETENT_H = 0.4
LABEL_SIZE = 7.5        # digit height ~5.3 mm

# Lid
LID_FIT = "snug"
LID_WALL = 2.0
LID_DEPTH = 10.0
LID_TOP = 2.0

BODY_R = BODY_OD / 2
INNER_R = BODY_R - BODY_WALL
CUP_IN_R = clearance(BODY_OD, DIAL_FIT) / 2
CUP_OUT_R = CUP_IN_R + DIAL_WALL


def body() -> Part:
    part = Cylinder(BODY_R, BODY_H, align=ON_BED)
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    # hopper: plain bore above the funnel, 45° cone (apex over the outlet) below it
    part -= Pos(0, 0, FUNNEL_TOP_Z) * Cylinder(INNER_R, BODY_H, align=ON_BED)
    z0 = FUNNEL_TOP_Z - (INNER_R + OUTLET_R - OUTLET_D / 2)   # cone throat height
    funnel = Pos(OUTLET_R, 0, z0) * Cone(OUTLET_D / 2, OUTLET_D / 2 + FUNNEL_TOP_Z - z0 + 0.01,
                                         FUNNEL_TOP_Z - z0 + 0.01, align=ON_BED)
    part -= funnel & Cylinder(INNER_R, BODY_H, align=ON_BED)
    part -= Pos(OUTLET_R, 0, z0 + 0.5) * pin_hole(OUTLET_D, z0 + 1)
    # snap V-groove
    groove = Polygon((BODY_R + 1, GROOVE_Z - GROOVE_DEPTH - 1), (BODY_R - GROOVE_DEPTH, GROOVE_Z),
                     (BODY_R + 1, GROOVE_Z + GROOVE_DEPTH + 1), align=None)
    part -= revolve(Plane.XZ * groove, Axis.Z)
    # detent dimple under the body, in line with the outlet
    part -= Pos(DETENT_R, 0, 0.6) * Cylinder(DETENT_D / 2 + 0.2, 0.6, align=(Align.CENTER, Align.CENTER, Align.MAX))
    # index arrow rib on the outside above the dial, over the outlet
    rib_z = DIAL_RIM_H + 2
    rib = Polygon((BODY_R - 0.5, rib_z), (BODY_R + 1.2, rib_z + 1.7), (BODY_R + 1.2, rib_z + 18),
                  (BODY_R - 0.5, rib_z + 18), align=None)          # 45° underside, no overhang
    part += extrude(Plane.XZ * rib, 1.0, both=True)
    return part


def dial() -> Part:
    flange_r = CUP_OUT_R + FLANGE_W
    floor = Cylinder(flange_r, DIAL_FLOOR, align=ON_BED)
    floor = chamfer(floor.edges().group_by(Axis.Z)[0], 0.4)
    cup = Pos(0, 0, DIAL_FLOOR) * (Cylinder(CUP_OUT_R, DIAL_RIM_H, align=ON_BED)
                                   - Cylinder(CUP_IN_R, DIAL_RIM_H, align=ON_BED))
    part = floor + cup
    # V-bead on the cup inside, aligned with the body groove
    zb = DIAL_FLOOR + GROOVE_Z
    bead = Polygon((CUP_IN_R + 0.2, zb - SNAP_BEAD - 0.2), (CUP_IN_R - SNAP_BEAD, zb),
                   (CUP_IN_R + 0.2, zb + SNAP_BEAD + 0.2), align=None)
    part += revolve(Plane.XZ * bead, Axis.Z)
    # flex slits make 4 snap fingers
    for i in range(FINGER_SLITS):
        a = 45 + i * 360 / FINGER_SLITS
        part -= Rot(0, 0, a) * Pos(CUP_IN_R, 0, DIAL_FLOOR) * Box(6, SLIT_W, DIAL_RIM_H + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # outlet holes, detent bumps and size labels at 90° steps
    for i, d in enumerate(HOLES):
        a = i * 90
        rot = Rot(0, 0, a)
        part -= rot * Pos(OUTLET_R, 0, DIAL_FLOOR) * pin_hole(d, DIAL_FLOOR + 1)
        part += rot * Pos(DETENT_R, 0, DIAL_FLOOR) * Cylinder(DETENT_D / 2, DETENT_H, align=ON_BED)
        txt = label(f"{d:g}", size=LABEL_SIZE, depth=0.6)
        part += rot * Pos(CUP_OUT_R + FLANGE_W / 2, 0, DIAL_FLOOR) * Rot(0, 0, -90) * txt
    return part


def lid() -> Part:
    r_in = clearance(BODY_OD, LID_FIT) / 2
    part = Cylinder(r_in + LID_WALL, LID_TOP + LID_DEPTH, align=ON_BED)
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    part -= Pos(0, 0, LID_TOP) * Cylinder(r_in, LID_DEPTH + 1, align=ON_BED)
    return part


def build():
    flange_r = CUP_OUT_R + FLANGE_W
    return [
        body(),
        Pos(BODY_R + flange_r + 8, 0, 0) * dial(),
        Pos(-(BODY_R + CUP_IN_R + LID_WALL + 8), 0, 0) * lid(),
    ]
