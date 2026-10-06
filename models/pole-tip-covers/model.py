"""pole-tip-covers: transport caps for trekking-pole carbide tips, with lanyard hole. Set of 2.

Spec: closed cap, 17 mm OD x 39 mm. Tapered bore Ø12.4 at the mouth -> Ø9.6 at 30 mm deep, so any
tip/ferrule of Ø10-12 mm wedges in snugly at its own depth (taper wedge fit). The carbide point lands
in a 45° cone pocket below the bore, backed by a solid 6 mm end, so it cannot punch through into a pack
or car seat. Ø3.5 lanyard hole through the solid end (tie the two caps together or to the pole strap).
In-use = print pose: mouth up, closed end on the bed, bore vertical (no supports).
Hardware: ~30 cm thin cord (optional).
Assumptions: tip + ferrule 30 mm long, Ø10-12 mm, roughly cylindrical/slightly conical.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # mouth up
    supports="off",
    brim="auto",
    copies=2,
)

OD = 17.0
BORE_TOP_D = 12.4          # mouth (fits Ø12 snug at the top)
BORE_BOT_D = 9.6           # bottom of the 30 mm bore (Ø10 wedges near the bottom)
BORE_DEPTH = 30.0
END_T = 6.0                # solid end below the point pocket
POINT_POCKET_H = 3.0       # 45° cone for the carbide point
LANYARD_D = 3.5
MOUTH_CHAMFER = 0.8
HEIGHT = END_T + POINT_POCKET_H + BORE_DEPTH


def build() -> Part:
    body = Cylinder(OD / 2, HEIGHT, align=ON_BED)
    body = fillet(body.edges().group_by(Axis.Z)[-1], 0.8)
    body = chamfer(body.edges().group_by(Axis.Z)[0], 0.4)
    z0 = END_T + POINT_POCKET_H
    body -= Pos(0, 0, z0) * Cone(BORE_BOT_D / 2, BORE_TOP_D / 2, BORE_DEPTH + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # 45° lead-in at the mouth
    body -= Pos(0, 0, HEIGHT - MOUTH_CHAMFER) * Cone(BORE_TOP_D / 2, BORE_TOP_D / 2 + MOUTH_CHAMFER + 0.01, MOUTH_CHAMFER + 0.01,
                                                    align=(Align.CENTER, Align.CENTER, Align.MIN))
    body -= Pos(0, 0, END_T) * Cone(0.4, BORE_BOT_D / 2, POINT_POCKET_H + 0.02, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body -= Pos(0, 0, END_T / 2) * teardrop_hole(LANYARD_D, OD + 2, along="Y")
    return body
