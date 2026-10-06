"""file-folder-sorter: vertical desk sorter for 5 A4 file folders, stepped heights.

Spec: 5 front-to-back slots, each takes one A4 file folder (up to SLOT_W thick) standing upright on
its long edge. Divider heights step up toward the back so every folder spine/top is visible.
Stepped side walls tie the dividers together; dividers have 45-degree-roofed windows (print without
supports, save plastic). Base is the full footprint for stability with ~2.5 kg of folders.

Assumptions: A4 file folder / pocket file ~ 240 x 320 mm, <= 25 mm thick; ~500 g each.
MEASURE BEFORE PRINTING: folder width (front-back of the sorter) and thickness.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 0, 160), grams=2500)],   # 5 folders, COM ~half folder height
    print_orientation="auto",
    supports="auto",
    brim="on",             # ABS, 250 x 175 mm footprint
)

# Folders / fits
FOLDER_W = 240.0       # folder width standing in the slot (X)
FOLDER_CLEAR = 4.0     # per side
SLOT_W = 28.0          # slot thickness (folder <= 25 mm + 3 mm play)
N_SLOTS = 5

# Structure
DIV_T = 2.4
WALL = 3.0
BASE_T = 3.0
H0 = 50.0              # front divider height above base
STEP = 35.0            # height step per divider
WIN_BOTTOM = 20.0      # window bottom above base
WIN_TOP_MARGIN = 15.0  # material above the window apex
WIN_W_MAX = 200.0

IN_W = FOLDER_W + 2 * FOLDER_CLEAR
PITCH = SLOT_W + DIV_T


def build() -> Part:
    n_div = N_SLOTS + 1
    ys = [(i - N_SLOTS / 2) * PITCH for i in range(n_div)]
    hs = [H0 + i * STEP for i in range(n_div)]
    y_front, y_back = ys[0] - DIV_T / 2, ys[-1] + DIV_T / 2
    depth = y_back - y_front
    out_w = IN_W + 2 * WALL

    part = rounded_box(out_w, depth, BASE_T, radius=3)

    pts = [(y_front, 0), (y_front, BASE_T + hs[0])]
    for i in range(1, n_div):
        pts += [(ys[i] - DIV_T / 2, BASE_T + hs[i - 1]), (ys[i] - DIV_T / 2, BASE_T + hs[i])]
    pts += [(y_back, BASE_T + hs[-1]), (y_back, 0)]
    prof = Polygon(*pts, align=None)
    for sx in (-1, 1):
        x_out = sx * out_w / 2
        x_far = x_out if sx > 0 else x_out + WALL      # Plane.YZ extrudes toward -X
        part += Pos(x_far, 0, 0) * extrude(Plane.YZ * prof, WALL)

    for y, h in zip(ys, hs):
        div = Pos(0, y, BASE_T - 0.5) * Box(IN_W + 1, DIV_T, h + 0.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        apex = BASE_T + h - WIN_TOP_MARGIN
        z0 = BASE_T + WIN_BOTTOM
        w = min(WIN_W_MAX, 2 * (apex - z0 - 10))
        if w > 30:
            side_top = apex - w / 2
            win = Polygon((-w / 2, z0), (w / 2, z0), (w / 2, side_top), (0, apex), (-w / 2, side_top), align=None)
            win = Pos(0, y, 0) * extrude(Plane.XZ * win, 2 * DIV_T, both=True)
            div -= win
        part += div
    return part
