"""sponge-holder: sink-side sponge tray with drain slots.

Spec: open-top tray for a standard kitchen sponge (~110 x 75 x 30 mm). The floor has
stadium drain slots; the underside has open-ended 45 deg V-grooves across the width so water
that passes the slots runs out sideways instead of pooling under the tray.
Assumptions: sponge 110 x 75 mm, 5 mm free play per side; sits on the counter/sink
ledge; ABS+ is fine with dish soap and warm water.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 0, 15), grams=60)],   # wet sponge
    print_orientation="auto",
    supports="auto",
    brim="on",                 # ABS, 125 x 90 flat footprint
)

# Parameters
SPONGE_L = 110.0
SPONGE_W = 75.0
PLAY = 5.0
WALL = 2.4
FLOOR = 4.0
HEIGHT = 25.0
CORNER_R = 8.0
SLOT_L = 90.0
SLOT_W = 5.0
SLOT_PITCH = 10.0
GROOVE_D = 2.5   # 45 deg V-groove, 5 mm wide, self-supporting
GROOVE_PITCH = 22.0

OUT_L = SPONGE_L + 2 * PLAY + 2 * WALL
OUT_W = SPONGE_W + 2 * PLAY + 2 * WALL


def build() -> Part:
    part = rounded_box(OUT_L, OUT_W, HEIGHT, radius=CORNER_R)
    inner = rounded_box(OUT_L - 2 * WALL, OUT_W - 2 * WALL, HEIGHT, radius=CORNER_R - WALL,
                        bottom_chamfer=0)
    part -= Pos(0, 0, FLOOR) * inner
    # drain slots through the floor (long axis X)
    n_slots = int((OUT_W - 2 * WALL - 2 * PLAY) // SLOT_PITCH)
    for i in range(n_slots):
        y = (i - (n_slots - 1) / 2) * SLOT_PITCH
        part -= Pos(0, y, FLOOR) * slot(SLOT_L, SLOT_W, FLOOR + 1)
    # underside grooves along Y, open at both long walls
    n_g = int((OUT_L - 30) // GROOVE_PITCH) + 1
    for i in range(n_g):
        x = (i - (n_g - 1) / 2) * GROOVE_PITCH
        tri = Polygon((x - GROOVE_D, -0.01), (x + GROOVE_D, -0.01), (x, GROOVE_D), align=None)
        part -= extrude(Plane.XZ * tri, OUT_W / 2 + 1, both=True)
    return part
