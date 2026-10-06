"""first-aid-case: compact hinged first-aid box with O-ring cord seal, snap latch, raised cross, lanyard lug.

Spec: inner 120 x 80 x 40 mm (base 30 mm deep + lid 10 mm). Walls 1.6 mm (not structurally loaded,
kept light), rims 4.9 mm. The base rim top has a groove for a 2 mm O-ring cord (1.5 mm deep, cord
stands 0.5 mm proud -> ~25 % squeeze under the lid's flat rim band). Rear hinge: 5 knuckles on a
printed octagonal pin (press fit in the 3 base knuckles, free in the 2 lid knuckles). Front snap latch:
a flex tab on the lid hooks under a ridge on the base rim - pull the tab's bottom outward to open.
Raised cross: a separate cross insert (print in red if you like) pushed through a cross window from
inside the lid; its flange bears on the lid ceiling, it stands 1.2 mm proud (keeps the lid printable
flat on its top face). Lanyard lug
with a Ø5 hole on the left (-X) end.

Print layout (returned parts are already in print pose, printed together, no supports):
base upright at the origin, lid flipped next to it (-Y), hinge pin + cross insert flat behind (+Y).
Hardware: 2 mm O-ring cord (NBR/silicone), ~410 mm cut and butt-glued (CA) into a ring, pressed into
the groove; optional lanyard / paracord.
Assumptions: splash/rain-proof, not submersible; the 1.2 mm / 0.9 mm latch catch ledges are left
flat (short overhangs that print unsupported); the case is a container (no structural load).
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # parts are modelled in print pose
    supports="off",               # only the 1.2 / 0.9 mm latch catch ledges overhang; they print unsupported
    brim="auto",
)

INNER_L = 120.0
INNER_W = 80.0
INNER_R = 4.0
BASE_DEPTH = 30.0         # inner depth of the base
LID_DEPTH = 10.0          # inner depth of the lid (total 40)
WALL = 1.6
FLOOR = 1.6
RIM = 4.9                 # rim band width (seal face)
BAND_H = 6.0              # height of the thick rim bands
# O-ring cord
CORD_D = 2.0
GROOVE_W = CORD_D + 0.1
GROOVE_DEPTH = 1.5        # cord stands 0.5 proud
GROOVE_IN = (RIM - GROOVE_W) / 2   # groove offset from the inner wall
# raised cross on the lid: separate insert through a cross window (prints flat, can be red)
RAISE = 1.2               # stands proud of the lid top
CROSS_ARM = 44.0
CROSS_W = 13.0
CROSS_FIT = FIT["press"]  # window grows by this per side
CROSS_FLANGE = 2.5        # retaining flange inside the lid
CROSS_FLANGE_T = 1.2
# hinge
HINGE_LEN = 100.0
KNUCKLES = 5
KNUCKLE_GAP = 0.6
KNUCKLE_R = 4.0
AXIS_OUT = 4.5            # hinge axis outside the back rim face
PIN_AF = 3.0              # octagonal pin across flats
BASE_PIN_HOLE = PIN_AF + 2 * FIT["press"]   # 3.2: octagon corners press in
LID_PIN_HOLE = PIN_AF + 2 * FIT["loose"]    # 3.8: free to turn
# latch
LATCH_W = 24.0
TAB_T = 1.6
TAB_CLEAR = 1.5           # tab inner face off the rim face
RIDGE_D = 1.2
HOOK_D = 0.9
# lanyard lug
LUG_HOLE_D = 5.0
LUG_W = 14.0
LUG_OUT = 10.0
STEEP = 1.2               # rise/run of the 'chamfer' faces (> 1 = steeper than 45°)
# print layout
LID_GAP = 25.0

OUT_L = INNER_L + 2 * RIM
OUT_W = INNER_W + 2 * RIM
HB = FLOOR + BASE_DEPTH                     # parting plane
LID_TOP = HB + LID_DEPTH + FLOOR            # lid top plate surface
YB = OUT_W / 2
YA = YB + AXIS_OUT
SEG = (HINGE_LEN - (KNUCKLES - 1) * KNUCKLE_GAP) / KNUCKLES


def _rr(off: float):
    """Rounded rectangle outline offset `off` from the cavity."""
    return RectangleRounded(INNER_L + 2 * off, INNER_W + 2 * off, INNER_R + off)


def _yz(pts, x0, x1) -> Part:
    """Extrude a (y, z) polygon along X from x0 to x1."""
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1]))
    if area < 0:
        pts = pts[::-1]
    face = Plane.YZ * Polygon(*pts, align=None)
    return Pos(x0, 0, 0) * extrude(face, x1 - x0)


def _segments(owner: str):
    for i in range(KNUCKLES):
        if (i % 2 == 0) == (owner == "base"):
            x0 = -HINGE_LEN / 2 + i * (SEG + KNUCKLE_GAP)
            yield x0, x0 + SEG


def _knuckles(owner: str) -> Part:
    s = -1 if owner == "base" else 1
    parts = []
    y_in = YB - (RIM - WALL)
    for x0, x1 in _segments(owner):
        z_top = HB + s * KNUCKLE_R
        if s > 0:   # lid: gusset steeper than 45° up to the lid top
            pts = [(y_in, HB), (YA, HB), (YA, z_top), (YA - (LID_TOP - z_top) / STEEP, LID_TOP), (y_in, LID_TOP)]
        else:
            pts = [(y_in, HB), (YA, HB), (YA, z_top), (y_in, z_top - (YA - y_in) * STEEP)]
        parts.append(_yz(pts, x0, x1))
        parts.append(Pos(x0, YA, HB) * Rot(0, 90, 0) * Cylinder(KNUCKLE_R, SEG, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        # 45° teardrop point on the print-underside of the knuckle (base: down, lid: up = down when flipped)
        t = KNUCKLE_R * 0.7071
        parts.append(_yz([(YA - t, HB + s * t), (YA, HB + s * 2 * t), (YA + t, HB + s * t), (YA, HB)], x0, x1))
    return parts


def build_base() -> Part:
    z_band = HB - BAND_H
    z_ch = z_band - (RIM - WALL) * STEEP
    body = extrude(_rr(WALL), z_ch)
    body += loft([Plane.XY.offset(z_ch) * _rr(WALL), Plane.XY.offset(z_band) * _rr(RIM)])
    body += Pos(0, 0, z_band) * extrude(_rr(RIM), BAND_H)
    body = chamfer(body.edges().group_by(Axis.Z)[0], 0.4)
    for k in _knuckles("base"):
        body += k
    # latch ridge on the front rim face (catch face flat underneath)
    y0 = -YB
    body += _yz([(y0 + 0.3, HB - 4), (y0 - RIDGE_D, HB - 4), (y0 - RIDGE_D, HB - 2.5), (y0 + 0.3, HB - 1.3)],
                -LATCH_W / 2, LATCH_W / 2)
    # lanyard lug on -X, 45° underside
    xw = -(INNER_L / 2 + WALL) + 0.3
    zb = 5.0
    lug_pts = [(xw, zb), (xw - LUG_OUT, zb + LUG_OUT * STEEP), (xw - LUG_OUT, zb + LUG_OUT * STEEP + 7), (xw, zb + LUG_OUT * STEEP + 7)]
    lug = extrude(Plane.XZ * Polygon(*lug_pts, align=None), LUG_W / 2, both=True)
    lug = fillet(lug.edges().filter_by(Axis.Y).group_by(Axis.X)[0], 2.0)
    body += lug
    body -= Pos(xw - LUG_OUT / 2 - 0.5, 0, zb + LUG_OUT * STEEP + 3) * teardrop_hole(LUG_HOLE_D, LUG_W + 2, along="Y")
    # cavity + seal groove + hinge pin hole
    body -= Pos(0, 0, FLOOR) * extrude(_rr(0), HB)
    groove = _rr(GROOVE_IN + GROOVE_W) - _rr(GROOVE_IN)
    body -= Pos(0, 0, HB - GROOVE_DEPTH) * extrude(groove, GROOVE_DEPTH + 1)
    body -= Pos(0, YA, HB) * teardrop_hole(BASE_PIN_HOLE, HINGE_LEN + 2, along="X", tip="+Z")
    return body


def build_lid_closed() -> Part:
    body = Pos(0, 0, HB) * extrude(_rr(RIM), LID_TOP - HB)
    for k in _knuckles("lid"):
        body += k
    # latch tab: flex strip joined to the lid only near the top
    y_in = -YB - TAB_CLEAR
    body += _yz([(y_in, HB - 6.5), (y_in - TAB_T, HB - 6.5), (y_in - TAB_T, LID_TOP), (y_in, LID_TOP)],
                -LATCH_W / 2, LATCH_W / 2)
    body += _yz([(-YB + 0.3, HB + 7), (y_in - 0.1, HB + 7), (y_in - 0.1, LID_TOP), (-YB + 0.3, LID_TOP)],
                -LATCH_W / 2, LATCH_W / 2)
    zc = HB - 4.2
    tip = y_in + (TAB_CLEAR - RIDGE_D) + HOOK_D       # overlaps the ridge by HOOK_D
    hook = [(y_in - 0.1, zc), (tip, zc), (tip, zc - 0.5), (y_in - 0.1, zc - 0.6 - (tip - y_in))]
    body += _yz(hook, -LATCH_W / 2, LATCH_W / 2)
    # cavity: flat seal band, 45° chamfer, thin walls
    z1 = HB + 3.0
    z2 = z1 + (RIM - WALL) * STEEP
    cav = Pos(0, 0, HB - 1) * extrude(_rr(0), z1 - HB + 1)
    cav += loft([Plane.XY.offset(z1) * _rr(0), Plane.XY.offset(z2) * _rr(RIM - WALL)])
    cav += Pos(0, 0, z2) * extrude(_rr(RIM - WALL), HB + LID_DEPTH - z2)
    body -= cav
    body -= Pos(0, YA, HB) * teardrop_hole(LID_PIN_HOLE, HINGE_LEN + 2, along="X", tip="-Z")
    # cross-shaped window for the raised cross insert
    body -= Pos(0, 0, HB) * extrude(_cross(CROSS_FIT), LID_TOP - HB + 1)
    return body


def _cross(grow: float = 0.0):
    return Rectangle(CROSS_ARM + 2 * grow, CROSS_W + 2 * grow) + Rectangle(CROSS_W + 2 * grow, CROSS_ARM + 2 * grow)


def build_cross() -> Part:
    """Separate cross insert (print it in red): pushed out through the lid window from inside,
    stands RAISE proud; the flange bears on the lid ceiling. Press fit + optional drop of CA."""
    flange = extrude(offset(_cross(), CROSS_FLANGE), CROSS_FLANGE_T)
    plug = extrude(_cross(), CROSS_FLANGE_T + FLOOR + RAISE)
    part = flange + plug
    return chamfer(part.edges().group_by(Axis.Z)[0], 0.3)


def build_pin() -> Part:
    r = PIN_AF / 2 / 0.92388      # octagon circumradius from across-flats
    pin = extrude(Plane.YZ * RegularPolygon(r, 8, rotation=22.5), HINGE_LEN)
    return Pos(-HINGE_LEN / 2, YA + 15, PIN_AF / 2) * pin


def build():
    base = build_base()
    lid = build_lid_closed()
    lid = Pos(0, -(OUT_W + LID_GAP + 2 * AXIS_OUT), LID_TOP) * Rot(180, 0, 0) * lid
    cross = Pos(0, OUT_W / 2 + 50, 0) * build_cross()
    return [base, lid, build_pin(), cross]
