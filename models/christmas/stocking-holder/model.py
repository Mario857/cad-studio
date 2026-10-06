"""stocking-holder: screw-tightened C-clamp mantel stocking hook with a star on top.

Spec: a C-clamp wraps the front edge of a mantel shelf (30-60 mm thick). An M6 bolt runs up
through the bottom jaw into a captive M6 nut (pocket opens into the clamp gap, so the clamping
reaction presses the nut onto plastic) and presses a pad against the shelf underside. A J-hook in
front of the spine carries a stocking (2 kg design load). A 5-point star stands on the top jaw,
flush with the front face.
Coordinates: viewer at -Y, shelf occupies y >= 0 (its front edge touches the spine at y = 0).
Print: lying on the side (use +X = print up), so the clamp/hook profile lies in the layer plane and
the hook load runs along layers; all profile faces are vertical walls -> no supports.
Assumptions:
- Shelf 30-60 mm thick (gap 62 mm); bolt travel covers 30..62 mm with an M6x50 bolt.
- Clamp is 40 mm wide; star is 44 mm across and tilted 18 deg (a jaunty star) because an upright
  5-point star printed on its side would have a ~72 deg overhang; tilted, with the notch between
  its two print-bottom tips cut deeper and the two beside the print-top tip shallower, it prints
  support-free (slightly irregular star).
- Bolt hole is a teardrop (horizontal in print), nut pocket hex has a 45 deg peak toward
  print-up (extra void above the nut).
- Add felt pads under the top jaw / on the bolt tip to protect the mantel finish.
"""

import math

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm.
# Parameters ----------------------------------------------------------------
W = 40.0             # clamp width along the mantel (X) = print height
SPINE_T = 10.0       # vertical spine thickness (in front of the shelf edge)
GAP = 62.0           # jaw opening: max shelf 60 mm + 2 mm
JAW_BOT_T = 14.0     # bottom jaw thickness (holds the nut pocket)
JAW_BOT_L = 50.0     # bottom jaw reach under the shelf (from shelf edge)
JAW_TOP_T = 9.0      # top jaw thickness
JAW_TOP_L = 40.0     # top jaw reach over the shelf
SCREW_Y = 30.0       # bolt axis distance behind the shelf front edge
CORNER_R = 2.0       # outer corner rounding of the profile

HOOK_REACH = 32.0    # hook arm length in front of the spine
HOOK_T = 10.0        # hook arm thickness
LIP_T = 8.0          # hook lip thickness
LIP_H = 28.0         # hook lip height (from z = 0)
HOOK_INNER_R = 5.0   # fillet in the U (stress relief, stocking loop seat)

# Hardware / fits
BOLT = "M6"
BOLT_FIT = "loose"                       # free-running bolt through the jaw
BOLT_D = 6.0 + 2 * FIT[BOLT_FIT]         # 6.8 mm clear hole
NUT_AF = 10.0                            # M6 nut across flats
NUT_FIT = 0.25                           # per side across flats (slide)
NUT_T = 5.2                              # M6 nut thickness
NUT_POCKET_DEPTH = NUT_T + 0.6           # nut sits just below the jaw top surface

# Star
STAR_R = 22.0        # outer radius (44 mm across)
STAR_RI = 0.42       # inner radius ratio
STAR_RI_LOW = 0.17   # deeper notch between the two print-bottom tips -> 45+ deg roof, no support
STAR_RI_SIDE = 0.56  # shallower notches beside the print-top tip -> <=45 deg overhang
STAR_T = 6.0         # star plate thickness (Y)
STAR_EMBED = 3.0     # lowest tip sunk into the top jaw
NECK_W = 12.0        # neck reaches NECK_W/2 past the star centre in X, down to the bed face

EF = 0.4             # elephant-foot chamfer on the print-bed face

Z_TOP = JAW_BOT_T + GAP + JAW_TOP_T

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,           # clamped to the shelf
    loads=[dict(at=(0, -SPINE_T - (HOOK_REACH - LIP_T) / 2, HOOK_T), grams=2000)],
    print_orientation=(0, -90, 0),   # use +X -> print +Z: hook/clamp bending runs along layers
    supports="off",
    brim="auto",
)


def _box(y0, y1, z0, z1):
    return Pos(0, (y0 + y1) / 2, (z0 + z1) / 2) * Box(W, y1 - y0, z1 - z0)


def _edges_x_at(part, pts, tol=0.05):
    out = []
    for e in part.edges().filter_by(Axis.X):
        c = e.center()
        for (y, z) in pts:
            if abs(c.Y - y) < tol and abs(c.Z - z) < tol:
                out.append(e)
    return out


def _star_pts(cx, cz):
    pts = []
    for k in range(10):
        a = math.radians(36 * k)   # tips at 0, 72, ... deg from +X -> one tip points print-up
        r = STAR_R if k % 2 == 0 else STAR_R * {5: STAR_RI_LOW, 3: STAR_RI_SIDE, 7: STAR_RI_SIDE}.get(k, STAR_RI)
        pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def build() -> Part:
    yf = -SPINE_T
    body = (
        _box(yf, JAW_BOT_L, 0, JAW_BOT_T)
        + _box(yf, 0, 0, Z_TOP)
        + _box(yf, JAW_TOP_L, JAW_BOT_T + GAP, Z_TOP)
        + _box(yf - HOOK_REACH, yf, 0, HOOK_T)
        + _box(yf - HOOK_REACH, yf - HOOK_REACH + LIP_T, 0, LIP_H)
    )
    # U-seat fillets of the hook
    body = fillet(_edges_x_at(body, [(yf, HOOK_T), (yf - HOOK_REACH + LIP_T, HOOK_T)]), HOOK_INNER_R)
    # outer convex corners
    outer = [
        (yf - HOOK_REACH, 0), (yf - HOOK_REACH, LIP_H), (yf - HOOK_REACH + LIP_T, LIP_H),
        (JAW_BOT_L, 0), (JAW_BOT_L, JAW_BOT_T),
        (yf, Z_TOP), (JAW_TOP_L, Z_TOP), (JAW_TOP_L, JAW_BOT_T + GAP),
    ]
    body = fillet(_edges_x_at(body, outer), CORNER_R)
    # elephant foot on the print-bed face (x = -W/2)
    bed_face = body.faces().sort_by(Axis.X)[0]
    body = chamfer(bed_face.edges(), EF)

    # star (XZ plane, front flush with spine front)
    cx = -W / 2 + STAR_R * math.sin(math.radians(54))   # lowest print points touch the bed
    cz = Z_TOP + STAR_R * math.sin(math.radians(72)) - STAR_EMBED
    star_plane = Plane(origin=(0, yf + STAR_T, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    star = extrude(star_plane * Polygon(*_star_pts(cx, cz), align=None), STAR_T)
    nx1 = cx + NECK_W / 2
    neck = Pos((nx1 - W / 2) / 2, yf + STAR_T / 2, (Z_TOP - 1 + cz) / 2) * Box(
        nx1 + W / 2, STAR_T, cz - Z_TOP + 1)
    part = body + star + neck

    # bolt teardrop hole (axis Z, point toward +X = print up)
    r = BOLT_D / 2
    tear = Circle(r) + Polygon((r / math.sqrt(2), r / math.sqrt(2)), (r * math.sqrt(2), 0),
                               (r / math.sqrt(2), -r / math.sqrt(2)), align=None)
    hole = Pos(0, SCREW_Y, -1) * extrude(tear, JAW_BOT_T + 2)
    # hex nut pocket from the gap side, vertex toward +X (print up) + 45 deg roof peak
    hex_r = (NUT_AF / 2 + NUT_FIT) / math.cos(math.radians(30))
    hy = hex_r * math.sqrt(3) / 2
    hex_sk = Polygon((hex_r / 2 + hy, 0), (hex_r / 2, hy), (-hex_r / 2, hy), (-hex_r, 0),
                     (-hex_r / 2, -hy), (hex_r / 2, -hy), align=None)
    pocket = Pos(0, SCREW_Y, JAW_BOT_T - NUT_POCKET_DEPTH) * extrude(
        hex_sk, NUT_POCKET_DEPTH + 1)
    return part - hole - pocket
