"""bag-clip-rod: two-part slide-on food bag sealing clip, 110 mm long.

Spec: a C-channel (bore + side slot) and a round rod. Fold the bag edge, wrap it round the
rod, push the bag edge through the slot and slide the rod (with the bag wrapped round it) into the
bore from the end; the folded bag is pinched between rod and bore wall and the slot is narrower
than the rod, so the rod cannot pull out sideways. Rod head and channel end tab are finger pulls.
Channel body 100 mm + 10 mm rounded tab = 110 mm overall; rod 96 mm + head.
Both parts are modelled lying flat in print position, side by side on one plate (the "2 separate bodies" mesh WARN is intended: channel + rod are two parts).

Assumptions: folded bag = 2 layers x 0.3 mm = 0.6 mm wrapped round the rod; bore gap per side =
fold + FIT snug (0.15) / 2 so it grips firmly but still slides; the bore ceiling is a 45 deg
teardrop (no supports); rod has small flats top/bottom so it prints flat on the bed; PETG for
toughness (PLA also works).
"""

from build123d import *

from cadlib import *

META = dict(
    material="PETG",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # modelled in print position; long axis along Y lies in layers
    supports="off",
    brim="auto",
)

# Parameters
CHANNEL_L = 100.0      # channel body length (Y)
TAB_L = 10.0           # finger tab beyond the body -> 110 total
CH_W = 14.0            # channel outer width (X)
CH_H = 12.0            # channel outer height (Z)
ROD_D = 6.0            # rod diameter
ROD_FLAT = 2.7         # rod half-height after flats (prints flat on the bed)
BAG_FOLD = 0.6         # folded bag thickness wrapped round the rod (2 x 0.3)
SLOT_W = 2.4           # side slot width (bag edge passes through, rod cannot)
TAB_T = 2.4            # finger tab thickness
ROD_L = 96.0           # rod length (without head)
HEAD_W, HEAD_H, HEAD_T = 16.0, 9.0, 2.4
GAP_X = 4.0            # space between the two bodies
BORE_D = ROD_D + 2 * BAG_FOLD + FIT["snug"]
BORE_R = BORE_D / 2
BORE_Z = CH_H / 2


def channel() -> Part:
    c = 0.6   # bottom chamfer
    t = 2.5   # top chamfer (45 deg, no overhang)
    hw = CH_W / 2
    outer = Polygon(
        (-hw + c, 0), (hw - c, 0), (hw, c), (hw, CH_H - t), (hw - t, CH_H),
        (-hw + t, CH_H), (-hw, CH_H - t), (-hw, c), align=None,
    )
    k = BORE_R * 0.70710678
    bore = Pos(0, BORE_Z, 0) * (
        Circle(BORE_R) + Polygon((-k, k), (0, BORE_R * 1.41421356), (k, k), align=None)
    )
    sh = SLOT_W / 2   # slot flares upward at 45 deg so its ceiling needs no support
    slot = Pos(0, BORE_Z, 0) * Polygon(
        (0, -sh), (hw + 2, -sh), (hw + 2, sh + hw + 2), (0, sh), align=None
    )
    prof = outer - bore - slot
    body = Pos(0, CHANNEL_L / 2, 0) * extrude(Plane.XZ * prof, CHANNEL_L / 2, both=True)
    # round the plan view at the entry end
    plan = Pos(0, CHANNEL_L / 2, 0) * extrude(
        Plane.XY * RectangleRounded(CH_W, CHANNEL_L, 2.5), CH_H
    )
    body = body & plan
    tr = CH_W / 2
    tab = Pos(0, CHANNEL_L + TAB_L - tr, 0) * Cylinder(tr, TAB_T, align=ON_BED)
    tab += Pos(0, CHANNEL_L - 1 + (TAB_L - tr + 1) / 2, 0) * Box(
        CH_W, TAB_L - tr + 1, TAB_T, align=ON_BED
    )
    tab = chamfer(tab.edges().group_by(Axis.Z)[0], 0.4)
    return body + tab


def rod() -> Part:
    r = ROD_D / 2
    cyl = Pos(0, 0, ROD_FLAT) * Rot(-90, 0, 0) * Cylinder(r, ROD_L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cyl = chamfer(cyl.edges().group_by(Axis.Y)[-1], 0.8)
    h = 2 * ROD_FLAT
    keep = Polygon((-1.3, 0), (1.3, 0), (5, 3.7), (5, h), (-5, h), (-5, 3.7), align=None)
    cyl = cyl & extrude(Plane.XZ * keep, ROD_L, both=True).moved(Location((0, ROD_L / 2, 0)))
    head = Pos(0, -HEAD_T / 2, 0) * extrude(
        Plane.XZ * Pos(0, HEAD_H / 2, 0) * RectangleRounded(HEAD_W, HEAD_H, 3.5),
        HEAD_T / 2, both=True,
    )
    return Pos(0, HEAD_T, 0) * (head + Pos(0, -HEAD_T, 0) * cyl)


def build():
    ch = Pos(-(CH_W / 2 + GAP_X / 2), 0, 0) * channel()
    rd = Pos(HEAD_W / 2 + GAP_X / 2, 0, 0) * rod()
    return [ch, rd]
