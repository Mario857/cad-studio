"""sunglasses-strap-clip: side-on spring clip for a pack shoulder strap with a snap-in sunglasses slot.

Spec: a U-shaped spring clip pushed sideways over the edge of the webbing (25-50 mm wide, 1.5-3 mm
thick) - it grips 22 mm of the strap, so any webbing width works. A bump near the tongue tip locks it
behind the webbing; a flared tip leads it on. On the front face two flex fingers form a vertical
channel (open at top, bottom and front): press the folded temple arms in through the 3 mm throat (or
drop them in from the top) and the fingers snap around them, so the glasses don't bounce.
In-use: strap runs along Z, webbing thickness along Y (body at -Y), U-bend at the strap edge (x=0).

Printed standing (profile in XY, extruded along Z): both the spring tongue and the slot fingers flex
along the layers. Tongue strain at 3 mm webbing ~1.1 %, finger strain at a 6 mm arm stack ~1.8 %.
Hardware: none.
Assumptions: temple arms 2-4 mm thick each (folded stack <= 6.5 mm); webbing 1.5-3 mm thick.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[dict(at=(10.0, 12.0, 30.0), grams=40)],
    print_orientation=(0, 0, 0),  # standing: flex in the layer plane
    supports="off",
    brim="auto",
)

HEIGHT = 30.0            # along the strap
# strap clip
WEB_GAP = 2.0            # free gap for 1.5-3 mm webbing (tongue flexes open)
BUMP_H = 0.8             # retaining bump into the gap -> 1.2 mm at the bump
CLIP_REACH = 22.0        # how far the clip reaches over the strap
PLATE_T = 2.5            # front plate (carries the slot)
TONGUE_T = 2.0           # spring tongue (behind the strap)
BEND_T = 2.5
FLARE = 1.5              # lead-in flare at the tongue tip
# sunglasses slot
SLOT_X = 11.0            # channel centre from the strap edge
CHANNEL_W = 6.5          # inner width (folded arm stack)
THROAT = 3.0             # opening between the snap teeth
FINGER_T = 1.6
FINGER_LEN = 14.0        # finger length out of the front plate


def _profile():
    # front plate y 0..PLATE_T, gap -WEB_GAP..0, tongue below
    y_t = -WEB_GAP
    front = Pos(CLIP_REACH / 2 - BEND_T / 2, PLATE_T / 2) * Rectangle(CLIP_REACH + BEND_T, PLATE_T)
    bend = Pos(-BEND_T / 2, (PLATE_T + y_t - TONGUE_T) / 2) * Rectangle(BEND_T, PLATE_T - y_t + TONGUE_T)
    tongue = Polygon(
        (-BEND_T, y_t - TONGUE_T), (CLIP_REACH - 3, y_t - TONGUE_T),
        (CLIP_REACH, y_t - TONGUE_T - FLARE), (CLIP_REACH, y_t - FLARE),
        (CLIP_REACH - 3, y_t), (CLIP_REACH - 5, y_t),
        (CLIP_REACH - 6, y_t + BUMP_H), (CLIP_REACH - 7, y_t + BUMP_H), (CLIP_REACH - 8, y_t),
        (-BEND_T, y_t), align=None,
    )
    sk = front + bend + tongue
    # fingers with snap teeth at the tip
    tooth = (CHANNEL_W - THROAT) / 2
    for side in (-1, 1):
        xin = SLOT_X + side * CHANNEL_W / 2            # inner face
        xout = xin + side * FINGER_T
        y0, y1 = PLATE_T - 0.01, PLATE_T + FINGER_LEN
        pts = [(xout, y0), (xout, y1), (xin - side * tooth, y1),
               (xin - side * tooth, y1 - 1.0), (xin, y1 - 1.0 - tooth * 1.5), (xin, y0)]
        finger = Polygon(*(pts if side > 0 else pts[::-1]), align=None)
        sk += finger
    return sk


def build() -> Part:
    part = extrude(_profile(), HEIGHT)
    part = fillet(part.edges().group_by(Axis.Z)[-1], 0.6)
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    return part
