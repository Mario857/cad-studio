"""knife-block: universal knife block for 8+ knives with a rod-free slotted grid.

Spec: open-top box, 132 x 100 mm footprint, 230 mm tall. Inside, parallel 1.6 mm slats form
7 mm slots across the whole width, so any knife (paring to 22 cm chef/bread) drops into any
slot - no nylon rods needed. Slats only fill the top 30 mm plus a 45 deg V below it (prints
without supports, saves plastic). Floor has drain/crumb holes; 6 mm vertical corner radius
and 0.4 mm bottom chamfer against ABS warping.
Assumptions: blades up to 225 mm long and 85 mm tall (wider slots hold blade on edge),
handles stay above the rim; knives weigh ~150 g each (8 x 150 g load near the top).
ABS is not food-safe for direct food contact - wash knives as usual; block only holds them.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 0, 230), grams=1200)],
    print_orientation="auto",
    supports="auto",
    brim="on",
)

# Parameters
LENGTH = 132.0         # X, across the slots
DEPTH = 100.0          # Y, along the slots (blade height direction)
HEIGHT = 230.0
WALL = 2.0
FLOOR = 3.0
CORNER_R = 6.0
SLOT_GAP = 7.0         # blade slot width
SLAT_T = 1.6
SLAT_DEPTH = 30.0      # full-depth part of each slat below the rim
SLAT_RECESS = 2.0      # slats sit this far below the rim
DRAIN_D = 6.0
DRAIN_PITCH = 18.0


def build() -> Part:
    outer = rounded_box(LENGTH, DEPTH, HEIGHT, radius=CORNER_R)
    inner_l, inner_w = LENGTH - 2 * WALL, DEPTH - 2 * WALL
    cavity = Pos(0, 0, FLOOR) * rounded_box(inner_l, inner_w, HEIGHT, radius=CORNER_R - WALL,
                                             bottom_chamfer=0)
    part = outer - cavity

    # slats spanning Y, V-shaped underside (45 deg) so they print unsupported
    top = HEIGHT - SLAT_RECESS
    hy = inner_w / 2 + 0.5  # overlap into walls
    prof = Polygon((-hy, top), (hy, top), (hy, top - SLAT_DEPTH), (0, top - SLAT_DEPTH - hy),
                   (-hy, top - SLAT_DEPTH), align=None)
    slat = extrude(Plane.YZ * prof, SLAT_T)
    pitch = SLOT_GAP + SLAT_T
    n = int((inner_l - SLOT_GAP) // pitch)
    x0 = -(n - 1) * pitch / 2
    for i in range(n):
        part += Pos(x0 + i * pitch - SLAT_T / 2, 0, 0) * slat

    # drain / crumb holes in the floor
    nx, ny = int((inner_l - 12) // DRAIN_PITCH) + 1, int((inner_w - 12) // DRAIN_PITCH) + 1
    holes = GridLocations(DRAIN_PITCH, DRAIN_PITCH, nx, ny) * Cylinder(DRAIN_D / 2, FLOOR * 3)
    part -= holes
    return part
