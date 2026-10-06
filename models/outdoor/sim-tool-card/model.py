"""sim-tool-card: credit-card-sized travel SIM tool (wallet card).

Spec: ISO ID-1 card 85.6 x 54 mm, corner r 3.18, 2.24 mm thick (<= 2.5). Prints flat.
Features (top face, in-use = print orientation):
  * SIM-ejector pin pocket: 0.8 mm wire shank groove + flat loop-head recess, retained
    by two pinch points in the groove (press-in snap) and a finger scoop to pry it out.
  * Two SIM adapter frames printed in place in through-windows, held by thin breakaway
    tabs (like commercial adapter kits):
      - nano->micro: 15 x 12 outline with nano (12.3 x 8.8) hole
      - nano->standard: 25 x 15 outline with nano hole
    Frames are 0.80 mm thick (bed side of the card) = SIM thickness 0.67-0.76.
    Snap them out, deburr tab stubs with a nail file / knife.
  * 50 mm ruler along the bottom long edge: 1 mm ticks, 5 mm and 10 mm longer,
    0.6 mm deep, cm numbers 0..5 engraved (>= 5 mm tall).
Assumptions:
  * Ejector pin ~ Apple style: 0.8 mm wire, shank 14 mm, flat loop 10 x 6 mm outside,
    total ~ 24 mm. Pocket is 1.0 mm deep so the pin sits flush/below the surface.
  * Quality "fine" (0.12 mm layers, 0.2 mm first layer): T and FRAME_T are layer multiples (0.2 + n*0.12).
  * SIM corner key chamfers ~ nano 1.0, micro 2.0, standard 3.0 mm (45 deg).
  * Adapter outlines are nominal - ADAPTER_UNDER so they drop into the phone tray;
    nano holes are nominal + SIM_HOLE_CLR so the SIM drops in (adapters rely on tray).
  * Frames (0.80 mm) are intentionally thinner than the 1.2 mm wall rule - they must
    match SIM thickness. They are non-structural.
  * Ruler tick grooves are 0.35 mm wide (ridges 0.65 mm) - if the slicer closes them, the
    ticks still show as shallow lines; increase TICK_W to 0.4 at the cost of 0.6 ridges.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # flat, as modelled (frames + ruler on top/bed faces)
    supports="off",
    brim="off",
    notes="WARN walls accepted: adapter frames 0.8 mm thick on purpose (SIM thickness, ISO max 0.84); ruler ridges 0.65 mm.",
)

# --- Card ---------------------------------------------------------------------
CARD_L = 85.6
CARD_W = 54.0
CARD_R = 3.18
T = 2.24                 # card thickness (<= 2.5), layer multiple for 0.12 mm

# --- SIM dims (ISO) -------------------------------------------------------------
NANO = (12.3, 8.8, 1.0)  # l, w, key chamfer
MICRO = (15.0, 12.0, 2.0)
STD = (25.0, 15.0, 3.0)
FRAME_T = 0.80           # adapter thickness (ISO ID-000: 0.76 +-0.08 -> max 0.84)
ADAPTER_UNDER = 0.10     # outline undersize (total) so it fits the phone tray
SIM_HOLE_CLR = 0.15      # nano hole oversize (total)
WINDOW_GAP = 0.5         # gap between frame and card window
TAB_W = 0.8              # breakaway tab width
TAB_T = FRAME_T          # breakaway tab thickness (0.8 x 0.8 section, snaps by twisting)

STD_C = (-26.0, -3.0)    # window centres
MICRO_C = (-3.0, -3.0)

# --- Ejector pin ------------------------------------------------------------
PIN_D = 0.8
PIN_GROOVE_W = PIN_D + 0.25   # slide fit
PIN_PINCH_W = 0.65            # width at the two snap pinch points (interference)
PIN_SHANK_L = 15.0
PIN_LOOP_L = 11.0             # loop recess (pin loop 10 x 6 + clearance)
PIN_LOOP_W = 7.0
PIN_ISLAND_L = 6.4            # island filling the loop's inner hole (locates the loop)
PIN_ISLAND_W = 2.6
POCKET_D = 1.0
PIN_Y = 18.0
PIN_X0 = 8.0                  # loop end x
SCOOP_R = 3.5

# --- Ruler -------------------------------------------------------------------
RULER_LEN = 50
RULER_X0 = -25.0
TICK_W = 0.35           # groove; leaves 0.65 mm ridges (wall audit fails < 0.6)
TICK_D = 0.6
TICK_1, TICK_5, TICK_10 = 2.0, 3.0, 4.5
NUM_SIZE = 7.0           # label size -> ~5 mm digit height
NUM_Y = -27.0 + 5.5      # bottom of number row


def sim_shape(l, w, ch, h):
    """Chamfered-corner SIM outline (key corner at -x,+y), extruded z 0..h, centred."""
    pts = [(-l / 2, -w / 2), (l / 2, -w / 2), (l / 2, w / 2),
           (-l / 2 + ch, w / 2), (-l / 2, w / 2 - ch)]
    return extrude(Plane.XY * Polygon(*pts, align=None), h)


def adapter(outer, center):
    l, w, ch = outer
    nl, nw, nch = NANO
    frame = sim_shape(l - ADAPTER_UNDER, w - ADAPTER_UNDER, ch, FRAME_T)
    frame -= Pos(0, 0, -0.1) * sim_shape(nl + SIM_HOLE_CLR, nw + SIM_HOLE_CLR, nch,
                                          FRAME_T + 0.2)
    win = Pos(0, 0, -1) * sim_shape(l + 2 * WINDOW_GAP, w + 2 * WINDOW_GAP, ch, T + 2)
    tab_len = 2 * WINDOW_GAP + 1.0
    tabs = [Pos(sx * (l / 2 + WINDOW_GAP / 2 - ADAPTER_UNDER / 4), 0, 0)
            * Box(tab_len, TAB_W, TAB_T, align=ON_BED) for sx in (-1, 1)]
    tabs += [Pos(0, sy * (w / 2 + WINDOW_GAP / 2 - ADAPTER_UNDER / 4), 0)
             * Box(TAB_W, tab_len, TAB_T, align=ON_BED) for sy in (-1, 1)]
    loc = Pos(*center, 0)
    return loc * win, loc * frame, [loc * t for t in tabs]


def build() -> Part:
    card = rounded_box(CARD_L, CARD_W, T, radius=CARD_R)

    # adapter windows + frames
    wins, frames, tabs = [], [], []
    for outer, c in ((STD, STD_C), (MICRO, MICRO_C)):
        w, f, t = adapter(outer, c)
        wins.append(w)
        frames.append(f)
        tabs += t
    for w in wins:
        card -= w

    # ejector pin pocket (cut from top face down)
    top = T
    loop_cx = PIN_X0 + PIN_LOOP_L / 2
    loop = Pos(loop_cx, PIN_Y, top - POCKET_D) * extrude(
        RectangleRounded(PIN_LOOP_L, PIN_LOOP_W, PIN_LOOP_W / 2 - 0.01), POCKET_D + 1)
    island = Pos(loop_cx, PIN_Y, top - POCKET_D - 0.5) * extrude(
        RectangleRounded(PIN_ISLAND_L, PIN_ISLAND_W, PIN_ISLAND_W / 2 - 0.01), POCKET_D + 0.5)
    shank_x0 = PIN_X0 + PIN_LOOP_L - 1.0
    shank = Pos(shank_x0 + PIN_SHANK_L / 2, PIN_Y, top - POCKET_D) * Box(
        PIN_SHANK_L, PIN_GROOVE_W, POCKET_D + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    bump_r = 0.4
    bump_off = PIN_PINCH_W / 2 + bump_r
    bumps = [Pos(x, PIN_Y + s * bump_off, top - POCKET_D) * Cylinder(bump_r, POCKET_D, align=ON_BED)
             for x in (shank_x0 + 4.0, shank_x0 + PIN_SHANK_L - 3.0) for s in (-1, 1)]
    scoop = Pos(PIN_X0 - 0.5, PIN_Y, top - POCKET_D) * Cylinder(SCOOP_R, POCKET_D + 1, align=ON_BED)
    pocket = (loop - island) + shank + scoop
    for b in bumps:
        pocket -= b
    card -= pocket

    # ruler ticks along bottom edge (y = -CARD_W/2), cut from top
    ticks = []
    for i in range(RULER_LEN + 1):
        ln = TICK_10 if i % 10 == 0 else TICK_5 if i % 5 == 0 else TICK_1
        ticks.append(Pos(RULER_X0 + i, -CARD_W / 2 - 0.5 + (ln + 0.5) / 2, top - TICK_D)
                     * Box(TICK_W, ln + 0.5, TICK_D + 1, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    for t in ticks:
        card -= t
    for n in range(0, RULER_LEN // 10 + 1):
        txt = label(str(n), size=NUM_SIZE, depth=TICK_D + 1)
        bb = txt.bounding_box()
        cx = (bb.min.X + bb.max.X) / 2
        card -= Pos(RULER_X0 + 10 * n - cx, NUM_Y - bb.min.Y, top - TICK_D) * txt
    cm = label("cm", size=NUM_SIZE, depth=TICK_D + 1)
    bb = cm.bounding_box()
    card -= Pos(RULER_X0 + 55 - bb.min.X - 2, NUM_Y - bb.min.Y, top - TICK_D) * cm

    part = card
    for f in frames:
        part += f
    for t in tabs:
        part += t
    return part
