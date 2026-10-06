"""coin-valet-tray: entryway valet tray 200 x 120 mm with sloped coin well, key section,
card/receipt slot and phone rest.

Spec (X = width, -Y = front towards the user):
- Coin well (left): rounded pocket tilted COIN_SLOPE so it is deepest at the front - coins gather
  where the fingers scoop them.
- Key section (front right): wide rounded pocket for keys / wallet / sunglasses.
- Card/receipt slot (back right): narrow upright slot for cards, receipts, a few notes.
- Phone rest (back): slot tilted back PHONE_TILT; the phone stands in it, screen visible.
All pockets have rounded vertical corners (POCKET_R) and filleted floors (FLOOR_R).
Prints in use orientation, no supports.

MEASURE BEFORE PRINTING: phone thickness incl. case <= PHONE_SLOT_W - 1 (default 13 mm);
bank card 85.6 x 54 mm (slot length CARD_SLOT_L).
Assumptions: solid-top tray, slicer infill keeps weight down; non-slip feet optional.
Hardware: optional 4 adhesive rubber feet 10 mm.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(30, 44, 60), grams=230), dict(at=(-69, 0, 20), grams=150)],  # phone, coins
    print_orientation=(0, 0, 0),
    supports="off",
    brim="on",                 # 200 x 120 mm ABS footprint
)

# Parameters
TRAY_L, TRAY_W, TRAY_H = 200.0, 120.0, 24.0
OUTER_R = 10.0
TOP_R = 2.0
RIM = 6.0                  # outer rim / walls between zones
POCKET_R = 7.0
FLOOR_R = 4.0
MIN_FLOOR = 2.4
COIN_W = 50.0
COIN_DEPTH_FRONT = 18.0
COIN_DEPTH_BACK = 8.0
KEY_DEPTH = 13.0
KEY_BACK_Y = 14.0          # back edge of the key pocket
CARD_SLOT_W = 6.0
CARD_SLOT_L = 92.0
CARD_SLOT_DEPTH = 18.0
CARD_SLOT_Y = 23.0         # slot centre line
PHONE_SLOT_W = 14.0
PHONE_SLOT_DEPTH = 13.0
PHONE_TILT = 15.0
PHONE_SLOT_Y = 41.0        # slot centre at the top surface
PHONE_SLOT_X0 = -38.0      # phone slot spans X0 .. right rim

X0, X1 = -TRAY_L / 2 + RIM, TRAY_L / 2 - RIM
Y0, Y1 = -TRAY_W / 2 + RIM, TRAY_W / 2 - RIM


def _pocket(lx: float, ly: float, depth: float) -> Part:
    """Rounded pocket cutter, top at z=0 extending up 20, floor filleted."""
    c = Pos(0, 0, -depth) * extrude(RectangleRounded(lx, ly, POCKET_R), depth + 20)
    return fillet(c.edges().group_by(Axis.Z)[0], FLOOR_R)


def build() -> Part:
    tray = rounded_box(TRAY_L, TRAY_W, TRAY_H, radius=OUTER_R, top_radius=TOP_R)
    # coin well, tilted about X so the front is deepest
    ly = Y1 - Y0
    slope = math.degrees(math.atan2(COIN_DEPTH_FRONT - COIN_DEPTH_BACK, ly))
    mid_depth = (COIN_DEPTH_FRONT + COIN_DEPTH_BACK) / 2
    coin = Pos((X0 + X0 + COIN_W) / 2, 0, TRAY_H) * Rot(slope, 0, 0) * _pocket(COIN_W, ly / math.cos(math.radians(slope)), mid_depth)
    tray -= coin
    # key section
    kx0 = X0 + COIN_W + RIM
    tray -= Pos((kx0 + X1) / 2, (Y0 + KEY_BACK_Y) / 2, TRAY_H) * _pocket(X1 - kx0, KEY_BACK_Y - Y0, KEY_DEPTH)
    # card / receipt slot
    tray -= Pos(X1 - CARD_SLOT_L / 2, CARD_SLOT_Y, TRAY_H) * _pocket_slot(CARD_SLOT_L, CARD_SLOT_W, CARD_SLOT_DEPTH)
    # phone rest: tilted slot
    pl = X1 - PHONE_SLOT_X0
    phone = Pos(0, 0, -PHONE_SLOT_DEPTH / math.cos(math.radians(PHONE_TILT))) * extrude(
        RectangleRounded(pl, PHONE_SLOT_W, PHONE_SLOT_W / 2 - 0.5), 40)
    phone = fillet(phone.edges().group_by(Axis.Z)[0], 2.0)
    tray -= Pos(PHONE_SLOT_X0 + pl / 2, PHONE_SLOT_Y, TRAY_H) * Rot(-PHONE_TILT, 0, 0) * phone
    return tray


def _pocket_slot(lx: float, w: float, depth: float) -> Part:
    c = Pos(0, 0, -depth) * extrude(RectangleRounded(lx, w, w / 2 - 0.2), depth + 20)
    return fillet(c.edges().group_by(Axis.Z)[0], 1.5)
