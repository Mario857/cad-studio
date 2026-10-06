"""twist-vase: modern fluted vase with a gentle spiral twist.

Spec: 220 mm tall decorative / flower vase. Soft 8-lobe fluted cross-section that twists 90 deg
from foot to lip, bulging body (Ø ~115 mm) tapering to a narrow neck with a slight lip flare.
Hollow with ~2 mm walls and a 3 mm solid floor, prints upright with no supports.

Assumptions:
- Size ~220 x 115 x 115 mm; wall 2.2 mm, floor 3.0 mm (change WALL / FLOOR / HEIGHT below).
- Matte PLA for the look. FDM walls are not guaranteed watertight: for fresh flowers use a glass
  liner, or switch to PETG and seal the inside.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="PLA-MATTE",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 0, 60), grams=400)],  # water + stems
    print_orientation=(0, 0, 0),  # upright: base on the bed, no supports
    supports="off",
    brim="auto",
)

# Parameters
HEIGHT = 220.0
WALL = 2.2
FLOOR = 3.0
LOBES = 8            # number of flutes
FLUTE = 0.06         # flute depth as a fraction of radius
TWIST = 90.0         # total twist foot -> lip, degrees
POINTS = 96          # points per cross-section spline

# Radius profile (z, mean radius): foot, belly, shoulder, neck, lip
PROFILE = [
    (0.0, 42.0),
    (35.0, 52.0),
    (75.0, 57.0),
    (120.0, 50.0),
    (165.0, 36.0),
    (200.0, 31.0),
    (220.0, 35.0),
]


def _radius(z: float) -> float:
    """Smooth (cosine-eased) interpolation of the radius profile."""
    for (z0, r0), (z1, r1) in zip(PROFILE, PROFILE[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            t = (1 - math.cos(math.pi * t)) / 2
            return r0 + (r1 - r0) * t
    return PROFILE[-1][1]


def _section(z: float, inset: float = 0.0) -> Face:
    r = _radius(z) - inset
    twist = math.radians(TWIST * z / HEIGHT)
    pts = []
    for i in range(POINTS):
        a = 2 * math.pi * i / POINTS
        rr = r * (1 + FLUTE * math.cos(LOBES * a))
        pts.append((rr * math.cos(a + twist), rr * math.sin(a + twist), z))
    return make_face(Spline(*pts, periodic=True))


def build() -> Part:
    zs = [i * HEIGHT / 11 for i in range(12)]
    outer = loft([_section(z) for z in zs])
    # Inner cavity: inset sections, open at the top. It ends exactly at HEIGHT (coplanar with the
    # outer top); overshooting makes the rim's B-spline intersection mesh with open edges.
    inner_zs = [FLOOR] + [z for z in zs if z > FLOOR + 5]
    inner = loft([_section(z, WALL) for z in inner_zs])
    vase = outer - inner
    try:
        vase = chamfer(vase.edges().group_by(Axis.Z)[0], 0.4)
    except Exception:
        pass  # elephant-foot chamfer is cosmetic; skip if the B-spline edge refuses
    return vase
