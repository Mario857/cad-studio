"""bottle-drip-spike: soil spike that screws onto a PET bottle (PCO 1881) and drips slowly.

Spec: a threaded cap fits a standard 28 mm PCO 1881 PET bottle neck. Fill the bottle, screw the
spike on, turn it over and push the spike into the pot/soil. Water runs from the cap through a
small press-in drip insert (Ø0.8 / 1.0 / 1.2 / 1.5 mm, identified by 1-4 notches on its flange)
and down a Ø3.5 mm channel to two side outlets near the tip (side outlets don't clog with soil).
Set of 4 spikes + 4 inserts each (one of every size); 5 separate bodies per copy is intended.
Material: AzureFilm ABS PLUS. ABS+ yellows/embrittles after a season or two in full sun; the
user's "AzureFilm ASA @BBL H2C 0.4 nozzle" preset is the long-life swap (same geometry).

Assumptions:
- PCO 1881 neck: thread OD 27.4, thread root Ø25.1, pitch 2.7 mm, single start (the vent-slot
  interruptions on the neck don't matter to a continuous cap thread). All are params; tune
  THREAD_CLEAR if the fit is tight/loose.
- Cap thread depth 12 mm keeps clear of the neck's tamper bead / support ring.
- The bottle lip seats on the 45° funnel (conical line seal); a perfect seal is not needed (any thread leak
  still ends up in the soil). Drip rate also depends on air getting into the bottle: prick the
  bottle base with a pin to speed it up, leave it sealed for the slowest drip.
- Inserts are a snug press fit; pull out with tweezers via the flange.
- Prints upside down (cap opening on the bed, spike up): the cap floor is a 45° funnel and the
  thread ridges have a 45° flank so everything prints without supports.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(180, 0, 0),  # cap opening on the bed, spike tip up
    supports="off",
    brim="auto",
    copies=4,
)

# Bottle neck (PCO 1881)
NECK_THREAD_OD = 27.4
NECK_ROOT_D = 25.1
THREAD_PITCH = 2.7
THREAD_CLEAR = 0.4         # radial clearance cap thread <-> neck
THREAD_CREST = 0.5         # axial width of the cap ridge tip
THREAD_LEN = 12.0          # thread engagement depth inside the cap

# Cap
CAP_WALL = 2.4
CAP_FLOOR = 3.0            # material below the funnel at the socket
GRIP_RIBS = 18

# Drip insert
INSERT_D = 8.0
INSERT_LEN = 6.0
INSERT_FIT = "snug"
FLANGE_D = 11.0
FLANGE_T = 1.2
DRIP_HOLES = (0.8, 1.0, 1.2, 1.5)

# Spike
SPIKE_LEN = 120.0
SPIKE_TOP_D = 16.0
SPIKE_MID_D = 9.0          # at the outlet height
TIP_LEN = 22.0
CHANNEL_D = 3.5
OUTLET_D = 3.0
OUTLET_Z = 28.0            # outlet height above the tip

BORE_R = NECK_THREAD_OD / 2 + THREAD_CLEAR
CREST_R = NECK_ROOT_D / 2 + THREAD_CLEAR
CAP_OD = 2 * (BORE_R + CAP_WALL)
FUNNEL_H = BORE_R - clearance(INSERT_D, INSERT_FIT) / 2  # 45° cone from bore wall to socket; flange rests on it
SOCKET_DEPTH = INSERT_LEN + 0.5
CAP_BASE_H = SOCKET_DEPTH + FUNNEL_H + CAP_FLOOR
CAP_H = CAP_BASE_H + THREAD_LEN


def cap_thread(z0: float) -> Part:
    depth = BORE_R - CREST_R
    # (r, z) profile: flat underside, 45° top flank (overhang side when printed upside down)
    prof = Polygon(
        (BORE_R + 0.4, 0), (CREST_R, 0), (CREST_R, THREAD_CREST),
        (BORE_R, THREAD_CREST + 1.2 * depth), (BORE_R + 0.4, THREAD_CREST + 1.2 * depth), align=None,
    )
    turns_h = THREAD_LEN - THREAD_CREST - 1.2 * depth - 1.0
    helix = Helix(THREAD_PITCH, turns_h, BORE_R)
    thread = sweep(Plane.XZ * prof, path=helix, is_frenet=True)
    return Pos(0, 0, z0 + 0.5) * thread


def spike() -> Part:
    z_top = SPIKE_LEN
    body = loft([
        Plane.XY.offset(TIP_LEN) * Circle(SPIKE_MID_D / 2 * 0.85),
        Plane.XY.offset(OUTLET_Z) * Circle(SPIKE_MID_D / 2),
        Plane.XY.offset(z_top) * Circle(SPIKE_TOP_D / 2),
    ], ruled=True)
    tip = Cone(0.6, SPIKE_MID_D / 2 * 0.85, TIP_LEN, align=ON_BED)
    return body + tip


def spike_body() -> Part:
    z_cap = SPIKE_LEN
    part = spike()
    cap = Pos(0, 0, z_cap) * Cylinder(CAP_OD / 2, CAP_H, align=ON_BED)
    # grip ribs around the cap
    for i in range(GRIP_RIBS):
        rib_ = Pos(CAP_OD / 2, 0, z_cap + 2) * Box(1.6, 1.6, CAP_H - 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        cap += Rot(0, 0, i * 360 / GRIP_RIBS) * rib_
    # 45° shoulder from spike into the cap (no flat overhang either way up)
    shoulder_h = (CAP_OD - SPIKE_TOP_D) / 2
    part += cap + Pos(0, 0, z_cap - shoulder_h) * Cone(SPIKE_TOP_D / 2, CAP_OD / 2, shoulder_h, align=ON_BED)

    z_seat = z_cap + CAP_FLOOR + SOCKET_DEPTH                # socket mouth level
    z_thread = z_cap + CAP_BASE_H
    # bore + funnel + flange seat + insert socket
    # 64-gon bore: a true cylinder fused with the helical sweep meshes with open edges
    bore = extrude(RegularPolygon(BORE_R / math.cos(math.pi / 64), 64), THREAD_LEN + 1)
    part -= Pos(0, 0, z_thread) * bore
    part -= Pos(0, 0, z_seat) * Cone(clearance(INSERT_D, INSERT_FIT) / 2, BORE_R, FUNNEL_H + 0.01, align=ON_BED)
    part -= Pos(0, 0, z_seat) * Cylinder(clearance(INSERT_D, INSERT_FIT) / 2, SOCKET_DEPTH, align=(Align.CENTER, Align.CENTER, Align.MAX))
    # 45° socket floor down to the channel (no flat ceiling when printed upside down)
    sock_r = clearance(INSERT_D, INSERT_FIT) / 2
    cone_h = sock_r - hole_d(CHANNEL_D) / 2
    part -= Pos(0, 0, z_seat - SOCKET_DEPTH - cone_h) * Cone(hole_d(CHANNEL_D) / 2, sock_r, cone_h + 0.01, align=ON_BED)
    # channel down the spike
    part -= Pos(0, 0, z_seat) * Cylinder(hole_d(CHANNEL_D) / 2, z_seat - OUTLET_Z + OUTLET_D / 2, align=(Align.CENTER, Align.CENTER, Align.MAX))
    # side outlets (teardrop, tip pointing to the print-up direction = model -Z)
    part -= Pos(0, 0, OUTLET_Z) * teardrop_hole(OUTLET_D, SPIKE_MID_D + 4, along="Y", tip="-Z")
    part += cap_thread(z_thread)
    return part


def insert(hole: float, notches: int) -> Part:
    body = Cylinder(INSERT_D / 2, INSERT_LEN, align=(Align.CENTER, Align.CENTER, Align.MAX))
    body = chamfer(body.edges().group_by(Axis.Z)[0], 0.5)
    flange = Cylinder(FLANGE_D / 2, FLANGE_T, align=ON_BED)
    part = body + flange
    for i in range(notches):
        part -= Rot(0, 0, i * 30) * Pos(FLANGE_D / 2, 0, 0) * Cylinder(0.8, 3 * FLANGE_T, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    part -= Pos(0, 0, FLANGE_T) * pin_hole(hole, INSERT_LEN + FLANGE_T + 1)
    return part


def build():
    parts = [spike_body()]
    for i, h in enumerate(DRIP_HOLES):
        parts.append(Pos(CAP_OD / 2 + 10 + i * 14, 0, SPIKE_LEN + CAP_H - FLANGE_T) * insert(h, i + 1))
    return parts
