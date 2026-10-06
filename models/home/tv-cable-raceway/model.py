"""tv-cable-raceway: wall cord cover (raceway) kit hiding TV cables.

Spec: 300 mm base channel (inner 25 x 12 mm) with countersunk M3 screw holes in the floor and a
flat back for double-sided tape; a snap-on lid (legs outside the base walls, 45° bumps engaging
V-grooves on the base outer walls); a slip-over end cap and a slip-over 90° corner cover (both
open at the back, sized to sleeve over the assembled raceway end). Segments butt-join end to end;
runs meeting at a corner are cut short and their ends hidden by the corner cover.

Coordinates: the kit is laid out exactly as printed (print_orientation fixed to (0, 0, 0)):
base channel back-down, lid / end cap / corner cover outer face down. Base + lid are laid
diagonally (DIAG_ANGLE): a 300 mm part straight along Y fails the H2C per-nozzle printable area. In use, the base "back" (z=0) faces the wall.

ASSUMPTIONS
- Wall 2 mm, floor 2.5 mm (needed so an M3 countersunk head sits fully in the floor).
- Screws: M3 (or #4/#5 wood screws) countersunk, every 100 mm; or tape on the flat 29 mm back.
- Snap: SNAP_DEPTH 0.4 mm interference on a 1.2 mm x 8 mm ABS leg (~1 % strain, re-usable).
- End cap and corner cover are friction slip-overs (COVER_CLEAR per side); tape them if loose.
- Check WARNs are intended: 4 separate bodies (kit printed together); thin-wall warn is the
  1.2 mm lid snap legs (deliberately thin so they flex) and the 0.6 mm-deep snap grooves.
- Corner = flat 90° turn in the wall plane (e.g. horizontal run turning to vertical).
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # kit is modelled in print layout (see docstring)
    supports="off",
    brim="auto",
    copies=1,
)

# --- channel -----------------------------------------------------------------
LENGTH = 300.0          # base / lid length (along Y on the plate)
INNER_W = 25.0          # cable space width
INNER_H = 12.0          # cable space height (floor top to lid underside)
WALL = 2.0              # base side wall
FLOOR = 2.5             # base floor (back)
BOTTOM_CHAMFER = 0.4    # elephant-foot chamfer

# --- screw holes -------------------------------------------------------------
SCREW = "M3"            # countersunk
SCREW_PITCH = 100.0     # holes at -100, 0, +100 mm

# --- snap fit ----------------------------------------------------------------
LID_T = 2.0             # lid top plate
LEG_T = 1.2             # lid leg thickness
LEG_L = 8.0             # leg length below base top
SIDE_CLEAR = 0.2        # gap between lid leg and base outer wall
SNAP_DEPTH = 0.4        # bump interference past the base wall face
GROOVE_DEPTH = 0.6      # V-groove depth in base outer wall (>= SNAP_DEPTH + clearance)
GROOVE_FLAT = 0.4       # flat bottom height of the groove
LID_EDGE_CHAMFER = 0.8  # outer top edges of the lid

# --- end cap / corner cover --------------------------------------------------
COVER_CLEAR = 0.3       # slip-over clearance per side
COVER_WALL = 1.6
COVER_TOP = 2.0
SLEEVE = 15.0           # overlap onto the raceway
CORNER_ARM = 15.0       # extra arm length beyond the corner square (+ SLEEVE)

GAP = 6.0               # spacing between parts on the plate
DIAG_ANGLE = 30.0       # long parts laid diagonally (300 mm along Y hits the H2C nozzle-area limit)

# derived
BW = INNER_W + 2 * WALL                 # base outer width 29
BH = FLOOR + INNER_H                    # base height 14.5
GZ = BH - LEG_L + 1.0                   # groove / bump centre height
LEG_IN = BW / 2 + SIDE_CLEAR            # lid leg inner face x
LW = LEG_IN + LEG_T                     # lid half width
TOT_H = BH + LID_T                      # assembled height
CIW = 2 * LW + 2 * COVER_CLEAR          # cover inner width
CIH = TOT_H + COVER_CLEAR               # cover inner height
COW = CIW + 2 * COVER_WALL              # cover outer width
COH = CIH + COVER_TOP                   # cover outer height


def _prism(pts, length):
    """Extrude an XZ profile along Y, centred on y=0."""
    return Pos(0, length / 2, 0) * extrude(Plane.XZ * Polygon(*pts, align=None), amount=length)


def base() -> Part:
    h, c, g, f = BW / 2, BOTTOM_CHAMFER, GROOVE_DEPTH, GROOVE_FLAT / 2
    right = [(h - c, 0), (h, c),
             (h, GZ - f - g), (h - g, GZ - f), (h - g, GZ + f), (h, GZ + f + g),
             (h, BH), (INNER_W / 2, BH), (INNER_W / 2, FLOOR)]
    left = [(-x, z) for x, z in reversed(right)]
    part = _prism(right + left, LENGTH)
    n = int(LENGTH // SCREW_PITCH)
    for i in range(n):
        y = (i - (n - 1) / 2) * SCREW_PITCH
        part -= Pos(0, y, FLOOR) * bolt_hole(SCREW, FLOOR + 1, head="csk")
    return part


def lid() -> Part:
    """Lid profile in print orientation: top plate on the bed (z' = TOT_H - z_in_use)."""
    zb = lambda z: TOT_H - z  # noqa: E731
    a, ch = SNAP_DEPTH + SIDE_CLEAR, LID_EDGE_CHAMFER
    tip = GZ - a - 0.4
    right = [(LW - ch, 0), (LW, ch), (LW, zb(tip)), (LEG_IN, zb(tip)),
             (LEG_IN, zb(GZ - a)), (LEG_IN - a, zb(GZ)), (LEG_IN, zb(GZ + a)),
             (LEG_IN, LID_T)]
    left = [(-x, z) for x, z in reversed(right)]
    return _prism(right + left, LENGTH)


def _chamfer_bed(part, d=BOTTOM_CHAMFER):
    try:
        return chamfer(part.edges().group_by(Axis.Z)[0], d)
    except Exception:
        return part


def end_cap() -> Part:
    """Slip-over end cap, outer (front) face on bed, open at -Y and toward the wall (+Z)."""
    depth = SLEEVE + COVER_WALL
    outer = Box(COW, depth, COH, align=(Align.CENTER, Align.MIN, Align.MIN))
    cav = Pos(0, -1, COVER_TOP) * Box(CIW, SLEEVE + 1, CIH + 1,
                                     align=(Align.CENTER, Align.MIN, Align.MIN))
    return _chamfer_bed(outer - cav)


def corner() -> Part:
    """Slip-over 90° corner cover (L), arms along +X and +Y, open arm ends and back."""
    arm = COW + CORNER_ARM + SLEEVE
    mn = (Align.MIN, Align.MIN, Align.MIN)
    outer = Box(arm, COW, COH, align=mn) + Box(COW, arm, COH, align=mn)
    cav = (Pos(COVER_WALL, COVER_WALL, COVER_TOP) * Box(arm, CIW, CIH + 1, align=mn)
           + Pos(COVER_WALL, COVER_WALL, COVER_TOP) * Box(CIW, arm, CIH + 1, align=mn))
    return _chamfer_bed(outer - cav)


def build():
    # base + lid side by side, then the pair turned diagonally on the plate
    b = Pos(-(BW / 2 + GAP / 2), 0, 0) * base()
    l = Pos(LW + GAP / 2, 0, 0) * lid()
    band = [Rot(0, 0, DIAG_ANGLE) * p for p in (b, l)]
    bb = band[0].bounding_box().add(band[1].bounding_box())
    # accessories in the two free triangular corners of the plate
    c = Pos(bb.max.X - COW - CORNER_ARM - SLEEVE, bb.max.Y - COW - CORNER_ARM - SLEEVE, 0) * corner()
    e = Pos(bb.min.X + COW / 2, bb.min.Y, 0) * end_cap()
    return band + [c, e]
