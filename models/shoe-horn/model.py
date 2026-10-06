"""shoe-horn: long (280 mm) shoe horn with a curved scoop blade, hanging hole and stiffening rib.

Spec: 280 mm long, 45 mm wide scoop blade at x=0 (concave across the width, 4 mm deep, round tip),
tapering into a 28 mm wide, 3 mm thick handle with a 10 mm hanging hole near x=266. A 3 mm wide,
8 mm tall rib with 45 deg ends runs along the handle (x=150..250) to stiffen it in bending.
Fits the 300 mm bed straight along X (no diagonal needed).

Orientation: printed flat, bottom (flat back of the blade + handle plate) on the bed, scoop
concave side and rib up. Shoe-horn bending (about Y) then loads the layers in tension/compression
along X, i.e. ALONG the layers. The blade back is flat (solid 3..7 mm thick) so the scoop prints
smooth with ZERO supports; the rib sits on the face opposite the bed (the horn is held with the
rib side outward; the scoop is concave on that same side, the heel slides on its smooth top).
Assumptions: PETG (flex + toughness); no longitudinal curve (blade is straight, tilt it in use);
3 mm minimum thickness; hang hole 10 mm for a hook/nail.
"""

from build123d import *

from cadlib import *

META = dict(
    material="PETG",
    quality="strong",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # flat on its back: plate in XY, bending runs along layers
    supports="auto",
    brim="auto",
)

# Parameters
LENGTH = 280.0
BLADE_W = 45.0        # scoop width
BLADE_L = 105.0       # full-width blade length before taper
TAPER_END = 150.0     # x where handle width is reached
HANDLE_W = 28.0
THICK = 3.0           # plate / shell thickness
SAG = 4.0             # scoop depth across the width
SAG_HANDLE = 0.05     # near-flat handle top (keeps loft topology identical)
HOLE_D = 10.0
HOLE_X = LENGTH - HANDLE_W / 2
RIB_W = 3.0
RIB_H = 8.0
RIB_X0 = 150.0
RIB_X1 = 250.0


def section(x: float, sag: float):
    """Closed wire at station x (YZ plane): flat bottom on the bed, concave arc top.

    The scoop is concave on top; its rims are THICK+sag high, centre line THICK high.
    """
    h = BLADE_W / 2
    w = Wire(
        [
            Line((-h, 0), (h, 0)),
            Line((h, 0), (h, THICK + sag)),
            ThreePointArc((h, THICK + sag), (0, THICK), (-h, THICK + sag)),
            Line((-h, THICK + sag), (-h, 0)),
        ]
    )
    return Plane(origin=(x, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)).location * w


def build() -> Part:
    stations = [(0.0, SAG), (BLADE_L, SAG), (TAPER_END, SAG_HANDLE), (LENGTH, SAG_HANDLE)]
    wires = [section(x, s) for x, s in stations]
    body = Solid.make_loft(wires, ruled=True)

    # plan outline: round tip, blade, taper, handle, round end
    r = BLADE_W / 2
    plan = Pos(r, 0) * Circle(r)
    plan += Pos((r + BLADE_L) / 2, 0) * Rectangle(BLADE_L - r, BLADE_W)
    plan += Polygon(
        (BLADE_L - 1, -r), (TAPER_END, -HANDLE_W / 2), (TAPER_END, HANDLE_W / 2), (BLADE_L - 1, r),
        align=None,
    )
    plan += Pos((TAPER_END + LENGTH - HANDLE_W / 2) / 2, 0) * Rectangle(
        LENGTH - HANDLE_W / 2 - TAPER_END + 1, HANDLE_W
    )
    plan += Pos(HOLE_X, 0) * Circle(HANDLE_W / 2)
    outline = extrude(Plane.XY.offset(-30) * plan, 40)
    part = Part() + body
    part = part & outline

    # stiffening rib on the back of the handle (below the plate), 45 deg ends
    rib_top = THICK + RIB_H
    rib_sk = Polygon(
        (RIB_X0, 2.0),
        (RIB_X0 + RIB_H - 1, rib_top),
        (RIB_X1 - RIB_H + 1, rib_top),
        (RIB_X1, 2.0),
        align=None,
    )
    rib = extrude(Plane.XZ * rib_sk, RIB_W / 2, both=True)
    part = part + rib

    # hanging hole (vertical in print orientation)
    part = part - Pos(HOLE_X, 0, -5) * Cylinder(HOLE_D / 2, 30, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # 0.4 mm elephant-foot chamfer on the outer bottom edges (hole edge excluded)
    try:
        bottom = part.faces().sort_by(Axis.Z)[0]
        part = chamfer(bottom.outer_wire().edges(), 0.4)
    except Exception:
        pass
    return part
