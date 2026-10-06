"""drown-tray-ramp: low soapy-water floor trap for stink bugs, with snap-on perforated cover.

Spec: tray 200x120x35 (2.4 mm walls, floor 2.4, ~15 mm soapy water). A 45 deg climb ramp on each long
side (35 mm run, thin plate + gussets, 0.8 mm grip ribs) leads to the rim; bugs cross the 4 mm slotted
cover and drop in. Cover (200x120) snaps in via an inner skirt with a small bead. Printed side by side
flat, no supports (ramps are 45 deg plates, ribs 45 deg flanks).
Assumptions: ramp plate 2.4 mm normal thickness, gussets every ~33 mm; cover printed plate-down
(modelled upside down beside the tray); slots 30x4 so pets can't reach the water.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="auto",
)

L = 200.0
W = 120.0
H = 35.0
WALL = 2.4
FLOOR = 2.4
RAMP_RUN = 35.0          # 45 deg: run = height
RAMP_T = 2.4
RIB_H = 0.8
RIB_W = 1.6
RIB_PITCH = 7.0
GUSSET_N = 7
SKIRT_H = 4.0
SKIRT_T = 1.6
SKIRT_CLR = 0.25
BEAD = 0.5
SLOT_L, SLOT_W = 30.0, 4.0
GAP = 6.0
S2 = math.sqrt(2)


def ext(sk, amount) -> Part:
    p = extrude(Plane.YZ * sk, amount)
    return Pos(-p.bounding_box().min.X, 0, 0) * p


def ramp_side() -> Part:
    """Ramp on +Y side, wall outer face at y=W/2."""
    y0 = W / 2
    vt = RAMP_T * S2
    plate_pts = [(y0 - 0.5, H), (y0 + RAMP_RUN, 0), (y0 + RAMP_RUN - vt, 0), (y0 - 0.5, H - vt - 0.5)]
    plate = Pos(-L / 2, 0, 0) * ext(Polygon(*plate_pts, align=None), L)
    ramp = plate
    for i in range(GUSSET_N):
        x = -L / 2 + (L - RAMP_T) * i / (GUSSET_N - 1) + RAMP_T / 2
        g = Polygon((y0 - 0.5, 0), (y0 + RAMP_RUN, 0), (y0 - 0.5, H), align=None)
        ramp += Pos(x - RAMP_T / 2, 0, 0) * ext(g, RAMP_T)
    # grip ribs on the sloped surface (surface line: from (y0,H) to (y0+RUN,0)), normal (1,1)/sqrt2
    n = (1 / S2, 1 / S2)
    t = (1 / S2, -1 / S2)
    s = 4.0
    while s < RAMP_RUN * S2 - 4:
        p0 = (y0 + t[0] * s, H + t[1] * s)
        p1 = (p0[0] + t[0] * RIB_W, p0[1] + t[1] * RIB_W)
        e = lambda p, k: (p[0] + n[0] * k, p[1] + n[1] * k)
        rib = Polygon(e(p0, -0.4), e(p1, -0.4), e(p1, RIB_H), e(p0, RIB_H), align=None)
        ramp += Pos(-L / 2, 0, 0) * ext(rib, L)
        s += RIB_PITCH
    return ramp


def tray() -> Part:
    body = rounded_box(L, W, H, radius=3)
    body -= Pos(0, 0, FLOOR) * Box(L - 2 * WALL, W - 2 * WALL, H, align=ON_BED)
    r = ramp_side()
    body += r + mirror(r, about=Plane.XZ)
    return body


def cover() -> Part:
    plate = Box(L, W, 2.4, align=ON_BED)
    plate = fillet(plate.edges().filter_by(Axis.Z), 3)
    ow, ol = W - 2 * WALL - 2 * SKIRT_CLR, L - 2 * WALL - 2 * SKIRT_CLR
    outer = Pos(0, 0, 2.4) * Box(ol, ow, SKIRT_H, align=ON_BED)
    inner = Pos(0, 0, 2.4) * Box(ol - 2 * SKIRT_T, ow - 2 * SKIRT_T, SKIRT_H, align=ON_BED)
    skirt = outer - inner
    # snap beads on the long outer faces, 45 deg flanks
    for sy in (1, -1):
        b = Polygon((0, 0), (BEAD, BEAD), (0, 2 * BEAD), align=None)
        bead = Pos(-ol / 2 + 20, 0, 0) * ext(b, ol - 40)
        bead = Pos(0, 0, 2.4 + SKIRT_H - 2 * BEAD - 0.4) * bead
        skirt += Pos(0, sy * (ow / 2), 0) * (bead if sy == 1 else mirror(bead, about=Plane.XZ))
    cov = plate + skirt
    cut = None
    for i in range(5):
        for j in range(10):
            x = (i - 2) * 36
            y = (j - 4.5) * 9
            c = Pos(x, y, -1) * Box(SLOT_L, SLOT_W, 6, align=ON_BED)
            cov -= c
    return cov


def build():
    t = tray()
    c = Pos(0, W / 2 + RAMP_RUN + GAP + W / 2, 0) * cover()
    return [t, c]
