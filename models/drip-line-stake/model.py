"""drip-line-stake: 150 mm ground stake with a snap-in clip for drip micro-tubing.

Spec: flat stake, 150 mm overall, pushed into the soil up to a depth-stop wing. A C-clip at the
top snaps over 4 mm or 6 mm micro-tubing (two variants, labelled 4 / 6 on the wing) and holds
the tube centre (dripper end) 20 mm above the soil. Set of 20 = 10 pairs via copies.
Prints lying flat so the layers run along the stake and around the clip (strong in bending,
clip flexes within the layer plane).
Material: AzureFilm ABS PLUS. ABS+ yellows/embrittles after a season or two in full sun; the
user's "AzureFilm ASA @BBL H2C 0.4 nozzle" preset is the long-life swap (same geometry).

Assumptions:
- Micro-tubing OD is exactly 4.0 / 6.0 mm (the "4/6 mm" sizes; for 4/7 or 5/7 tube change
  TUBE_ODS). Clip bore = OD + 2 x TUBE_FIT (press 0.10) so it grips without crushing; the snap
  mouth is SNAP_RATIO x OD wide with a 45° lead-in.
- The tube runs horizontally through the clip, perpendicular to the stake face.
- Soil line = underside of the depth-stop wing.
- One 4 mm + one 6 mm stake per copy (2 separate bodies is intended). The thinnest spots
  (~0.8 mm) are the blunted stake point and the clip's lead-in lips, by design.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[],
    print_orientation=(90, 0, 0),  # lie flat: layers along the stake and around the clip
    supports="off",
    brim="auto",
    copies=10,                      # x 2 variants = 20 stakes
)

STAKE_LEN = 150.0      # tip to top of clip
DRIP_HEIGHT = 20.0     # tube centre above the soil line
TUBE_ODS = (4.0, 6.0)
TUBE_FIT = FIT["press"]
SNAP_RATIO = 0.72      # mouth width / tube OD
CLIP_WALL = 2.2
CLIP_T = 8.0           # clip width along the tube
STAKE_W = 9.0
STAKE_T = 5.0
TIP_LEN = 25.0
WING_W = 26.0
WING_H = 12.0
LABEL_SIZE = 7.5     # glyph height ~5.3 mm
VARIANT_GAP = 14.0     # spacing between the two variants on the plate


def stake(tube_od: float) -> Part:
    r_in = (tube_od + 2 * TUBE_FIT) / 2
    r_out = r_in + CLIP_WALL
    zc = STAKE_LEN - r_out                 # tube centre
    soil = zc - DRIP_HEIGHT
    # 2D profile in XZ (local x = X, local y = Z)
    w, ww, top = STAKE_W / 2, WING_W / 2, soil + 3 + (WING_W - STAKE_W) / 2
    outline = Polygon(
        (-0.6, 0), (0.6, 0), (w, TIP_LEN), (w, soil - 6), (ww, soil), (ww, soil + 3), (w, top), (w, zc),
        (-w, zc), (-w, top), (-ww, soil + 3), (-ww, soil), (-w, soil - 6), (-w, TIP_LEN), align=None,
    )   # stake + depth-stop wing (underside tapers so it pushes into the soil)
    flat = extrude(Plane.XZ * outline, STAKE_T, dir=(0, 1, 0))   # y 0..STAKE_T
    flat = chamfer(flat.edges().group_by(Axis.Y)[0], 0.4)

    ring = Pos(0, 0, zc) * (Cylinder(r_out, CLIP_T, rotation=(90, 0, 0), align=(Align.CENTER, Align.CENTER, Align.MAX))
                            - Cylinder(r_in, CLIP_T, rotation=(90, 0, 0), align=(Align.CENTER, Align.CENTER, Align.MAX)))
    # boss joining ring to stake
    neck = Pos(0, 0, zc - r_out - 3) * Box(STAKE_W, CLIP_T, 3 + CLIP_WALL, align=(Align.CENTER, Align.MIN, Align.MIN))
    part = flat + ring + neck
    # snap mouth on top with 45° lead-in
    mouth = SNAP_RATIO * tube_od
    cut = Polygon(
        (-mouth / 2, 0), (mouth / 2, 0), (mouth / 2 + 3, 3), (-mouth / 2 - 3, 3), align=None,
    )
    mouth_z = zc + (r_in ** 2 - (mouth / 2) ** 2) ** 0.5 - 0.2
    part -= Pos(0, 0, mouth_z) * extrude(Plane.XZ * cut, CLIP_T + 1, dir=(0, 1, 0))
    part -= Pos(0, -0.5, mouth_z - 1) * Box(mouth, CLIP_T + 2, r_out, align=(Align.CENTER, Align.MIN, Align.MIN))
    part -= Pos(0, 0, zc) * Cylinder(r_in, 3 * CLIP_T, rotation=(90, 0, 0))
    # size label sunk into the top face of the wing
    txt = label(f"{tube_od:g}", size=LABEL_SIZE, depth=0.6)
    part -= Pos(0, STAKE_T - 0.6, soil + 4) * Rot(-90, 0, 0) * Rot(0, 0, 180) * txt
    return part


def build():
    return [Pos(i * (WING_W + VARIANT_GAP), 0, 0) * stake(od) for i, od in enumerate(TUBE_ODS)]
