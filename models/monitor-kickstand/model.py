"""monitor-kickstand: desk stand for a 14-15.6 in portable monitor with a hinged, adjustable rear leg.

Spec: 140 x 96 mm base plate. The monitor's bottom edge drops into a 12 mm channel behind a 16 mm
front lip (low locating ridge behind it). The panel leans back onto the rounded top edge of a
100 mm wide rear leg (a plate) that pivots on a full-width hub at the back of the base, between two
cheeks. Swinging the leg sets the monitor tilt: 60 deg (leg ~vertical) .. 80 deg (leg ~25 deg
forward). Model shown/audited at TILT_DEG; the leg angle is solved so its top edge touches the panel.
The hub has a 45 deg skirt whose 7 mm flat rests on the desk (sized at 70 deg; at 60/80 deg the
skirt edge lifts the hinge end <=0.6 mm, harmless). Two bodies on purpose: base + leg.

Hardware: 2x M4x16 socket bolts + 2x M4 heat-set inserts (one in each hub end) + 2 washers.
Each bolt passes through a cheek into the hub insert; tighten until the leg holds (stepless
friction hinge, 60-80 deg). Leg and base are separate prints plated together (0.3 mm gap).

Assumptions: monitor ~700 g, 6 mm thick at the edge (channel takes up to ~10 mm), its centre of
gravity ~105 mm up the panel from the bottom edge. Worst cases checked by setting TILT_DEG to
60 (tips backward) and 80 (tips forward).
Tip angles: 20.1 deg @60, 26.4 deg @70, 18.5 deg @80 (all >= 12 deg incl. 700 g monitor).
"""

import math

from build123d import *

from cadlib import *

# Parameters
WIDTH = 140.0           # base width (X)
BASE_FRONT_Y = -14.0    # front edge of base
BASE_REAR_Y = 82.0      # rear edge of base
PLATE_T = 6.0           # base plate thickness
LIP_T = 10.0            # front lip thickness (Y)
LIP_H = 16.0            # lip height above plate
CHANNEL_W = 12.0        # monitor-edge channel width
RIDGE_T = 4.0           # rear locating ridge
RIDGE_H = 5.0

MON_T = 6.0             # monitor thickness at the edge
MON_GRAMS = 700.0
MON_COG = 105.0         # CoG distance up the panel from its bottom edge
TILT_DEG = 70.0         # monitor tilt from horizontal shown/audited (60..80)

PIVOT_Y = 70.0          # hinge axis
HUB_R = 8.0             # hub radius
HUB_FLAT = 0.4          # hub bottom flattened by this much (sits on the desk)
PIVOT_Z = HUB_R - HUB_FLAT
HUB_W = 100.0           # leg / hub width (X)
HUB_GAP = 0.3           # clearance hub-to-cheek and hub-to-plate
CHEEK_T = 8.0           # cheek thickness (X)
CHEEK_R = 10.0          # cheek radius around the pivot
LEG_T = 6.0             # leg plate thickness
LEG_REACH = 115.0       # pivot to leg top edge
WINDOW_W = 60.0         # lightening window in the leg
BOLT = "M4"
BOLT_D = 4.5            # M4 clearance

Y0 = BASE_FRONT_Y + LIP_T   # monitor bottom-front corner (against lip)
Z0 = PLATE_T                # channel floor


def _contact(tilt_deg):
    """Point on the monitor back face at LEG_REACH from the pivot."""
    th = math.radians(tilt_deg)
    c, s = math.cos(th), math.sin(th)
    by, bz = Y0 + MON_T * s, Z0 - MON_T * c          # back-face bottom
    dy, dz = by - PIVOT_Y, bz - PIVOT_Z
    b = dy * c + dz * s
    t = -b + math.sqrt(b * b - (dy * dy + dz * dz - LEG_REACH ** 2))
    return by + t * c, bz + t * s


def _cog(tilt_deg):
    th = math.radians(tilt_deg)
    c, s = math.cos(th), math.sin(th)
    return (0.0, Y0 + MON_COG * c + MON_T / 2 * s, Z0 + MON_COG * s - MON_T / 2 * c)


def leg_angle(tilt_deg=TILT_DEG):
    cy, cz = _contact(tilt_deg)
    return math.degrees(math.atan2(-(cy - PIVOT_Y), cz - PIVOT_Z))


# Coordinates = in-use orientation, Z up, mm. The audit picks the print orientation.
META = dict(
    material="PLA",
    quality="standard",
    standing=True,
    loads=[dict(at=_cog(TILT_DEG), grams=MON_GRAMS)],
    print_orientation="auto",
    supports="auto",
    brim="auto",
)


def _base() -> Part:
    depth = BASE_REAR_Y - BASE_FRONT_Y
    part = Pos(0, (BASE_FRONT_Y + BASE_REAR_Y) / 2, 0) * rounded_box(WIDTH, depth, PLATE_T, radius=6)
    in_w = WIDTH - 12
    lip = Pos(0, BASE_FRONT_Y + LIP_T / 2, PLATE_T - 1) * Box(in_w, LIP_T, LIP_H + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    lip = fillet(lip.edges().group_by(Axis.Z)[-1].filter_by(Axis.X), 3)
    ridge = Pos(0, Y0 + CHANNEL_W + RIDGE_T / 2, PLATE_T - 1) * Box(in_w, RIDGE_T, RIDGE_H + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    ridge = chamfer(ridge.edges().group_by(Axis.Z)[-1].filter_by(Axis.X).sort_by(Axis.Y)[0], 2.5)
    part = part + lip + ridge
    # notch for the hub (hub bears on the desk)
    notch_y0 = PIVOT_Y - HUB_R - 1.0
    notch = Pos(0, notch_y0, -1) * Box(HUB_W + 2 * HUB_GAP, 50, 20, align=(Align.CENTER, Align.MIN, Align.MIN))
    part = part - notch
    # cheeks on the outer strips
    prof = (Pos(PIVOT_Y - 9, PIVOT_Z / 2) * Rectangle(2 * CHEEK_R + 18, PIVOT_Z)
            + Pos(PIVOT_Y, PIVOT_Z) * Circle(CHEEK_R))
    prof = prof & Pos(0, 50) * Rectangle(400, 100)   # keep z >= 0
    cx = HUB_W / 2 + HUB_GAP + CHEEK_T / 2
    for sx in (-1, 1):
        cheek = extrude(Plane.YZ.offset(sx * cx - CHEEK_T / 2) * prof, CHEEK_T)
        cheek = chamfer(cheek.edges().group_by(Axis.Z)[0], 0.4)
        part = part + cheek
        part = part - Pos(sx * cx, PIVOT_Y, PIVOT_Z) * teardrop_hole(BOLT_D, CHEEK_T + 2, along="X")
    return part


def _leg() -> Part:
    """Pivot at origin, leg plate along +Z, thickness along Y."""
    hub = Rot(0, 90, 0) * Cylinder(HUB_R, HUB_W)
    plate_h = LEG_REACH - LEG_T / 2
    plate = Box(HUB_W, LEG_T, plate_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    top = Pos(0, 0, plate_h) * Rot(0, 90, 0) * Cylinder(LEG_T / 2, HUB_W)
    leg = hub + plate + top
    # lightening window: 45 deg pointed top so it prints without support
    w = WINDOW_W
    win = Polygon((-w / 2, 0), (w / 2, 0), (w / 2, 40), (0, 40 + w / 2), (-w / 2, 40), align=None)
    leg = leg - extrude(Plane.XZ * Pos(0, 20) * win, LEG_T, both=True)
    return leg


def build():
    a = leg_angle()
    leg = Pos(0, PIVOT_Y, PIVOT_Z) * Rot(a, 0, 0) * _leg()
    # 45 deg skirt under the hub (support-free, bears on the desk)
    k = HUB_R / math.sqrt(2)
    skirt = Polygon((-k, k), (k, k), (2 * k, 0), (0, -2 * k), (-2 * k, 0), align=None)
    skirt = Pos(0, PIVOT_Y, PIVOT_Z) * extrude(Plane.YZ * Pos(0, 0) * skirt, HUB_W / 2, both=True)
    leg = leg + skirt
    # flatten the hub where it meets the desk
    leg = leg - Box(400, 400, 10, align=(Align.CENTER, Align.CENTER, Align.MAX))
    # heat-set insert hole in each hub end
    for sx in (-1, 1):
        leg = leg - Pos(sx * (HUB_W / 2 + 0.5), PIVOT_Y, PIVOT_Z) * Rot(0, 90 * sx, 0) * insert_hole(BOLT, depth=7)
    return [_base(), leg]
