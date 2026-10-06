"""mason-jar-trap-lid: push-on lid for a wide-mouth mason jar with a 45 deg one-way funnel.

Spec: skirt pushes over the jar rim/thread; a 30 mm mouth funnel (45 deg walls) hangs into the
jar so bugs walk/fall in through the 6 mm exit and cannot find the way back. A 14 mm side port
is closed by a separate flanged plug (printed beside the lid) for emptying.
Assumptions: jar outer thread diameter 95 mm (86 mm opening); retention = push-on rim lip
(friction, no band/ring) with 0.25 mm radial clearance (skirt ID 95.5 mm); plug fit 0.25 mm per side.
Printed top-down (plate on bed, skirt/funnel up), zero supports.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(180, 0, 0),
    supports="off",
    brim="off",
)

JAR_OD = 95.0
CLEAR = 0.25
SKIRT_T = 2.4
SKIRT_H = 12.0
PLATE_T = 3.0
FUNNEL_MOUTH = 30.0
FUNNEL_EXIT = 6.0
FUNNEL_WALL = 2.0
PORT_D = 14.0
PORT_X = 31.0
PLUG_FLANGE_D = 18.0
PLUG_FLANGE_T = 1.5
PLUG_LEN = 2.5

SKIRT_ID = JAR_OD + 2 * CLEAR
SKIRT_R_OUT = SKIRT_ID / 2 + SKIRT_T
Z_PLATE = SKIRT_H            # plate underside
Z_TOP = SKIRT_H + PLATE_T
FUN_H = (FUNNEL_MOUTH - FUNNEL_EXIT) / 2   # 45 deg


def build():
    lid = Cylinder(SKIRT_R_OUT, Z_TOP, align=ON_BED)
    lid = chamfer(lid.edges().group_by(Axis.Z)[-1], 0.4)
    lid -= Cylinder(SKIRT_ID / 2, SKIRT_H, align=ON_BED)
    # funnel: outer cone hanging from plate underside, tip at z = Z_PLATE - FUN_H
    zt = Z_PLATE - FUN_H
    outer = Pos(0, 0, zt) * Cone(FUNNEL_EXIT / 2 + FUNNEL_WALL, FUNNEL_MOUTH / 2 + FUNNEL_WALL, FUN_H, align=ON_BED)
    lid += outer
    inner = Pos(0, 0, zt - 0.01) * Cone(FUNNEL_EXIT / 2, FUNNEL_MOUTH / 2, FUN_H + 0.02, align=ON_BED)
    lid -= inner
    lid -= Pos(0, 0, Z_PLATE - 0.5) * Cylinder(FUNNEL_MOUTH / 2, PLATE_T + 1, align=ON_BED)
    # side port (plug flange sits on top of the plate)
    hole = hole_d(PORT_D)
    lid -= Pos(PORT_X, 0, Z_PLATE - 0.5) * Cylinder(hole / 2, PLATE_T + 1, align=ON_BED)
    # plug beside lid, in-use orientation (flange up); flipped with the lid for printing
    plug = Cylinder(PORT_D / 2, PLUG_LEN + 0.01, align=ON_BED)
    plug += Pos(0, 0, PLUG_LEN) * Cylinder(PLUG_FLANGE_D / 2, PLUG_FLANGE_T, align=ON_BED)
    plug = Pos(-(SKIRT_R_OUT + 14), 0, Z_TOP - PLUG_LEN - PLUG_FLANGE_T) * plug
    return [lid, plug]
