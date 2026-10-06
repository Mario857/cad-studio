"""bug-dustpan: mini dustpan + flick blade for moving a stink bug without touching it.

Spec: 90 mm wide pan (90 deep scoop, 2.4 mm floor, 12 mm back lip, 45 deg ramp on front edge)
and a flat 90 mm blade, 1.6 mm thick. Both share a 120 mm x 20 mm handle with a 6 mm hanging hole.
Nesting: blade lies on the pan floor, handles stacked; printed side by side flat.
Assumptions: no side walls (so the 90 mm blade nests flush); blade is thinner than the pan floor.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation="auto",
    supports="off",
    brim="auto",
)

WIDTH = 90.0
SCOOP = 90.0
FLOOR = 2.4
LIP_H = 12.0
LIP_T = 2.0
RAMP = FLOOR - 0.6      # 45 deg: run = rise
HANDLE_L = 120.0
HANDLE_W = 20.0
HANDLE_T = 4.0
HOLE_D = 6.0
BLADE_T = 1.6
GAP = 12.0


def handle(y0):
    h = Pos(0, y0 + HANDLE_L / 2, HANDLE_T / 2) * Box(HANDLE_W, HANDLE_L, HANDLE_T)
    h = h - Pos(0, y0 + HANDLE_L - 12, 0) * Cylinder(HOLE_D / 2, HANDLE_T * 3)
    return h


def pan():
    p = Pos(0, SCOOP / 2, FLOOR / 2) * Box(WIDTH, SCOOP, FLOOR)
    p = chamfer(p.edges().filter_by(Axis.X).group_by(Axis.Z)[-1].group_by(Axis.Y)[0], RAMP)
    p += Pos(0, SCOOP - LIP_T / 2, LIP_H / 2) * Box(WIDTH, LIP_T, LIP_H)
    p += Pos(0, SCOOP - 1, HANDLE_T / 2) * Box(HANDLE_W, 2, HANDLE_T)
    p += handle(SCOOP)
    return p


def blade():
    b = Pos(0, SCOOP / 2, BLADE_T / 2) * Box(WIDTH, SCOOP, BLADE_T)
    b = chamfer(b.edges().filter_by(Axis.X).group_by(Axis.Z)[-1].group_by(Axis.Y)[0], 0.8)
    b += Pos(0, SCOOP - 1, HANDLE_T / 2) * Box(HANDLE_W, 2, HANDLE_T)
    b += handle(SCOOP)
    return b


def build():
    return [pan(), Pos(WIDTH + GAP, 0, 0) * blade()]
