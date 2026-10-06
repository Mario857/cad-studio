"""ip15pm-charging-station-3in1: desk charging station for iPhone 15 Pro Max + Apple Watch + AirPods Pro.

Spec: one 192 x 115 mm base carrying
- phone: portrait 65 deg back plate with an Apple MagSafe puck (Ø56 x 5.5) flush in an open-top
  U-pocket; the phone stands on two corner pads with lips. The 56 mm centre gap keeps the USB-C
  port and both speakers clear; nothing touches the side buttons; plate ends below the camera.
- watch: 36 mm wide post with the Apple Watch charger puck (Ø28 x 7.5) in a teardrop pocket on
  its front face, 60 mm up so an open band hangs around the post.
- AirPods Pro (USB-C) case: stadium cup (case stands lid-up) on a 30 mm pedestal; a USB-C plug is
  pushed up through a rectangular hole in the cup floor and plugs into the case from below.
Hidden cable routing: every cable drops through an open slit (cables lay in from above, no need
to thread plugs) into channels on the underside of the base, which merge and exit at the rear
centre. A 3-port USB-C charger (or 3 adapters) sits behind the desk.

Assumptions:
- Phone + case: 76.7 + 2*CASE by 159.9 + 2*CASE by 8.25 + 2*CASE; 221 g + ~30 g case.
- MagSafe centre ~80 mm above the bare phone's bottom edge.
- Watch puck cable leaves at its edge or back centre; both fit the 6 mm slit (rotate it down).
- AirPods Pro 2 USB-C case 60.6 x 21.7 x 45.2 mm, port centred in its bottom face.
- USB-C plug overmold <= 12.6 x 7 mm (press fit; a drop of hot glue fixes a looser one) and
  ~18 mm long; the metal tongue (6.6 mm) stands proud of the cup floor.
- Phone contact edges 0.8 mm chamfered / 1 mm filleted; stick felt on pad tops and lip backs,
  and rubber feet under the base corners (they also keep the underside channels off the desk).

MEASURE BEFORE PRINTING (unverified values):
- PHONE_W/H/T, CASE: phone in its case.  MAGSAFE_FROM_BOTTOM: snap puck on, bottom edge -> centre.
- PUCK_D/PUCK_T (MagSafe), WATCH_PUCK_D/WATCH_PUCK_T (Apple Watch charger varies by generation).
- POD_L/POD_W/POD_H: AirPods case outline.
- PLUG_W/PLUG_T/PLUG_BODY: USB-C overmold width/thickness/length of the cable you will use.
- CABLE_SLOT_W: thickest cable/strain relief.  CAM_FROM_TOP, SPEAKER_GAP as on the phone.
"""

import math

from build123d import *

from cadlib import *

# Phone / accessories
PHONE_W = 76.7
PHONE_H = 159.9
PHONE_T = 8.25
CASE = 2.5
PHONE_G = 221
CASE_G = 30 if CASE > 0 else 0
MAGSAFE_FROM_BOTTOM = 80.0
CAM_FROM_TOP = 50.0
SPEAKER_GAP = 56.0
PUCK_D, PUCK_T, PUCK_FIT = 56.0, 5.5, 0.4
WATCH_PUCK_D, WATCH_PUCK_T = 28.0, 7.5
POD_L, POD_W, POD_H = 60.6, 21.7, 45.2
POD_FIT = 0.8
PLUG_W, PLUG_T, PLUG_BODY = 12.6, 7.0, 18.0
CABLE_SLOT_W = 6.0

# Layout (X = depth, viewer at -X; Y = width)
PHONE_Y = -52.0
WATCH_Y = 24.0
POD_Y = 75.0
POD_X = 10.0
BASE_X0, BASE_X1 = -40.0, 75.0
BASE_Y0, BASE_Y1 = -97.0, 95.0
BASE_T = 9.0
CH_W = 8.0                      # underside cable channels: 45 deg gable, no flat ceiling
CH_X = 55.0                     # collector channel position
CH_WALL = 1.5                   # channel: 8 wide, 1.5 straight + 4 roof -> fits a 4 mm cable

# Phone stand
ANGLE = 65.0
LEDGE_Z = 35.0
PLATE_T = PUCK_T + 2.5
PLATE_TOP_ABOVE_PUCK = 20.0
PAD_EXTRA = 2.0
LIP_H, LIP_T, PHONE_GAP = 6.0, 3.0, 1.2

# Watch post
POST_W, POST_D = 36.0, 20.0
WATCH_Z = 60.0
POST_H = WATCH_Z + WATCH_PUCK_D / 2 + 8

# AirPods cup
CUP_WALL = 2.4
CUP_FLOOR_Z = 30.0
CUP_DEPTH = 15.0
CAVITY_H = CUP_FLOOR_Z - PLUG_BODY

PW, PT, PH = PHONE_W + 2 * CASE, PHONE_T + 2 * CASE, PHONE_H + 2 * CASE
PUCK_CX = CASE + MAGSAFE_FROM_BOTTOM
PLATE_W = PW + 2 * PAD_EXTRA
LOCAL = Pos(0, PHONE_Y, LEDGE_Z) * Rot(0, -ANGLE, 0)
_c, _s = math.cos(math.radians(ANGLE)), math.sin(math.radians(ANGLE))
_pc = (_c * (CASE + PH / 2) - _s * PT / 2, LEDGE_Z + _s * (CASE + PH / 2) + _c * PT / 2)

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[
        dict(at=(_pc[0], PHONE_Y, _pc[1]), grams=PHONE_G + CASE_G),
        dict(at=(-8, WATCH_Y, WATCH_Z), grams=40),
        dict(at=(POD_X, POD_Y, CUP_FLOOR_Z + POD_H / 2), grams=51),
    ],
    print_orientation=(0, 0, 0),  # as used: channels are 45 deg gables, everything else vertical
    supports="auto",
    brim="on",                  # ABS, 192 x 115 mm flat base
)


def phone_stand() -> Part:
    top = PUCK_CX + PLATE_TOP_ABOVE_PUCK
    plate = Pos(top, 0, 0) * Box(top + 60, PLATE_W, PLATE_T, align=(Align.MAX, Align.CENTER, Align.MAX))
    plate = chamfer(plate.edges().group_by(Axis.Z)[-1], 0.8)
    pad_w = (PLATE_W - SPEAKER_GAP) / 2
    local = plate
    for s in (-1, 1):
        leg = Box(80, pad_w, PT + PHONE_GAP + LIP_T, align=(Align.MAX, Align.CENTER, Align.MIN))
        leg = chamfer(leg.edges().group_by(Axis.X)[-1].group_by(Axis.Z)[0], 0.8)
        lip = Pos(0, 0, PT + PHONE_GAP) * Box(LIP_H, pad_w, LIP_T, align=(Align.MIN, Align.CENTER, Align.MIN))
        lip = fillet(lip.edges().group_by(Axis.X)[-1], 1.0)
        local = local + Pos(0, s * (SPEAKER_GAP / 2 + pad_w / 2), 0) * (leg + lip)
    pocket = Pos(PUCK_CX, 0, 0) * Cylinder((PUCK_D + PUCK_FIT) / 2, PUCK_T, align=(Align.CENTER, Align.CENTER, Align.MAX))
    slot_len = PUCK_D / 2 + 4 + PLATE_TOP_ABOVE_PUCK + 2
    cslot = Pos(top + 2 - slot_len / 2, 0, 0) * Box(slot_len, CABLE_SLOT_W, 3 * PLATE_T)
    return LOCAL * (local - pocket - cslot)


def watch_post() -> Part:
    post = Pos(POST_D / 2, WATCH_Y, 0) * Box(POST_D, POST_W, POST_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    post = fillet(post.edges().filter_by(Axis.Z), 4)
    post = fillet(post.edges().group_by(Axis.Z)[-1], 1.0)
    pocket = Pos(0, WATCH_Y, WATCH_Z) * teardrop_hole(WATCH_PUCK_D + 0.4, 2 * WATCH_PUCK_T, along="X")
    slit = Pos(3, WATCH_Y - CABLE_SLOT_W / 2, -1) * Box(POST_D, CABLE_SLOT_W, POST_H + 2, align=(Align.MIN, Align.MIN, Align.MIN))
    return post - pocket, slit


def pod_cup() -> Part:
    outer = extrude(Pos(POD_X, POD_Y) * SlotOverall(POD_L + POD_FIT + 2 * CUP_WALL, POD_W + POD_FIT + 2 * CUP_WALL), CUP_FLOOR_Z + CUP_DEPTH)
    outer = fillet(outer.edges().group_by(Axis.Z)[-1], 1.0)
    inner = Pos(0, 0, CUP_FLOOR_Z) * extrude(Pos(POD_X, POD_Y) * SlotOverall(POD_L + POD_FIT, POD_W + POD_FIT), 50)
    plug = Pos(POD_X, POD_Y, CAVITY_H - 1) * Box(PLUG_W, PLUG_T, PLUG_BODY + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cavity = Pos(POD_X, POD_Y, 0) * gable(30, 14, "X", wall=CAVITY_H - 7)
    return outer, inner + plug + cavity


def gable(length, width, along="X", z0=0.0, wall=0.0) -> Part:
    """Prism cutter: vertical walls `wall` high, then a 45 deg roof; bottom at z0 - 1."""
    h = width / 2
    prof = Polygon((-width / 2, -1), (width / 2, -1), (width / 2, wall), (0, wall + h), (-width / 2, wall), align=None)
    if along == "X":
        cut = extrude(Plane.YZ * prof, length / 2, both=True)
    else:
        cut = extrude(Plane.XZ * prof, length / 2, both=True)
    return Pos(0, 0, z0) * cut


def build() -> Part:
    base = Pos((BASE_X0 + BASE_X1) / 2, (BASE_Y0 + BASE_Y1) / 2, 0) * rounded_box(BASE_X1 - BASE_X0, BASE_Y1 - BASE_Y0, BASE_T, radius=10, top_radius=2)
    post, wslit = watch_post()
    cup, cup_cut = pod_cup()
    part = base + phone_stand() + post + cup
    part = part & Box(1000, 1000, 500, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # cable drops (open slits) and underside channels -> rear exit
    pslit = Pos(0, PHONE_Y - CABLE_SLOT_W / 2, -1) * Box(CH_X, CABLE_SLOT_W, BASE_T + 2, align=(Align.MIN, Align.MIN, Align.MIN))
    under = [
        Pos(CH_X, (PHONE_Y + POD_Y) / 2, 0) * gable(POD_Y - PHONE_Y + CH_W, CH_W, "Y", wall=CH_WALL),
        Pos((CH_X + BASE_X1) / 2 + 2, 0, 0) * gable(BASE_X1 - CH_X + 4, CH_W, "X", wall=CH_WALL),
        Pos((POST_D + CH_X) / 2, WATCH_Y, 0) * gable(CH_X - POST_D + 6, CH_W, "X", wall=CH_WALL),
        Pos((POD_X + CH_X) / 2, POD_Y, 0) * gable(CH_X - POD_X, CH_W, "X", wall=CH_WALL),
    ]
    part = part - pslit - wslit - cup_cut
    for u in under:
        part = part - u
    return part
