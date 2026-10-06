"""egg-tray-6: stackable 2x3 fridge egg tray.

Spec: 6 conical egg seats on a 52 mm grid inside a walled tray. Walls rise above the
eggs so filled trays stack; the wall top carries a 4 mm locating lip with a 45 deg roof that drops into
a matching V-topped groove (no supports) in the bottom of the tray above. The underside under each seat is
hollowed with a 45 deg cone (self-supporting) to save material.
Assumptions: size M/L hen eggs, max 46 mm diameter x 62 mm tall, seated so their top
is ~58 mm above the bed -> wall top 66 mm (upper tray floor clears the eggs).
Lip/groove radial clearance 0.3 mm.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 0, 40), grams=6 * 60)],
    print_orientation="auto",
    supports="auto",
    brim="on",                 # ABS, 167 x 115 flat footprint
)

# Parameters
NX, NY = 3, 2
PITCH = 52.0
WALL = 3.6
MARGIN = 2.0
PLATE_H = 24.0           # solid seat block height
SEAT_TOP_R = 23.0
SEAT_BOT_R = 12.0
SEAT_DEPTH = 16.0
CAVITY_R = 14.0          # 45 deg underside cone
HEIGHT = 66.0            # wall top
CORNER_R = 6.0
LIP_T = 1.8
LIP_H = 4.0
CLR = 0.3

L = NX * PITCH + 2 * (WALL + MARGIN)
W = NY * PITCH + 2 * (WALL + MARGIN)


def ring(inset_out, inset_in, h):
    o = rounded_box(L - 2 * inset_out, W - 2 * inset_out, h, radius=CORNER_R - inset_out,
                    bottom_chamfer=0)
    i = rounded_box(L - 2 * inset_in, W - 2 * inset_in, h + 2, radius=CORNER_R - inset_in,
                    bottom_chamfer=0)
    return o - Pos(0, 0, -1) * i


def rr(inset, z):
    return Plane.XY.offset(z) * RectangleRounded(L - 2 * inset, W - 2 * inset, CORNER_R - inset)


def vroof(inset_out, inset_in, z):
    """45 deg roof (apex up) over a ring band starting at height z."""
    mid = (inset_out + inset_in) / 2
    h = (inset_in - inset_out) / 2
    a = loft([rr(inset_out, z), rr(mid, z + h)])
    b = loft([rr(inset_in, z), rr(mid, z + h)])
    return a - b


def build() -> Part:
    part = rounded_box(L, W, HEIGHT, radius=CORNER_R)
    part -= Pos(0, 0, PLATE_H) * rounded_box(L - 2 * WALL, W - 2 * WALL, HEIGHT,
                                            radius=CORNER_R - WALL, bottom_chamfer=0)
    part += Pos(0, 0, HEIGHT) * ring(WALL - LIP_T, WALL, LIP_H)
    part += vroof(WALL - LIP_T, WALL, HEIGHT + LIP_H)
    for ix in range(NX):
        for iy in range(NY):
            x = (ix - (NX - 1) / 2) * PITCH
            y = (iy - (NY - 1) / 2) * PITCH
            part -= Pos(x, y, PLATE_H - SEAT_DEPTH) * Cone(SEAT_BOT_R, SEAT_TOP_R + 0.5, SEAT_DEPTH + 0.01,
                                                         align=ON_BED)
            part -= Pos(x, y, -0.01) * Cone(CAVITY_R, 0, CAVITY_R, align=ON_BED)
    # stacking groove in the bottom, mates with the lip of the tray below
    part -= Pos(0, 0, -0.01) * ring(WALL - LIP_T - CLR, WALL + CLR, LIP_H + 0.4)
    part -= vroof(WALL - LIP_T - CLR, WALL + CLR, LIP_H + 0.39)
    return part
