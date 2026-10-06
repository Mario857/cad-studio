"""cat-hole-trowel: 160 mm leave-no-trace backpacking trowel, curved blade, serrated edge, depth marks.

Spec: 160 mm long, 52 mm wide blade, 2.4 mm thick curved (scoop) blade - the outline is cut from a
R60 cylindrical shell, so the whole tool is curved across its width for stiffness. Triangular spine rib
(4 mm deep, 45° flanks) under the centreline, tapering out before the tip. Serrated top edge (pitch 4,
2 mm teeth) for cutting roots, pointed tip, 30 mm wide handle, diamond hang hole (8 mm).
Depth marks: grooves across the scoop at 5 cm (1 line), 10 cm (2 lines) and 15 cm (3 lines) from the
tip - dig until the 15 cm mark is level with the ground (cat-hole 15-20 cm deep, 60 m from water).
In-use: length along X (tip at +X), width Y, scoop concave up (+Z).

Print: on its straight lower (-Y) edge, rotated 90° about X, so the extrusion lines and layers run
along the length (bending strength while prying), the scoop curve and 45° rib print without supports.
That is why the outline has a straight bottom edge (with a 2 mm stiffening flange that forms a
~15 mm wide stable footprint) and the handle sits on that side.
Hardware: none.
Assumptions: target <= 25 g; asymmetric (straight-backed) outline is the price of support-free
edge-on printing.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[],
    print_orientation=(90, 0, 0),  # on the straight -Y edge: layers along the length
    supports="off",
    brim="on",
)

LENGTH = 160.0
BLADE_W = 52.0
HANDLE_W = 30.0
HANDLE_L = 55.0           # handle length from the back end
TIP_LEN = 20.0            # pointed tip length
THICK = 2.4               # blade thickness (loaded)
SCOOP_R = 60.0            # cross curvature radius
RIB_H = 4.0               # spine rib depth (45° flanks)
RIB_END = 115.0           # rib fades out here (x)
SERR_X0, SERR_X1 = 70.0, 128.0
SERR_PITCH = 4.0
SERR_DEPTH = 2.0
FLANGE_T = 2.0            # back-edge flange thickness
FLANGE_DROP = 4.0         # flange reaches this far below the blade underside
HANG_D = 8.0              # diamond hang hole (diagonal)
HANG_X = 26.0
MARK_W = 0.8
MARK_DEPTH = 0.6
MARK_SPACING = 2.4

Y0 = -BLADE_W / 2                    # straight bottom (print bed) edge
Y1 = BLADE_W / 2
YH = Y0 + HANDLE_W


def _outline():
    pts = [(0, Y0), (LENGTH - TIP_LEN, Y0), (LENGTH, 0.0), (LENGTH - 30, Y1)]
    # serrated top edge, from the tip side back
    x = SERR_X1
    while x - SERR_PITCH >= SERR_X0:
        pts += [(x, Y1), (x - SERR_PITCH / 2, Y1 - SERR_DEPTH)]
        x -= SERR_PITCH
    pts += [(x, Y1), (HANDLE_L + 8, Y1), (HANDLE_L, YH), (0, YH)]
    return Polygon(*pts, align=None)


def _shell(r_in, r_out) -> Part:
    c = Pos(LENGTH / 2, 0, SCOOP_R) * Rot(0, 90, 0)
    return c * Cylinder(r_out, LENGTH + 10) - c * Cylinder(r_in, LENGTH + 12)


def build() -> Part:
    prism = extrude(Plane.XY.offset(-30) * _outline(), 60)
    blade = prism & _shell(SCOOP_R, SCOOP_R + THICK)
    # spine rib under the centreline, 45° flanks, tapering out toward the tip
    tri = Polygon((-RIB_H - 1, 0), (RIB_H + 1, 0), (0, -RIB_H - 1), align=None)
    rib = Pos(4, 0, -THICK + 1) * extrude(Plane.YZ * tri, RIB_END - 4)
    taper = Pos(RIB_END, 0, -THICK) * Rot(0, -30, 0) * Box(60, 20, 20, align=(Align.MIN, Align.CENTER, Align.MAX))
    rib -= taper
    blade += rib & prism
    # back-edge flange: stiffens the straight edge and is the wide, stable print footprint
    fl_z0 = -THICK - FLANGE_DROP
    fl_z1 = SCOOP_R - (SCOOP_R ** 2 - Y0 ** 2) ** 0.5 + THICK
    blade += Pos(0, Y0, fl_z0) * Box(LENGTH - TIP_LEN - 4, FLANGE_T, fl_z1 - fl_z0, align=(Align.MIN, Align.MIN, Align.MIN))
    # hang hole (diamond: 45° roof when printed on edge)
    blade -= Pos(HANG_X, (Y0 + YH) / 2, -30) * extrude(Rot(0, 0, 45) * Rectangle(HANG_D / 1.414, HANG_D / 1.414), 60)
    # depth marks: 1/2/3 grooves at 5/10/15 cm from the tip, cut into the scoop face
    skin = _shell(SCOOP_R - 1, SCOOP_R + MARK_DEPTH)
    for n, d in ((1, 50.0), (2, 100.0), (3, 150.0)):
        for i in range(n):
            x = LENGTH - d + (i - (n - 1) / 2) * MARK_SPACING
            blade -= skin & Pos(x, 0, 0) * Box(MARK_W, BLADE_W + 10, 100)
    return blade
