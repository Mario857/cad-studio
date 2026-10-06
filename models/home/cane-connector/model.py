"""cane-connector: bamboo cane connectors - 3-way teepee top, 4-way grid cross, 90° corner.

Spec: every socket is a slip-fit bore with two opposed spring tabs whose inner grip ribs press
on the cane, so one socket grips a 2 mm range of cane diameters. Two size ranges cover the
8-12 mm canes: 8-10 mm (bore 10.5) and 10-12 mm (bore 12.5); each set = teepee + cross +
corner in both ranges (6 parts), printed together. Cross/corner arms carry a raised size label.
- Teepee: 3 sockets splayed 20° from vertical at 120°, for a bean/sweet-pea teepee.
- Grid cross: 4 sockets in a plane at 90° (trellis/grid crossings).
- Corner: 2 sockets at 90° (frame corners).
Parts are laid out in their print poses (teepee hub-down; cross/corner flat on an octagon
face), so model coordinates are print poses. Arms are octagonal so every face is ≤ 45°;
horizontal bores are teardrops.
Material: AzureFilm ABS PLUS. ABS+ yellows/embrittles after a season or two in full sun; the
user's "AzureFilm ASA @BBL H2C 0.4 nozzle" preset is the long-life swap (same geometry).

Assumptions:
- Socket depth 35 mm; bore = range max + 2 x CANE_SLIP; grip ribs reach range min - GRIP.
- Spring tabs 20 mm long, full wall thickness (~1.2 % strain at full deflection).
- Teepee size is told apart by bore (no room for a ≥ 5 mm label on its tilted faces).
- Audit notes: 6 separate bodies per set is intended; the ~1.4 cm² "needs support" is spread
  over the teepee grip-rib/slit undersides (≤ 10 mm² each) which print fine as short overhangs.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),   # parts already in print poses
    supports="off",
    brim="auto",
    copies=2,
)

CANE_RANGES = ((8.0, 10.0), (10.0, 12.0))
CANE_SLIP = FIT["slide"]       # radial clearance on the largest cane of a range
GRIP = 0.4                     # rib interference on the smallest cane (radial)
SOCKET_DEPTH = 35.0
WALL = 2.6
TIP_WALL = 1.2
TAB_L = 20.0
TAB_W = 7.0
SLIT = 1.0
TEEPEE_SPLAY = 20.0            # socket angle from vertical
TEEPEE_ARM = 62.0              # hub centre to socket mouth
GRID_ARM = 46.0                # hub centre to socket mouth
LABEL_SIZE = 7.5
SET_GAP = 10.0

C8 = 1 / math.cos(math.radians(22.5))


def octagon(r: float) -> Sketch:
    pts = [(r * C8 * math.cos(math.radians(22.5 + 45 * k)), r * C8 * math.sin(math.radians(22.5 + 45 * k)))
           for k in range(8)]
    return Polygon(*pts, align=None)


def dims(rng):
    bore_r = rng[1] / 2 + CANE_SLIP
    rib_h = bore_r - (rng[0] / 2 - GRIP)
    out_r = max(bore_r + WALL, bore_r * math.sqrt(2) + TIP_WALL)   # teardrop tip keeps TIP_WALL
    return bore_r, out_r, rib_h


def half_width(r: float, z: float) -> float:
    """Half-width of a teardrop bore (tip +Z) at height z."""
    if z > r / math.sqrt(2):
        return max(r * math.sqrt(2) - z, 0.0)
    return math.sqrt(max(r * r - z * z, 0.0))


def socket(rng, length: float, round_bore: bool = False) -> Part:
    """Socket on the +X axis (axis through the origin), mouth at x = length."""
    bore_r, out_r, rib_h = dims(rng)
    part = extrude(Plane.YZ * octagon(out_r), length)
    x0 = length - SOCKET_DEPTH
    if round_bore:
        part -= Pos(x0, 0, 0) * Rot(0, 90, 0) * Cylinder(bore_r, SOCKET_DEPTH + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    else:
        part -= Pos(x0 + SOCKET_DEPTH / 2 + 0.5, 0, 0) * teardrop_hole(2 * bore_r, SOCKET_DEPTH + 1, along="X")
    x_root = length - 4.0
    x_free = x_root - TAB_L
    sh = SLIT * 1.4                       # vertical height of a 45° slit
    z0u, z0l = TAB_W / 2, -TAB_W / 2 - sh
    # slits run flat from the axis to just inside the bore wall, then rise 45° to the outside
    # (measured at the slit ceiling so no flat ceiling is left over material)
    yb_u = half_width(bore_r, z0u + sh) - 0.3
    yb_l = half_width(bore_r, z0l + sh) - 0.3
    yo = out_r + 1
    # tab cross-section bounds at the bore wall (y = bore_r)
    z_lo = z0l + sh + max(0.0, bore_r - yb_l)
    z_hi = min(z0u + max(0.0, bore_r - yb_u), bore_r / math.sqrt(2))
    for sy in (1, -1):
        # U-slit through the side wall -> spring tab rooted near the mouth. The two long slits
        # rise 45° outward so their ceilings print without support.
        cuts = []
        if round_bore:
            # near-vertical socket (teepee): plain long slits; the end slit is cut at 45° to the
            # axis so its ceiling is not a flat overhang
            run = yo - bore_r + 2
            for zc in (TAB_W / 2 + SLIT / 2, -TAB_W / 2 - SLIT / 2):
                cuts.append(Pos(x_free - run - 1, 0, zc) * Box(x_root - x_free + run + 1, yo, SLIT,
                                                              align=(Align.MIN, Align.MIN, Align.CENTER)))
            yc = (bore_r - 1 + yo) / 2
            cuts.append(Pos(x_free - (yc - bore_r), yc, 0) * Rot(0, 0, 45) *
                        Box(SLIT, (yo - bore_r + 2) * 1.42, TAB_W + 2 * SLIT))
        else:
            for z0, yb in ((z0u, yb_u), (z0l, yb_l)):
                par = Polygon((0, z0), (yb, z0), (yo, z0 + yo - yb), (yo, z0 + yo - yb + sh),
                              (yb, z0 + sh), (0, z0 + sh), align=None)
                cuts.append(Pos(x_free, 0, 0) * extrude(Plane.YZ * par, TAB_L))
            end = Polygon((0, z0l), (yb_l, z0l), (yo, z0l + yo - yb_l), (yo, z0u + yo - yb_u + sh),
                          (yb_u, z0u + sh), (0, z0u + sh), align=None)
            cuts.append(Pos(x_free - SLIT, 0, 0) * extrude(Plane.YZ * end, SLIT))
        for c in cuts:
            part -= c if sy > 0 else mirror(c, about=Plane.XZ)
        # grip rib at the free end: 45° lead-in from the mouth, 45° release, 45° underside
        tri = Polygon((x_free + 0.8, sy * (bore_r + 0.3)), (x_free + 0.8 + 2 * rib_h, sy * (bore_r + 0.3)),
                      (x_free + 0.8 + rib_h, sy * (bore_r - rib_h)), align=None)
        lo, hi = (-TAB_W / 2 + 0.6, TAB_W / 2 - 0.6) if round_bore else (z_lo + 0.8, z_hi - 0.4)
        zb = lo
        rib = Pos(0, 0, zb) * extrude(tri, hi - zb)
        rib -= Pos(0, sy * bore_r, zb) * Rot(-sy * 45, 0, 0) * Box(80, 20, 20, align=(Align.CENTER, Align.CENTER, Align.MAX))
        part += rib
    return part


def label_on_arm(text: str, out_r: float, x: float) -> Part:
    """Raised label on the top face of a +X arm whose axis is at z = out_r."""
    return Pos(x, 0, 2 * out_r - 0.05) * Rot(0, 0, 0) * label(text, size=LABEL_SIZE, depth=0.65)


def grid(rng, n_arms: int) -> Part:
    bore_r, out_r, _ = dims(rng)
    part = None
    for i in range(n_arms):
        arm = Rot(0, 0, 90 * i) * Pos(0, 0, out_r) * socket(rng, GRID_ARM)
        part = arm if part is None else part + arm
    # corner block fills the inside of the hub
    part += extrude(octagon(out_r), 2 * out_r)
    txt = f"{rng[0]:g}-{rng[1]:g}"
    part += Rot(0, 0, 90) * label_on_arm(txt, out_r, out_r + 9)
    return part


def teepee(rng) -> Part:
    bore_r, out_r, _ = dims(rng)
    part = Cylinder(out_r * 1.6, out_r * 1.4, align=ON_BED)
    for i in range(3):
        s = socket(rng, TEEPEE_ARM, round_bore=True)
        part += Rot(0, 0, 120 * i) * Pos(0, 0, out_r * 0.9) * Rot(0, -(90 - TEEPEE_SPLAY), 0) * s
    part &= Box(400, 400, 400, align=ON_BED)
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    return part


def build():
    parts = []
    x = 0.0
    for j, rng in enumerate(CANE_RANGES):
        _, out_r, _ = dims(rng)
        y = j * (2 * GRID_ARM + SET_GAP)
        parts.append(Pos(0, y, 0) * grid(rng, 4))
        parts.append(Pos(GRID_ARM * 2 + SET_GAP, y - GRID_ARM / 2, 0) * grid(rng, 2))
        parts.append(Pos(GRID_ARM * 3 + 2 * SET_GAP + 35, y, 0) * teepee(rng))
    return parts
