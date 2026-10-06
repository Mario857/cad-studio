"""spiral-tree: tabletop decorative Christmas tree, twisting stack of star tiers, star on top.

Spec: 180 mm tall. Five tiers, each a lofted 8-point star that flares out (underside
<= 45 deg) then tapers in, the whole stack twisting continuously upward. Hollow shell
(>= 1.6 mm walls, measured normal to the surface) with an open bottom so it can sit over
an LED tea light. Topped by a thick 5-point star standing upright, point down, with
pyramidal bevels on both faces so every face is <= 45 deg from vertical -> no supports.
Assumptions:
- Open bottom (decoration; lets a tea light glow through / saves filament).
- Base star outer radius 62 mm (~124 mm across) for stability; tip angle checked by audit.
- Twist 70 deg over the body height; each tier steps in 16 mm radius; flares and
  tapers both ~35 deg from vertical so neither outside nor cavity ceiling needs support.
- Top star 36 mm across, 10 mm thick, bevelled down to 30 % at the faces.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[],
    print_orientation="auto",
    supports="auto",
    brim="auto",
)

# Parameters
TOTAL_H = 180.0          # overall height incl. star
N_TIERS = 5
BASE_R = 62.0            # outer star radius of the bottom tier
TOP_TIER_R = 22.0        # max outer star radius of the top tier
TIER_STEP = 16.0         # radius each tier tapers in by before the next one flares out
                         # (flare/taper slopes are derived: ~35 deg from vertical)
INNER_CLOSE = 0.8        # cavity closes at this fraction of the last tier's taper height
INNER_CLOSE_R = 3.0      # star radius where the cavity closes
STAR_POINTS = 8          # points of the tier star
STAR_RATIO = 0.62        # inner/outer radius of the tier star
TWIST_DEG = 70.0         # total twist over BODY_H
TIP_R = 4.0              # outer radius at the very top of the body
WALL = 2.4               # horizontal wall offset (>= 1.6 mm normal to the ~35 deg flares)
FOOT_CHAMFER = 0.4       # elephant-foot chamfer at the bed

TOP_STAR_R = 18.0        # top star outer radius
TOP_STAR_RATIO = 0.45    # inner/outer radius of top star
TOP_STAR_T = 10.0        # top star thickness (Y)
TOP_STAR_BEVEL = 0.3     # face scale of the pyramidal bevel
TOP_STAR_SINK = 5.0      # how far the body tip reaches up into the star's bottom notch
BODY_H = TOTAL_H - TOP_STAR_R - TOP_STAR_R * TOP_STAR_RATIO + TOP_STAR_SINK  # body top


def star_pts(r_out, ratio, n, rot_deg, start_deg=90.0):
    pts = []
    for k in range(2 * n):
        a = math.radians(start_deg + rot_deg + k * 180.0 / n)
        r = r_out if k % 2 == 0 else r_out * ratio
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def inset(pts, t):
    """Offset a CCW polygon inward by t, keeping vertex count and order."""
    n = len(pts)
    lines = []
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L  # left normal = inward for CCW
        lines.append(((x1 + nx * t, y1 + ny * t), (dx, dy)))
    out = []
    for i in range(n):
        (p, d), (q, e) = lines[i - 1], lines[i]
        den = d[0] * e[1] - d[1] * e[0]
        s = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
        out.append((p[0] + d[0] * s, p[1] + d[1] * s))
    return out


def section(z, r, inner=False, r_override=None):
    rot = TWIST_DEG * z / BODY_H
    pts = star_pts(r, STAR_RATIO, STAR_POINTS, rot)
    if inner:
        pts = inset(pts, WALL)
    return Plane.XY.offset(z) * Polygon(*pts, align=None)


def profile():
    """(z, outer radius) stations of the tiered body."""
    tier_h = BODY_H / N_TIERS
    st = [(0.0, BASE_R - FOOT_CHAMFER), (FOOT_CHAMFER, BASE_R)]
    for i in range(N_TIERS):
        z0 = i * tier_h
        rmax = BASE_R + (TOP_TIER_R - BASE_R) * i / (N_TIERS - 1)
        rtop = TIP_R if i == N_TIERS - 1 else rmax - TIER_STEP
        if i > 0:
            rbot = st[-1][1]
            slope = tier_h / ((rmax - rbot) + (rmax - rtop))
            st.append((z0 + (rmax - rbot) * slope, rmax))
        st.append((z0 + tier_h, rtop))
    return st


def build() -> Part:
    st = profile()
    outer = loft([section(z, r) for z, r in st], ruled=True)

    # inner cavity: same stations inset by WALL, closing to a point below the top
    inner_st = [(z, r) for z, r in st[:-1]]
    inner_secs = [section(-1.0, st[0][1], inner=True)] + [
        section(z, r, inner=True) for z, r in inner_st
    ]
    z_last, r_last = st[-2]
    z_close = z_last + (BODY_H - z_last) * INNER_CLOSE
    inner_secs.append(section(z_close, INNER_CLOSE_R))
    inner = loft(inner_secs, ruled=True)
    body = outer - inner

    # top star: upright in XZ plane, point up, sitting on the body tip between its two lower points, pyramidal bevel faces
    cz = TOTAL_H - TOP_STAR_R
    def star_face(y, s):
        pts = star_pts(TOP_STAR_R * s, TOP_STAR_RATIO, 5, 0.0, start_deg=90.0)
        return Plane.XZ.offset(-y) * Pos(0, cz) * Polygon(*pts, align=None)

    star = loft(
        [star_face(-TOP_STAR_T / 2, TOP_STAR_BEVEL), star_face(0, 1.0),
         star_face(TOP_STAR_T / 2, TOP_STAR_BEVEL)],
        ruled=True,
    )
    return body + star
