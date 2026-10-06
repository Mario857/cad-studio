"""led-star-window: 5-point window star outline with snap-in channel for a fairy-light string.

Spec:
- 5-point star outline, 250 mm max tip-to-tip (overall width), ~238 mm tall + hanging tab.
- A U-channel runs along the whole outline (centred on the band), open towards the room (+Z).
  The wire is pushed in past two 45-degree snap lips (opening narrower than the wire) and is then
  held in a round-ish cavity. Lip undersides are 45 degree chamfers -> prints without supports.
- Star tips of the channel centreline are rounded (TIP_R) so the wire can follow them.
- Tab above the top tip with a keyhole for a standard window suction cup: the cup head passes the
  big hole, the neck slides UP into the slot; the star's weight keeps the neck seated at the slot top.
- Modelled lying flat as it prints: back face (window side) on z=0, channel opening faces +Z.

Assumptions:
- Fairy-light wire Ø2-3 mm; designed for WIRE_D = 2.5 mm. Snap opening 1.9 mm (cavity 3.0 mm) (thinner 2 mm wire is
  still retained, a 3 mm wire needs a firm push). LED beads stay outside the opening (face the room).
- Suction cup: neck Ø6 mm, head Ø10 mm, neck length >= TAB_T (2.5 mm).
- Flat on a window, no load besides its own weight + ~20 g of lights -> not a standing part.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),   # flat, channel opening up
    supports="off",
    brim="auto",
)

# --- Overall star ----------------------------------------------------------
STAR_SPAN = 250.0          # max tip-to-tip (overall width incl. band)
INNER_RATIO = 0.382        # classic pentagram (36 deg tips; TIP_RETREAT assumes this)
TIP_R = 5.0                # rounding radius of the channel centreline at the tips/valleys

# --- Wire channel ------------------------------------------------------------
WIRE_D = 2.5               # nominal fairy-light wire diameter (2-3 mm range)
CH_FIT = "slide"           # clearance fit for the cavity
CH_W = clearance(WIRE_D, CH_FIT)   # cavity width
LIP = 0.55                 # lip overhang per side (45 deg chamfer) -> opening = CH_W - 2*LIP
CH_DEPTH = WIRE_D + 0.3    # cavity depth below the lips (floor to start of lip chamfer)
LIP_H = 1.0                # vertical height of the lip throat above the chamfer
WALL = 2.0                 # side wall thickness each side of the cavity
FLOOR = 1.6                # floor under the channel (window side)
EDGE_CHAMFER = 0.4         # elephant-foot chamfer on bed edges

BAND_W = CH_W + 2 * WALL
OPEN_W = CH_W - 2 * LIP
HEIGHT = FLOOR + CH_DEPTH + LIP + LIP_H

# --- Suction-cup tab ---------------------------------------------------------
TAB_D = 22.0               # tab disc diameter
TAB_T = 2.5                # tab thickness (fits between cup and head)
CUP_NECK_D = 6.0           # suction cup neck diameter
CUP_HEAD_D = 10.0          # suction cup head diameter
CUP_FIT = "loose"
KEY_HEAD = clearance(CUP_HEAD_D, CUP_FIT)   # big hole
KEY_NECK = clearance(CUP_NECK_D, CUP_FIT)   # slot width
KEY_TRAVEL = 6.0           # centre distance big hole -> neck seat (seat is above)

# centreline outer radius so that outer band tips (rounded) give STAR_SPAN width
TIP_RETREAT = TIP_R * (1 / math.sin(math.radians(18)) - 1)  # tip loss from rounding
R_OUT = STAR_SPAN / 2 / math.sin(math.radians(72)) - BAND_W / 2 + TIP_RETREAT
R_IN = R_OUT * INNER_RATIO


def star_pts(ro, ri):
    pts = []
    for i in range(10):
        a = math.radians(90 + 36 * i)
        r = ro if i % 2 == 0 else ri
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def band(sk, w):
    """Closed band of width w centred on the sketch outline."""
    return offset(sk, w / 2, kind=Kind.ARC) - offset(sk, -w / 2, kind=Kind.ARC)


def build() -> Part:
    raw = Polygon(*star_pts(R_OUT, R_IN), align=None)
    # round the tips (convex) then the valleys (concave) of the centreline
    cl = offset(offset(raw, -TIP_R, kind=Kind.ARC), TIP_R, kind=Kind.ARC)
    cl = offset(offset(cl, TIP_R, kind=Kind.ARC), -TIP_R, kind=Kind.ARC)

    body = extrude(band(cl, BAND_W), HEIGHT)

    # suction-cup tab above the top tip
    top_y = R_OUT - TIP_RETREAT + BAND_W / 2
    tab_cy = top_y + TAB_D / 2 - 6.0
    tab = Pos(0, tab_cy, 0) * Cylinder(TAB_D / 2, TAB_T, align=ON_BED)
    body = chamfer(body.edges().group_by(Axis.Z)[0], EDGE_CHAMFER)
    tab = chamfer(tab.edges().group_by(Axis.Z)[0], EDGE_CHAMFER)
    body = body + tab

    # wire cavity with 45 deg lip undersides
    cav = Pos(0, 0, FLOOR) * extrude(band(cl, CH_W), CH_DEPTH + LIP)
    cav = chamfer(cav.edges().group_by(Axis.Z)[-1], LIP)
    throat = Pos(0, 0, FLOOR + CH_DEPTH) * extrude(band(cl, OPEN_W), LIP + LIP_H + 1)
    body = body - cav - throat

    # keyhole (big hole below, neck seat above)
    key_y = tab_cy - KEY_TRAVEL / 2 + 1.5
    key = (Pos(0, key_y, -1) * Cylinder(KEY_HEAD / 2, TAB_T + 2, align=ON_BED)
           + Pos(0, key_y + KEY_TRAVEL / 2, -1)
           * extrude(SlotCenterToCenter(KEY_TRAVEL, KEY_NECK, rotation=90), TAB_T + 2))
    body = body - key
    return body
