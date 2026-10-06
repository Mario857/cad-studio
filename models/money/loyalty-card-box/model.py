"""loyalty-card-box: box for 60 loyalty/bank cards with 5 labelled index dividers and a slip-over lid.

Spec: cards stand on their long edge (85.6 mm along X). Box walls 3.4 mm; the top LIP_H of the wall is
stepped in so the lid (same outer size) slides over it and sits flush on the step. Cards and divider
tabs stand above the box rim for easy grabbing; the lid is tall enough to clear the tabs.
Dividers: card-sized plates with a staggered tab carrying raised text (DIVIDER_LABELS, 0.6 mm).
"CARDS" engraved on the box front. All parts laid out on one plate in print pose
(box upright, lid top-down, dividers flat with text up).

MEASURE BEFORE PRINTING: card 85.6 x 54 x 0.76 mm (60 cards = 45.6 mm stack); thick embossed or
key-fob cards take more room - reduce CARDS_N.
Assumptions: labels are short (<= 5 chars at LABEL_SIZE); lid fit LID_CLEAR per side.
Hardware: none.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 0, 30), grams=330)],   # 60 cards ~5.5 g each
    print_orientation=(0, 0, 0),              # parts already in print pose
    supports="off",
    brim="on",                                # large flat ABS footprints
)

# Parameters
CARD_L, CARD_H, CARD_T = 85.6, 54.0, 0.76
CARDS_N = 60
DIVIDERS_N = 5
DIVIDER_LABELS = ("FOOD", "FUEL", "SHOP", "BANK", "MISC")
DIV_T = 1.6
DIV_CLEAR_X = 1.0          # divider narrower than the interior, total
SLACK_Y = 6.0              # free play in the stack
CLEAR_X = 1.4              # card length clearance, total
WALL = 3.4
FLOOR = 2.0
BOX_H = 44.0               # cards stick out ~12 mm above the rim
LIP_H = 14.0               # stepped-in lip the lid slides over
LID_WALL = 1.6
LID_CLEAR = 0.2            # per side
LID_TOP = 2.0
TAB_W, TAB_H = 26.0, 10.0
LABEL_SIZE = 7.0           # font size -> caps ~5 mm
LABEL_DEPTH = 0.6
FRONT_TEXT = "CARDS"
R_OUT = 4.0
GAP = 8.0                  # spacing on the plate

IN_X = CARD_L + CLEAR_X
IN_Y = CARDS_N * CARD_T + DIVIDERS_N * DIV_T + SLACK_Y
OUT_X = IN_X + 2 * WALL
OUT_Y = IN_Y + 2 * WALL
LIP_OUT_X = OUT_X - 2 * (LID_WALL + LID_CLEAR)
LIP_OUT_Y = OUT_Y - 2 * (LID_WALL + LID_CLEAR)
DIV_X = IN_X - DIV_CLEAR_X
DIV_H = CARD_H - 2.0
TAB_TOP = FLOOR + DIV_H + TAB_H
LID_IN_H = TAB_TOP + 1.0 - (BOX_H - LIP_H)
LID_H = LID_IN_H + LID_TOP


def _rrect_prism(x, y, r, h, z0=0.0) -> Part:
    return Pos(0, 0, z0) * extrude(RectangleRounded(x, y, r), h)


def box() -> Part:
    b = rounded_box(OUT_X, OUT_Y, BOX_H, radius=R_OUT)
    b -= _rrect_prism(IN_X, IN_Y, 1.5, BOX_H, FLOOR)
    ring = _rrect_prism(OUT_X + 2, OUT_Y + 2, R_OUT, LIP_H + 1, BOX_H - LIP_H) - \
        _rrect_prism(LIP_OUT_X, LIP_OUT_Y, R_OUT - LID_WALL - LID_CLEAR, LIP_H + 1, BOX_H - LIP_H)
    b -= ring
    # engraved front text (front = -Y face), below the lip
    t = label(FRONT_TEXT, size=10, depth=LABEL_DEPTH + 0.01)
    t = Pos(0, -OUT_Y / 2 + LABEL_DEPTH, (BOX_H - LIP_H) / 2) * Rot(90, 0, 0) * t
    b -= t
    return b


def lid() -> Part:
    """Lid in print pose: top on the bed, opening up."""
    l = rounded_box(OUT_X, OUT_Y, LID_H, radius=R_OUT)
    l -= _rrect_prism(LIP_OUT_X + 2 * LID_CLEAR, LIP_OUT_Y + 2 * LID_CLEAR, R_OUT - LID_WALL, LID_H, LID_TOP)
    return l


def divider(i: int) -> Part:
    """Divider in print pose: lying flat, its in-use height along +Y, text up."""
    d = extrude(RectangleRounded(DIV_X, DIV_H, 2.0), DIV_T)
    step = (DIV_X - TAB_W) / (DIVIDERS_N - 1)
    tx = -DIV_X / 2 + TAB_W / 2 + i * step
    tab = Pos(tx, DIV_H / 2 + TAB_H / 2 - 2, 0) * extrude(RectangleRounded(TAB_W, TAB_H + 4, 2.5), DIV_T)
    d = d + tab
    d = chamfer(d.edges().group_by(Axis.Z)[0], 0.3)
    d += Pos(tx, DIV_H / 2 + TAB_H / 2 - 0.5, DIV_T) * label(DIVIDER_LABELS[i], size=LABEL_SIZE, depth=LABEL_DEPTH)
    return d


def build():
    parts = [box(), Pos(OUT_X + GAP, 0, 0) * lid()]
    pitch_x, pitch_y = DIV_X + GAP, DIV_H + TAB_H + GAP
    cells = [(-1, 1), (0, 1), (1, 1), (-1, 2), (0, 2)]
    for i, (cx, cy) in enumerate(cells[:DIVIDERS_N]):
        parts.append(Pos(cx * pitch_x + OUT_X / 2, -OUT_Y / 2 - cy * pitch_y + 5, 0) * divider(i))
    return parts
