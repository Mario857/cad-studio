"""invoice-inbox-wall: wall mail sorter with 3 cascading pockets labelled IN / TO PAY / PAID.

Spec: back plate screwed to the wall through 2 keyhole slots; three pockets step down toward the
front (back pocket highest). Each pocket takes DL / C5 envelopes and A4 folded in thirds
(210 x 99 mm) standing on the long edge; pocket floors are 45-degree V-bottoms (support-free)
so letters slide to the front corner. Raised labels on each pocket front.
Printed standing as in use (all walls vertical, floors 45 deg, no supports).

Assumptions: largest item C5 229 x 162 or DL 220 x 110; stack <= POCKET_D - 5 mm per pocket.
Wall screws Ø3.5-4 mm, head <= 8.5 mm.
MEASURE BEFORE PRINTING: widest envelope you use (must be < IN_W), screw head diameter.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation="auto",
    supports="off",          # only raised-letter undersides (0.6 mm) flag; they print fine
    brim="on",               # ABS, tall 245 mm wide part
)

LABELS = ["IN", "TO PAY", "PAID"]   # back -> front

# Mail / fits
IN_W = 236.0             # inner pocket width (C5 229 mm + 3.5 mm per side)
POCKET_D = 25.0          # pocket depth (stack thickness)
POCKET_H = 70.0          # front wall top above the pocket's lowest floor point
STEP = 55.0              # front-wall top step between pockets
BACK_ABOVE = 55.0        # back plate above the back pocket front wall (keyholes)
T = 2.5                  # pocket walls / floors
BACK_T = 4.5
TEXT_SIZE = 9.0
TEXT_DEPTH = 0.6

# Keyholes (fits)
KH_HEAD_D = 9.0
KH_SLOT_W = 4.6
KH_SLOT_L = 10.0
KH_RECESS = 2.5
KH_X = 80.0

N = len(LABELS)
OUT_W = IN_W + 2 * T


def build() -> Part:
    # pocket k = 0 (back) .. N-1 (front); front-wall outer face y_f[k] (wall at y = 0, front = -Y)
    y_in = [-BACK_T - k * (POCKET_D + T) - POCKET_D for k in range(N)]  # inner face of front wall k
    s2 = T * 2 ** 0.5
    lift = T / 2 + s2                       # front pocket floor underside touches z = 0
    tops = [lift + POCKET_H + (N - 1 - k) * STEP for k in range(N)]
    lows = [t - POCKET_H for t in tops]
    back_top = tops[0] + BACK_ABOVE

    shapes = [Pos(-BACK_T / 2, back_top / 2) * Rectangle(BACK_T, back_top)]
    for k in range(N):
        yf, yb = y_in[k] - T, y_in[k] + POCKET_D        # front wall outer, back wall face
        wall_bot = lows[k + 1] + POCKET_D + T - s2 + 0.3 if k + 1 < N else 0.0  # buried in the 45 deg floor below
        shapes.append(Pos(yf + T / 2, (tops[k] + wall_bot) / 2) * Rectangle(T, tops[k] - wall_bot))
        # 45-degree floor: top surface from (yf + T, low) up to the back wall
        y0, z0 = yf + T / 2, lows[k] - T / 2
        L = yb + T - y0
        shapes.append(Polygon((y0, z0), (y0 + L, z0 + L), (y0 + L, z0 + L - s2), (y0, z0 - s2), align=None))
    body = extrude(Plane.YZ * shapes[0], OUT_W / 2, both=True)
    for s in shapes[1:]:
        body += extrude(Plane.YZ * s, OUT_W / 2, both=True)

    # stepped side walls
    pts = [(0, 0), (0, tops[0])]
    for k in range(N):
        yf = y_in[k] - T
        pts += [(yf, tops[k])]
        if k + 1 < N:
            pts += [(yf, tops[k + 1])]
    pts += [(y_in[-1] - T, 0)]
    side = Polygon(*pts, align=None)
    for sx in (-1, 1):
        body += Pos(sx * (OUT_W / 2 - T / 2), 0, 0) * extrude(Plane.YZ * side, T / 2, both=True)

    # labels on pocket fronts
    for k, text in enumerate(LABELS):
        yf = y_in[k] - T
        txt = label(text, size=TEXT_SIZE, depth=TEXT_DEPTH + 0.4)
        z = tops[k] - TEXT_SIZE - 6
        body += Pos(0, yf + 0.4, z) * Rot(90, 0, 0) * txt

    # keyholes: teardrop entry, shank slot with teardrop top, channel with 45 deg top on the wall side
    kz = back_top - 30
    top = kz + KH_SLOT_L
    for x in (-KH_X, KH_X):
        cut = Pos(x, 0, kz) * teardrop_hole(KH_HEAD_D, BACK_T * 3, along="Y")
        cut += Pos(x, 0, top) * teardrop_hole(KH_SLOT_W, BACK_T * 3, along="Y")
        cut += Pos(x, 0, (kz + top) / 2) * Box(KH_SLOT_W, BACK_T * 3, KH_SLOT_L)
        w = KH_HEAD_D + 0.4
        ch = Polygon((0.5, kz - w / 2), (0.5, top + w / 2 + KH_RECESS + 0.5),
                     (-KH_RECESS, top + w / 2), (-KH_RECESS, kz - w / 2), align=None)
        cut += Pos(x, 0, 0) * extrude(Plane.YZ * ch, w / 2, both=True)
        body -= cut
    return body
