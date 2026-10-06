"""dog-training-whistle: audible single-tone (~5-6 kHz) pea-less training whistle with lanyard loop.

Spec: a stopped-pipe whistle (like the classic "210.5" style). Blow into the mouthpiece end
(bottom, z=0). A flat windway WW_W x WW_H runs up the side of the body and sends a jet across a
side window (WIN_L long) onto a bevelled labium edge. Above the window is a closed resonator
bore (Ø BORE_D) with a 45° cone end. Pitch ~ c / (4 * L_eff): L_eff = RES_L + cone/3 + end
correction ~ 15-16 mm -> ~5.5 kHz. To raise the pitch, shorten RES_L (about 1 mm -> +0.35 kHz).
Lanyard loop tab on top (teardrop hole, no support needed).

Printing: stands upright as modelled, mouthpiece on the bed. The windway is a vertical slot whose
walls form it as it prints, so nothing needs support inside. The bore ends in a 45° cone instead
of a flat ceiling, and the labium bevel overhangs only LABIUM_BEVEL deg from vertical. The bed
chamfer also flares the windway inlet so elephant's foot can't close it. Quality "fine"
(thin layers give a cleaner labium edge).

Safety / use notes: ABS is not food-safe. This whistle goes in a person's mouth, so rinse it
with water before and after use, and never use it to hold food/water. It is not a chew toy; keep
it away from the dog. The whistle is audible on purpose: ultrasonic "silent" whistles need
tolerances beyond what FDM can do.
Hardware: a lanyard (cord <= LOOP_D - 1 mm thick).

Assumptions: speed of sound 343 m/s; pitch is approximate (±10 %) and depends on print accuracy
of the windway/labium; WW_H = 1.0 mm is ~2.5 nozzle widths so it prints open.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,            # hangs on a lanyard / handheld
    loads=[],
    print_orientation=(0, 0, 0),  # upright: windway vertical, formed by walls, no inner supports
    supports="off",
    brim="auto",
)

# Parameters
BODY_D = 14.0            # outer diameter
BORE_D = 8.0             # resonator bore
WW_LEN = 14.0            # windway length = mouthpiece length
WW_W = 5.0               # windway width (X)
WW_H = 1.0               # windway height (Y), the jet thickness
WIN_L = 2.6              # window: windway exit -> labium edge
LABIUM_BEVEL = 25.0      # deg from vertical
RES_L = 11.5             # straight bore above labium edge (tuning parameter)
CAP_T = 2.5              # solid wall above the bore cone
TAB_W = 12.0             # lanyard tab
TAB_T = 5.0
TAB_H = 11.0
LOOP_D = 5.0             # lanyard hole
EDGE_R = 1.0

R_OUT = BODY_D / 2
BORE_R = BORE_D / 2
WIN_BOT = WW_LEN
WIN_TOP = WW_LEN + WIN_L
BORE_TOP = WIN_TOP + RES_L
BODY_H = BORE_TOP + BORE_R + CAP_T     # 45° cone height = BORE_R


def build() -> Part:
    body = Cylinder(R_OUT, BODY_H, align=ON_BED)
    try:
        body = fillet(body.edges().group_by(Axis.Z)[-1], 2.0)
    except Exception:
        pass
    tab = Pos(0, 0, BODY_H - 2) * Box(TAB_W, TAB_T, TAB_H + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    tab = fillet(tab.edges().filter_by(Axis.Y).group_by(Axis.Z)[-1], TAB_W / 2 - 0.5)
    part = body + tab
    try:
        part = fillet(part.edges().filter_by(Axis.Y, reverse=True).group_by(Axis.Z)[-1], EDGE_R)
    except Exception:
        pass
    part -= Pos(0, 0, BODY_H + TAB_H / 2) * teardrop_hole(LOOP_D, TAB_T + 2, along="Y")

    # resonator: straight bore + 45° cone end
    part -= Pos(0, 0, WIN_BOT) * Cylinder(BORE_R, BORE_TOP - WIN_BOT, align=ON_BED)
    part -= Pos(0, 0, BORE_TOP) * Cone(BORE_R, 0.01, BORE_R, align=ON_BED)

    # windway: centred on the bore wall (y = BORE_R) so the jet splits on the labium edge
    part -= Pos(0, BORE_R, -1) * Box(WW_W, WW_H, WW_LEN + 1.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # window
    part -= Pos(0, BORE_R - WW_H / 2, WIN_BOT) * Box(WW_W, R_OUT, WIN_L, align=(Align.CENTER, Align.MIN, Align.MIN))
    # labium bevel (outside face of the wall above the window)
    part -= Pos(0, BORE_R, WIN_TOP) * Rot(-LABIUM_BEVEL, 0, 0) * Box(
        WW_W, R_OUT - BORE_R + 1, 20, align=(Align.CENTER, Align.MIN, Align.MIN))

    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    return part
