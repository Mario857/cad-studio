"""photo-frame: desktop frame for a 10x15 cm photo, slide-in from the top, leaning back 15 deg.

Spec: the photo slides down into a slot open at the top, between a U-shaped front bezel
(left, right, bottom borders overlap the photo by LIP) and a solid back plate. A thumb notch
in the back plate top lets you push/pull the photo. Two triangular ribs behind carry the frame
at TILT = 15 deg from vertical. ORIENTATION = "portrait" | "landscape".

Printing: printed upright exactly as it stands (bottom edge + ribs on the bed). Because the
slot and the U-window are open at the top, every cavity is a vertical channel: no bridges,
no ceilings, no supports; the 15 deg lean is only a 15 deg overhang.

Assumptions:
- Photo 100 x 150 mm, up to ~0.5 mm thick (photo + optional backing card fits SLOT_T = 1.2).
- The top edge of the photo is left uncovered (open-top slot); bezel overlap 5 mm on 3 sides.
- No hardware needed.
"""

import math

from build123d import *

from cadlib import *

ORIENTATION = "portrait"   # "portrait" | "landscape"

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[],
    print_orientation=(0, 0, 0),   # upright as in use: slot/window open upward, zero supports
    supports="off",
    brim="on",                     # tall part, small contact patch, ABS
)

# Photo
PHOTO_SHORT = 100.0
PHOTO_LONG = 150.0
PHOTO_CLR = 0.5          # side clearance per edge for sliding
SLOT_T = 1.2             # slot gap (photo thickness + play)

# Frame
BORDER = 10.0            # side border outside the photo
BOTTOM_BORDER = 14.0     # solid bottom under the photo
LIP = 5.0                # bezel overlap onto the photo
FRONT_T = 2.0            # front bezel thickness
BACK_T = 3.0             # back plate thickness
CORNER_R = 4.0           # top outer corner radius
FOOT_EXT = 4.0           # extra body below z=0 that gets cut flat by the bed plane
NOTCH_R = 12.0           # thumb notch radius in the back plate top

# Stand
TILT = 15.0              # lean back from vertical, deg
RIB_T = 4.0              # rib thickness (X)
RIB_DEPTH = 65.0         # how far the ribs reach behind the front edge on the table
RIB_HEIGHT = 85.0        # height up the frame back where the ribs attach
RIB_X_FRAC = 0.30        # rib x position as fraction of outer width from center


def _photo_dims():
    if ORIENTATION == "landscape":
        return PHOTO_LONG, PHOTO_SHORT
    return PHOTO_SHORT, PHOTO_LONG


def build() -> Part:
    pw, ph = _photo_dims()
    w_out = pw + 2 * PHOTO_CLR + 2 * BORDER
    h_out = BOTTOM_BORDER + ph
    t = FRONT_T + SLOT_T + BACK_T

    # Frame in local coords: front face y=0, back face y=t, bottom z=0 (extended by FOOT_EXT)
    body = Pos(0, t / 2, -FOOT_EXT) * Box(w_out, t, h_out + FOOT_EXT,
                                         align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = fillet(body.edges().filter_by(Axis.Y).group_by(Axis.Z)[-1], CORNER_R)

    big = h_out + 10
    slot = Pos(0, FRONT_T + SLOT_T / 2, BOTTOM_BORDER) * Box(
        pw + 2 * PHOTO_CLR, SLOT_T, big, align=(Align.CENTER, Align.CENTER, Align.MIN))
    window = Pos(0, FRONT_T / 2 - 0.5, BOTTOM_BORDER + LIP) * Box(
        pw - 2 * LIP, FRONT_T + 1.0, big, align=(Align.CENTER, Align.CENTER, Align.MIN))
    notch = Pos(0, FRONT_T + SLOT_T + BACK_T / 2, h_out) * Rot(90, 0, 0) * Cylinder(
        NOTCH_R, BACK_T + 2)
    frame = body - slot - window - notch

    # Lean back: local +Z goes toward +Y
    frame = Rot(-TILT, 0, 0) * frame

    # Ribs: triangle in YZ from the frame back down to the table
    a = math.radians(TILT)
    y_back0 = t / math.cos(a)                     # back face y at z=0
    y_att = y_back0 + RIB_HEIGHT * math.tan(a)    # back face y at z=RIB_HEIGHT
    tri = Polygon((y_back0 - 2, -FOOT_EXT), (y_back0 - 2, 0), (y_att - 2, RIB_HEIGHT),
                  (RIB_DEPTH, 0), (RIB_DEPTH, -FOOT_EXT), align=None)
    rib = extrude(Plane.YZ * tri, RIB_T / 2, both=True)
    rx = w_out * RIB_X_FRAC
    part = frame + Pos(rx, 0, 0) * rib + Pos(-rx, 0, 0) * rib

    # Flat bottom on the bed, elephant-foot chamfer
    part = split(part, bisect_by=Plane.XY, keep=Keep.TOP)
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    return part
