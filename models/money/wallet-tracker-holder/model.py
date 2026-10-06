"""wallet-tracker-holder: bank-card-sized carrier for an Apple AirTag that slides into a wallet card slot.

Spec: ID-1 card outline (85.6 x 54, R3.18 corners), PLATE_T thick, with a through bore for the AirTag
near one end (the AirTag bulges out on both sides of the plate). Retention: four fixed sectors carry a
bottom lip (stop), four flexible arc tabs (cantilevers cut free by arc slots + one radial slit each)
carry a V-shaped top lip that snaps over the AirTag rim. Push the AirTag in from the top: the tabs
flex outward, then spring back over its widest diameter. Push from below with a thumb to remove.
Prints flat, no supports (lip undersides are 45 deg).

MEASURE BEFORE PRINTING: AirTag dia 31.9 mm, thickness 8.0 mm; the widest diameter is assumed to lie
within the plate thickness when seated (adjust LIP_* if it sits loose); card slot accepts PLATE_T.
Assumptions: wallet slot takes ~2.4 mm; snap interference SNAP_INTERF per side.
Hardware: none.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="auto",
)

# Parameters
CARD_L, CARD_W, CARD_R = 85.6, 54.0, 3.18
PLATE_T = 2.4
TAG_D = 31.9
TAG_CLEAR = 0.4           # bore diametral clearance
BORE_X = -CARD_L / 2 + 6 + TAG_D / 2   # bore centre (towards one end)
BOTTOM_LIP_T = 0.6
BOTTOM_LIP_OVERLAP = 1.4  # radial overlap of the stop lip with the AirTag
SNAP_INTERF = 0.5         # radial overlap of the top V-lip with the AirTag
TAB_W = 1.8               # radial width of the flexible tabs
SLOT_W = 1.0              # arc slot width
N_TABS = 4
TAB_ANGLE = 62.0          # deg, each flexible tab
EDGE = 0.4

R_BORE = (TAG_D + TAG_CLEAR) / 2
R_SLOT_IN = R_BORE + TAB_W


def _wedge(a0: float, a1: float, r: float, h: float, z0: float = 0) -> Part:
    n = 24
    pts = [(0, 0)] + [(r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                       r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    return Pos(0, 0, z0) * extrude(Polygon(*pts, align=None), h)


def _ring(r_in: float, r_out: float, h: float, z0: float = 0) -> Part:
    return Pos(0, 0, z0) * (Cylinder(r_out, h, align=ON_BED) - Cylinder(r_in, h, align=ON_BED))


def build() -> Part:
    plate = extrude(RectangleRounded(CARD_L, CARD_W, CARD_R), PLATE_T)
    plate = chamfer(plate.edges().group_by(Axis.Z)[0] + plate.edges().group_by(Axis.Z)[-1], EDGE)
    hole = Cylinder(R_BORE, PLATE_T + 2, align=ON_BED)
    hub = Pos(0, 0, -1) * hole
    pitch = 360 / N_TABS
    cut = hub
    add = None
    for i in range(N_TABS):
        a0 = i * pitch
        a1 = a0 + TAB_ANGLE
        # arc slot behind the tab + radial slit at its free end
        cut += _ring(R_SLOT_IN, R_SLOT_IN + SLOT_W, PLATE_T + 2, -1) & _wedge(a0, a1, 40, PLATE_T + 2, -1)
        cut += Rot(0, 0, a1) * Pos((R_BORE + R_SLOT_IN + SLOT_W) / 2 - 0.2, 0, PLATE_T / 2) * Box(R_SLOT_IN + SLOT_W - R_BORE + 0.6, SLOT_W, PLATE_T + 2)
        # V snap lip on the tab: 45 deg underside and 45 deg lead-in
        r_tip = TAG_D / 2 - SNAP_INTERF
        dz = R_BORE - r_tip
        lip_prof = Polygon((R_BORE + 0.2, PLATE_T - 2 * dz), (r_tip, PLATE_T - dz), (R_BORE + 0.2, PLATE_T), align=None)
        lip = revolve(Plane.XZ * lip_prof, Axis.Z, 360) & _wedge(a0 + 2, a1 - 2, 40, PLATE_T + 1, -0.5)
        # bottom stop lip on the fixed sector that follows
        stop = _ring(TAG_D / 2 - BOTTOM_LIP_OVERLAP, R_BORE + 0.2, BOTTOM_LIP_T) & _wedge(a1 + 3, a0 + pitch - 3, 40, PLATE_T)
        add = lip + stop if add is None else add + lip + stop
    part = Pos(BORE_X, 0, 0) * add + (plate - Pos(BORE_X, 0, 0) * cut)
    return part
