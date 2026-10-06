"""pill-organizer-7day: slim 7-day travel pill organizer with individual dovetail slide lids.

Spec: one tray with 7 compartments in a row (M T W T F S S), each closed by its own lid that
slides in a 45 deg dovetail channel from the front face. A small conical bump on the tray's front ledge
clicks into a dimple under each lid so lids stay shut in a pack. Raised day letter (>= 5 mm cap
height) and a finger ridge on each lid. Filleted compartment floors for scooping pills out.
For DRY TABLETS / CAPSULES ONLY - not watertight, not for liquids or soft gels in heat.
Tray + 7 lids are returned as a list and print together (lids laid out beside the tray), so the
mesh check's "8 separate bodies" warning is intended.

Assumptions:
- Compartment ~17 x 23.5 x 13.8 mm is enough for a day's dose of normal tablets.
- Lids are fully removable (slide out the front); detent holds them closed.
- Fit clearances tuned for ABS on a 0.4 nozzle (LID_SIDE_CLEAR / LID_END_CLEAR / LID_Z_CLEAR);
  increase LID_SIDE_CLEAR by 0.05 if lids are tight.
- Letters use the default cadlib font at size 8 (cap height >= 5 mm), 0.8 mm tall.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # tray open-side up, lids flat with letters up
    supports="off",
    brim="auto",
)

# Parameters
N = 7
DAYS = ["M", "T", "W", "T", "F", "S", "S"]
PITCH = 20.0            # compartment spacing along X
CH_BOT_W = 18.0         # dovetail channel width at its bottom (wide side)
CH_DEPTH = 2.6          # dovetail depth = lid seat depth; 45 deg flanks
CH_VERT = 0.6           # vertical land at the dovetail bottom (no knife edges on lids)
CAV_W = 17.0            # compartment cavity width (leaves 0.5 mm ledge each side)
END_WALL = 2.0          # outer X walls at the channel bottom
FRONT_WALL = 3.0        # front wall under lid (carries the detent dome)
BACK_WALL = 2.0         # back wall, also the lid end stop
HEIGHT = 18.0
FLOOR = 1.6
CAV_FILLET = 4.0        # scoop radius at compartment floor
CORNER_R = 3.0

# Fits (ABS)
LID_SIDE_CLEAR = 0.30   # horizontal gap per side on dovetail flanks
LID_END_CLEAR = 0.30    # gap between lid and back stop
LID_Z_CLEAR = 0.20      # lid thinner than channel depth
DETENT_H = 0.30         # dome height on tray ledge (interference)
DETENT_R = 1.0          # dome footprint radius
DIMPLE_DEPTH = 0.50     # dimple under lid

# Lid features
LETTER_SIZE = 8.0
LETTER_DEPTH = 0.8
RIDGE_W = 1.2
RIDGE_H = 0.8

LENGTH = (N - 1) * PITCH + CH_BOT_W + 2 * END_WALL
DEPTH = FRONT_WALL + 23.5 + BACK_WALL
CH_TOP_W = CH_BOT_W - 2 * (CH_DEPTH - CH_VERT)


def _trap(bot_w, top_w, h, v=CH_VERT):
    return Polygon((-bot_w / 2, 0), (bot_w / 2, 0), (bot_w / 2, v), (top_w / 2, h),
                   (-top_w / 2, h), (-bot_w / 2, v), align=None)


def _prism_y(sketch, y0, y1):
    """Extrude an XZ-plane sketch between y0 and y1."""
    s = extrude(Plane.XZ * sketch, (y1 - y0) / 2, both=True)
    return Pos(0, (y0 + y1) / 2, 0) * s


def _lid(day):
    t = CH_DEPTH - LID_Z_CLEAR
    bw = CH_BOT_W - 2 * LID_SIDE_CLEAR
    tw = bw - 2 * (t - CH_VERT)
    y0, y1 = -DEPTH / 2, DEPTH / 2 - BACK_WALL - LID_END_CLEAR
    lid = _prism_y(_trap(bw, tw, t), y0, y1)
    # finger ridge at the front edge
    lid += Pos(0, y0 + 1.0 + RIDGE_W / 2, t) * Box(tw - 2, RIDGE_W, RIDGE_H,
                                                   align=(Align.CENTER, Align.CENTER, Align.MIN))
    # raised letter
    lid += Pos(0, (y0 + y1) / 2 + 2.5, t) * label(day, size=LETTER_SIZE, depth=LETTER_DEPTH)
    # detent dimple underneath
    yd = -DEPTH / 2 + FRONT_WALL / 2
    lid -= Pos(0, yd, -0.01) * Cone(DETENT_R + 0.25, 0.5, DIMPLE_DEPTH + 0.01,
                                    align=(Align.CENTER, Align.CENTER, Align.MIN))
    return lid


def build():
    tray = rounded_box(LENGTH, DEPTH, HEIGHT, radius=CORNER_R)
    z_seat = HEIGHT - CH_DEPTH
    ch_y0, ch_y1 = -DEPTH / 2 - 1, DEPTH / 2 - BACK_WALL
    cav_y0, cav_y1 = -DEPTH / 2 + FRONT_WALL, DEPTH / 2 - BACK_WALL
    cav_h = z_seat - FLOOR
    cav = Pos(0, (cav_y0 + cav_y1) / 2, FLOOR) * Box(CAV_W, cav_y1 - cav_y0, cav_h + 0.01,
                                                     align=(Align.CENTER, Align.CENTER, Align.MIN))
    cav = fillet(cav.edges().group_by(Axis.Z)[0], CAV_FILLET)
    channel = Pos(0, 0, z_seat) * _prism_y(
        _trap(CH_BOT_W, CH_TOP_W - 0.02, CH_DEPTH + 0.01), ch_y0, ch_y1)
    # dovetail flanks extended above top so the cut is clean
    channel += Pos(0, (ch_y0 + ch_y1) / 2, HEIGHT) * Box(
        CH_TOP_W, ch_y1 - ch_y0, 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cutter = cav + channel
    xs = [(i - (N - 1) / 2) * PITCH for i in range(N)]
    for x in xs:
        tray -= Pos(x, 0, 0) * cutter
    # detent domes on the front ledges
    yd = -DEPTH / 2 + FRONT_WALL / 2
    dome = Cone(DETENT_R, DETENT_R - 0.6, DETENT_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    dome = Pos(0, 0, -0.01) * dome
    for x in xs:
        tray += Pos(x, yd, z_seat) * dome

    # lids laid out in front of the tray for printing
    lids = []
    for x, d in zip(xs, DAYS):
        lids.append(Pos(x, -(DEPTH + 6), 0) * _lid(d))
    return [tray] + lids
