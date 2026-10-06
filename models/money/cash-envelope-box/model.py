"""cash-envelope-box: cash-envelope budgeting box for 10 envelopes, with lid and 10 clip-on index tabs.

Spec: open-top box holds 10 cash envelopes standing on their long edge (default banknote envelope
165 x 90 mm; set ENV_L/ENV_H = 220/110 for DL). Envelopes stick ENV_H - BOX_IN_H above the rim so
they are easy to pull. Each envelope gets a clip-on index tab (U-clip over the envelope's top edge)
with an engraved category name; tab positions can be staggered along the envelope by the user.
The lid slips over a stepped lip and rests on the shoulder; it is tall enough to cover the
envelopes and tabs. Front face carries an engraved "CASH" label.
Parts: box (in-use orientation), lid (output upside-down = print orientation), 10 tabs
(output on their side = print orientation, so the narrow clip gap needs no support).

Assumptions: each envelope with cash is <= ENV_T thick; envelope top edge paper <= CLIP_GAP.
MEASURE BEFORE PRINTING: envelope length/height (banknote envelopes are sized around the
EUR 200 note 153 x 77 mm; DL is 220 x 110), stuffed envelope thickness, flap paper thickness.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(0, 0, 40), grams=150)],
    print_orientation="auto",
    supports="off",            # only 0.6 mm-deep engraved-text ceilings need it; they bridge fine
    brim="on",                 # ABS + 177 x 66 mm flat box/lid footprints
)

# Envelope (banknote envelope default; DL = 220 x 110)
ENV_L = 165.0
ENV_H = 90.0
ENV_T = 5.0           # stuffed envelope thickness
N_ENV = 10
CATEGORIES = ["RENT", "FOOD", "FUEL", "BILLS", "FUN", "SAVE", "GIFTS", "HEALTH", "KIDS", "MISC"]

# Fits
ENV_CLEAR = 2.0       # per side, length direction
STACK_CLEAR = 3.0     # total extra in stack direction
LID_CLEAR = 0.3       # per side, lid over lip
CLIP_GAP = 0.6        # envelope edge paper (flap) thickness + grip

# Box
WALL = 3.2
LIP_WALL = 1.6
FLOOR = 2.4
BOX_IN_H = 68.0       # inner depth; envelope protrudes ENV_H - BOX_IN_H
LIP_H = 12.0
CORNER_R = 4.0

# Lid
LID_WALL = 2.0
LID_TOP = 2.4
LID_HEADROOM = 4.0    # above tab tops

# Clip tabs
TAB_W = 40.0
TAB_T = 2.0
TAB_LEG = 10.0
TAB_H = 14.0          # tab above the bridge
TEXT_SIZE = 5.5
TEXT_DEPTH = 0.6

IN_L = ENV_L + 2 * ENV_CLEAR
IN_W = N_ENV * ENV_T + STACK_CLEAR
BOX_H = FLOOR + BOX_IN_H
SHOULDER_Z = BOX_H - LIP_H


def make_box() -> Part:
    out_l, out_w = IN_L + 2 * WALL, IN_W + 2 * WALL
    lip_l, lip_w = IN_L + 2 * LIP_WALL, IN_W + 2 * LIP_WALL
    body = rounded_box(out_l, out_w, SHOULDER_Z, radius=CORNER_R)
    lip = Pos(0, 0, SHOULDER_Z - 1) * Box(lip_l, lip_w, LIP_H + 1, align=ON_BED)
    lip = fillet(lip.edges().filter_by(Axis.Z), CORNER_R - (WALL - LIP_WALL))
    box = body + lip
    cavity = Pos(0, 0, FLOOR) * Box(IN_L, IN_W, BOX_IN_H + 1, align=ON_BED)
    cavity = fillet(cavity.edges().filter_by(Axis.Z), CORNER_R - WALL)
    box = box - cavity
    txt = label("CASH", size=10, depth=TEXT_DEPTH + 0.01)
    box -= Pos(0, -out_w / 2 + TEXT_DEPTH, SHOULDER_Z / 2) * Rot(90, 0, 0) * txt
    return box


def make_lid() -> Part:
    """Returned upside-down (top on the bed) = print orientation."""
    lip_l, lip_w = IN_L + 2 * LIP_WALL, IN_W + 2 * LIP_WALL
    in_l, in_w = lip_l + 2 * LID_CLEAR, lip_w + 2 * LID_CLEAR
    out_l, out_w = in_l + 2 * LID_WALL, in_w + 2 * LID_WALL
    tab_top = FLOOR + ENV_H + TAB_T + TAB_H
    in_h = tab_top + LID_HEADROOM - SHOULDER_Z
    lid = rounded_box(out_l, out_w, in_h + LID_TOP, radius=CORNER_R)
    cav = Pos(0, 0, LID_TOP) * Box(in_l, in_w, in_h + 1, align=ON_BED)
    cav = fillet(cav.edges().filter_by(Axis.Z), CORNER_R - LID_WALL)
    return lid - cav


def make_tab(text: str) -> Part:
    """In-use: clip open downward over the envelope top edge (envelope plane = XZ)."""
    y_leg = CLIP_GAP / 2 + TAB_T / 2
    legs = [Pos(0, s * y_leg, -TAB_LEG) * Box(TAB_W, TAB_T, TAB_LEG, align=ON_BED) for s in (-1, 1)]
    bridge = Box(TAB_W, CLIP_GAP + 2 * TAB_T, TAB_T, align=ON_BED)
    flag = Pos(0, -y_leg, TAB_T) * Box(TAB_W, TAB_T, TAB_H, align=ON_BED)
    tab = legs[0] + legs[1] + bridge + flag
    txt = label(text, size=TEXT_SIZE, depth=TEXT_DEPTH + 0.01)
    tab -= Pos(0, -y_leg - TAB_T / 2 + TEXT_DEPTH, TAB_T + TAB_H / 2) * Rot(90, 0, 0) * txt
    return tab


def build():
    box = make_box()
    out_w = IN_W + 2 * WALL
    lid_w = IN_W + 2 * (LIP_WALL + LID_CLEAR + LID_WALL)
    lid = Pos(0, out_w / 2 + lid_w / 2 + 8, 0) * make_lid()
    parts = [box, lid]
    y0 = -out_w / 2 - 10
    for i, name in enumerate(CATEGORIES[:N_ENV]):
        col, row = i % 4, i // 4
        x = (col - 1.5) * (TAB_LEG + TAB_T + TAB_H + 8)
        y = y0 - row * 14
        tab = Rot(0, 90, 0) * make_tab(name)  # printed on its side: clip gap stays vertical
        bb = tab.bounding_box()
        parts.append(Pos(x - bb.center().X, y - bb.center().Y, -bb.min.Z) * tab)
    return parts
