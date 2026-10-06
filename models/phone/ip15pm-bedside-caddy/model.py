"""ip15pm-bedside-caddy: bedside caddy for iPhone 15 Pro Max that hangs between mattress and frame.

Spec: two printed parts (laid out side by side in their print orientation):
1. Caddy (printed upright, as used): 140 x 120 mm hanging plate with
   - phone pocket (phone in its case stands USB-C down): 84.7 x 16.25 mm inside, 45 mm walls
     (buttons > 80 mm up stay free; the camera end sticks out of the top). The front wall is
     two corner posts only (56 mm window: screen, speakers and USB-C free).
   - cable slot: 14 mm slot through the pocket floor, open to the front, so a USB-C cable
     coming up from the floor can be laid in and plugged in while the phone stands in it.
   - glasses slot: 48 x 40 mm pocket, 55 mm deep; folded glasses stand on their hinge end.
   - a 12 mm block behind the top with a 4.5 mm vertical slot for the tongue's tab
     (underside 45 deg so it prints without support).
2. Tongue: 130 x 200 x 3 mm plate that goes between mattress and frame/box spring, with a
   110 x 30 x 4 mm tab at the bed-edge end. Printed flat (tab up); in use the tab points down
   and drops into the caddy's slot. The mattress weight holds it.

Assumptions:
- Phone + case 76.7 + 2*CASE by 159.9 + 2*CASE by 8.25 + 2*CASE; 221 g + ~30 g case.
- Folded glasses up to ~40 mm thick, 45 mm tall (hinge end).
- Gap between mattress and frame side is open (no headboard rail at that spot).
- Pocket rims touching the phone are 0.8 mm chamfered; a felt strip on the pocket floor pads
  and back plate avoids scuffs.

MEASURE BEFORE PRINTING (unverified values):
- PHONE_W/T, CASE: phone in its case (pocket clearance POCKET_GAP / POCKET_DEPTH_GAP).
- BUTTON_MIN_Z: lowest button above the phone's bottom edge (must be > WALL_H).
- PLUG_OVERMOLD_W: your USB-C plug width (must pass CABLE_SLOT_W).
- GLASSES_W / GLASSES_T: folded glasses at the hinge end.
- TONGUE_L: how far the tongue can go under the mattress (longer = more secure).
"""

from build123d import *

from cadlib import *

# Phone / accessories
PHONE_W = 76.7
PHONE_H = 159.9
PHONE_T = 8.25
CASE = 2.5
PHONE_G = 221
CASE_G = 30 if CASE > 0 else 0
BUTTON_MIN_Z = 80.0           # info: must be > WALL_H
PLUG_OVERMOLD_W = 12.0        # info: must be < CABLE_SLOT_W
GLASSES_W, GLASSES_T = 48.0, 40.0

# Caddy (inner face against the bed at y = 0, pockets at -Y)
POCKET_GAP = 3.0
POCKET_DEPTH_GAP = 3.0
PLATE_T = 4.0
PLATE_H = 120.0
WALL = 2.4
FLOOR_T = 3.0
WALL_H = 45.0
GLASSES_H = 55.0
WINDOW_W = 56.0
CABLE_SLOT_W = 14.0
BLOCK_D = 12.0
BLOCK_H = 36.0
# Tongue
TONGUE_W, TONGUE_L, TONGUE_T = 130.0, 200.0, 3.0
TAB_W, TAB_T, TAB_H = 110.0, 4.0, 30.0
SLOT_FIT = 0.5
LAYOUT_GAP = 30.0

PW, PT = PHONE_W + 2 * CASE, PHONE_T + 2 * CASE
P_IW, P_ID = PW + POCKET_GAP, PT + POCKET_DEPTH_GAP
G_IW, G_ID = GLASSES_W, GLASSES_T
CW = P_IW + G_IW + 3 * WALL
XP = -CW / 2 + WALL + P_IW / 2           # phone pocket centre
XG = CW / 2 - WALL - G_IW / 2            # glasses pocket centre

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[dict(at=(XP, -PLATE_T - P_ID / 2, FLOOR_T + PHONE_H / 2), grams=PHONE_G + CASE_G)],
    print_orientation=(0, 0, 0),  # parts are laid out in their print poses
    supports="auto",
    brim="on",                 # ABS: 130 x 200 mm flat tongue
)


def pocket(xc, iw, idp, h) -> Part:
    outer = Pos(xc, -PLATE_T - (idp + WALL) / 2 + 0.5, 0) * Box(iw + 2 * WALL, idp + WALL + 1, h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    inner = Pos(xc, -PLATE_T - idp / 2, FLOOR_T) * Box(iw, idp, h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    p = outer - inner
    rim = [e for e in p.edges().group_by(Axis.Z)[-1] if e.center().Y < -PLATE_T - 0.1]
    return chamfer(rim, 0.8)


def caddy() -> Part:
    plate = Pos(0, -PLATE_T / 2, 0) * Box(CW, PLATE_T, PLATE_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    plate = fillet(plate.edges().filter_by(Axis.Y).group_by(Axis.Z)[-1], 6)
    # tab block behind the top, 45 deg underside
    prof = Polygon((-0.5, PLATE_H - BLOCK_H - BLOCK_D), (0, PLATE_H - BLOCK_H - BLOCK_D), (BLOCK_D, PLATE_H - BLOCK_H),
                   (BLOCK_D, PLATE_H), (-0.5, PLATE_H), align=None)
    block = extrude(Plane.YZ * prof, CW / 2, both=True)
    part = plate + block
    part = part + pocket(XP, P_IW, P_ID, WALL_H) + pocket(XG, G_IW, G_ID, GLASSES_H)
    # front window of the phone pocket + cable slot through floor and front
    yf = -PLATE_T - P_ID - WALL
    part = part - Pos(XP, yf + WALL / 2, FLOOR_T + 12) * Box(WINDOW_W, WALL + 2, WALL_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    part = part - Pos(XP, (yf - 1 - PLATE_T) / 2, -1) * Box(CABLE_SLOT_W, -yf + 1 - PLATE_T, FLOOR_T + 14, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # tongue tab slot
    sw = TAB_T + SLOT_FIT
    part = part - Pos(0, BLOCK_D / 2, PLATE_H + 1) * Box(TAB_W + 2 * SLOT_FIT, sw, TAB_H + 2, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return part


def tongue() -> Part:
    t = rounded_box(TONGUE_W, TONGUE_L, TONGUE_T, radius=10)
    tab = Pos(0, -TONGUE_L / 2 + 4 + TAB_T / 2, TONGUE_T - 0.5) * Box(TAB_W, TAB_T, TAB_H + 0.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    tab = chamfer(tab.edges().group_by(Axis.Z)[-1], 0.8)
    return t + tab


def build():
    return [caddy(), Pos(0, BLOCK_D + LAYOUT_GAP + TONGUE_L / 2, 0) * tongue()]
