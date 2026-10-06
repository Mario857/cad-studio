"""key-rack: wall key rack, 160 mm wide, 4 short upturned hooks + top shelf for phone/wallet.

Spec: 160 x 54 mm back plate (6 mm thick) screwed to the wall with two M4 countersunk
screws (heads flush on the front face, between the hooks and the shelf, driver access
from the front). 4 J-hooks (8 mm wide at the tip, 6 mm arm, 8 mm upturned lip,
18 mm projection) at 36 mm pitch carry ~150 g each (stress < 1 MPa, hugely over-built).
Shelf on top: 25 mm deep, 6 mm thick, 2 mm front rim, 45 deg gusset underneath.

Print orientation: standing on its end (model X up, 160 mm tall). The whole rack is an
extrusion along X, so the J-hook profile and the shelf profile lie IN the layer plane
(hook bending load runs along the layers, never across them) and nothing overhangs.
Each hook is widened toward the wall with a 45 deg lower flank so its first layers grow
out of the plate without supports. Brim on: slim 160 mm tall print.
Known WARN (accepted): the audit flags 'wobbly on bed (tips at 5 deg)' because the end
face is only ~5 cm2; this is deliberate, the brim (and slow outer walls) hold the 160 mm tall
print, and the strength gain (hook load along layers, zero supports) outweighs it.

Assumptions: wall is flat, 2 screws fit M4 (plug/screw choice is up to the wall type);
keys on split rings ~25 mm; PLA is fine indoors (use PETG if the wall gets warm/sunny).
Hook root is a sawtooth (45 deg flank on the -X side) while the tips are evenly spaced.
"""

from build123d import *

from cadlib import *

META = dict(
    material="PETG",
    quality="standard",
    standing=False,
    loads=[dict(at=(x, 24, 18), grams=150) for x in (-54, -18, 18, 54)]
    + [dict(at=(0, 14, 56), grams=300)],
    print_orientation=(0, -90, 0),  # stand on the -X end: layers = YZ profile
    supports="off",
    brim="on",
)

# Parameters
WIDTH = 160.0
PLATE_T = 6.0           # back plate thickness (y 0..PLATE_T)
HEIGHT = 54.0           # plate height (z 0..HEIGHT)
SHELF_D = 25.0          # shelf depth from wall (y)
SHELF_T = 6.0
RIM_H = 2.0             # front rim of shelf
RIM_W = 3.0
GUSSET = 8.0            # 45 deg gusset under shelf

HOOK_N = 4
HOOK_PITCH = 36.0       # tip pitch
HOOK_Z = 8.0            # underside of the arm
HOOK_ARM_T = 6.0        # arm thickness (z)
HOOK_PROJ = 18.0        # projection from plate face
HOOK_LIP_W = 5.0
HOOK_LIP_H = 8.0        # lip height above arm top
HOOK_TIP_W = 8.0        # hook width (x) at the tip
HOOK_ROOT_W = HOOK_TIP_W + HOOK_PROJ  # 45 deg lower flank -> self-supporting when printed on end

SCREW_X = 68.0
SCREW_Z = 31.0


def hook() -> Part:
    """Single hook at x0 = 0 (lower-x flank starts at x=0 at the plate face)."""
    yt = PLATE_T + HOOK_PROJ
    ztop = HOOK_Z + HOOK_ARM_T
    zl = ztop + HOOK_LIP_H
    prof = Polygon(
        (PLATE_T - 3, HOOK_Z), (yt, HOOK_Z), (yt, zl - 2), (yt - 2, zl),
        (yt - HOOK_LIP_W, zl), (yt - HOOK_LIP_W, ztop), (PLATE_T - 3, ztop),
        align=None,
    )
    side = extrude(Plane.YZ.offset(-3) * prof, HOOK_ROOT_W + 6)
    ytop = 40.0
    plan = Polygon(
        (-3, PLATE_T - 3), (HOOK_ROOT_W, PLATE_T - 3), (HOOK_ROOT_W, ytop),
        (ytop - PLATE_T, ytop), align=None,
    )
    prism = extrude(Plane.XY * plan, 40)
    return side & prism


def build() -> Part:
    h = HEIGHT
    prof = Polygon(
        (0, 0), (PLATE_T, 0), (PLATE_T, h - SHELF_T - GUSSET),
        (PLATE_T + GUSSET, h - SHELF_T), (SHELF_D, h - SHELF_T),
        (SHELF_D, h + RIM_H), (SHELF_D - RIM_W, h + RIM_H),
        (SHELF_D - RIM_W, h), (0, h),
        align=None,
    )
    body = extrude(Plane.YZ * prof, WIDTH / 2, both=True)

    for i in range(HOOK_N):
        tip_c = (i - (HOOK_N - 1) / 2) * HOOK_PITCH
        x0 = tip_c + HOOK_TIP_W / 2 - HOOK_ROOT_W
        body = body + Pos(x0, 0, 0) * hook()

    # chamfer the two end faces (bed end gets the elephant-foot chamfer)
    ends = body.edges().filter_by(Axis.X, reverse=True)
    for sx in (-WIDTH / 2, WIDTH / 2):
        sel = [e for e in ends if abs(e.center().X - sx) < 0.01]
        body = chamfer(sel, 0.6)

    # two M4 countersunk screws from the front face
    for sx in (-SCREW_X, SCREW_X):
        body = body - at(sx, PLATE_T, SCREW_Z, -90, 0, 0) * bolt_hole("M4", PLATE_T + 1, head="csk")
    return body
