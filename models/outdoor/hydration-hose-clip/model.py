"""hydration-hose-clip: side-on shoulder-strap spring clip with two snap-in hose pockets. Set of 2.

Spec: a U-shaped spring clip pushed sideways over the edge of the webbing (25-50 mm wide, 1.5-3 mm
thick); it grips 26 mm of the strap so any webbing width works, a bump behind the strap locks it and
a flared tongue tip leads it on. On the front, two C-pockets (snap-in through a narrower mouth) hold the drinking hose parallel to the strap: "S" pocket for Ø8-10 mm hose, "L" pocket
for Ø10-12 mm hose (each grips from about mid-range up, the C flexes open for the top size). Clip it
at chin height so the bite valve stays near the mouth. Use two clips, one high, one lower on the strap.
In-use: strap and hose run along Z, webbing thickness along Y (body at -Y), U-bend at x = 0.

Printed standing (profile in XY, extruded along Z): the spring tongue and C-rings flex along layers.
Hardware: none.
Assumptions: hose is a PU/PVC hydration tube, Ø8-12 OD; webbing 1.5-3 mm thick.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # standing: flex in the layer plane
    supports="off",
    brim="auto",
    copies=2,
)

HEIGHT = 20.0            # along the strap / hose
# strap clip
WEB_GAP = 2.0            # free gap for 1.5-3 mm webbing (tongue flexes open)
BUMP_H = 0.8
CLIP_REACH = 29.5
PLATE_T = 2.5
TONGUE_T = 2.0
BEND_T = 2.5
FLARE = 1.5
# hose pockets: (centre x, inner diameter, mouth width)
RING_T = 2.0
POCKET_S = (6.5, 8.5, 6.0)      # Ø8-10 hose
POCKET_L = (21.0, 10.5, 7.6)    # Ø10-12 hose


def _clip():
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
    return front + bend + tongue


def _pocket(cx, d, mouth):
    ri, ro = d / 2, d / 2 + RING_T
    cy = PLATE_T + ri + 0.2          # ring overlaps the plate by RING_T - 0.2
    ring = Pos(cx, cy) * Circle(ro)
    # 45° tangent web to the plate (no acute ring/plate joint)
    a = ro * 0.7071
    xb = a - (cy - a - (PLATE_T - 0.2))
    ring += Polygon((cx - xb, PLATE_T - 0.2), (cx + xb, PLATE_T - 0.2), (cx + a, cy - a), (cx - a, cy - a), align=None)
    ring -= Pos(cx, cy) * Circle(ri)
    # radial mouth cut (lip end faces are full ring thickness, no knife edges)
    th = math.asin(mouth / 2 / ri)
    R = (ro + 2) / math.cos(th)
    cut = Polygon((cx, cy), (cx + R * math.sin(th), cy + R * math.cos(th)),
                  (cx - R * math.sin(th), cy + R * math.cos(th)), align=None)
    return ring - cut, cy


def build() -> Part:
    sk = _clip()
    for cx, d, m in (POCKET_S, POCKET_L):
        ring, _ = _pocket(cx, d, m)
        sk += ring
    part = extrude(sk, HEIGHT)
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    return part
