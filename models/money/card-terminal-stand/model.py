"""card-terminal-stand: counter stand holding a mobile card terminal at 30 deg, with cable path.

Spec: cradle plate tilted TILT (30 deg from the counter) with side rails and two bottom ledges
the terminal's bottom edge rests on. The ledges leave a PLUG_GAP (40 mm) gap in the middle so a
USB-C plug in the terminal's bottom edge fits; the plug and cable hang free below the raised front
(FRONT_H 35 mm above the counter), then run back under the stand through a
12x12 mm pointed-roof tunnel along the counter. A solid wedge carries the cradle (zero-support print). Terminal top 30 mm overhangs the
plate (easy to lift out).

MEASURE BEFORE PRINTING: terminal footprint DEV_W x DEV_L x DEV_T (default 70 x 120 x 20 mm),
position of its charging port (assumed centred on the bottom short edge).
Assumptions: terminal ~400 g; CLEAR 1 mm per side; customer key presses push into the plate.
"""

import math

from build123d import *

from cadlib import *

# Parameters
DEV_W = 70.0
DEV_L = 120.0
DEV_T = 20.0
CLEAR = 1.0              # per side
TILT = 30.0              # plate angle from the counter (deg)
PLATE_T = 4.0
PLATE_L = 90.0           # supported length of the terminal
RAIL_T = 3.0
RAIL_H = 10.0            # side rails above the plate
LEDGE_D = 14.0           # ledge depth at the plate (front is cut vertical -> 7 mm at its top)
LEDGE_H = 12.0           # above the plate
PLUG_GAP = 40.0          # gap between the ledges for the plug
FRONT_H = 35.0           # plate front edge above the counter (plug + cable bend room)
CABLE_SLOT_W = 12.0      # cable tunnel under the wedge 
CABLE_SLOT_H = 12.0      # peak of the 45 deg pointed tunnel roof

_C, _S = math.cos(math.radians(TILT)), math.sin(math.radians(TILT))


def _world(y, z):
    """Cradle-local (y along plate, z normal) -> world (Y, Z)."""
    return (y * _C - z * _S, y * _S + z * _C + FRONT_H)


META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=True,
    loads=[dict(at=(0, *_world(DEV_L / 2 - LEDGE_D, DEV_T / 2)), grams=400)],
    print_orientation=(0, 0, 0),
    supports="auto",
    brim="auto",
)


def build() -> Part:
    in_w = DEV_W + 2 * CLEAR
    out_w = in_w + 2 * RAIL_T
    y0 = -LEDGE_D

    # cradle in local coords: plate top at z=0, terminal bottom edge at y=0
    cr = Pos(0, (y0 + PLATE_L) / 2, -PLATE_T) * Box(out_w, PLATE_L - y0, PLATE_T + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for sx in (-1, 1):
        cr += Pos(sx * (in_w + RAIL_T) / 2, (y0 + PLATE_L) / 2, 0) * Box(RAIL_T, PLATE_L - y0, RAIL_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
        lw = (in_w - PLUG_GAP) / 2
        cr += Pos(sx * (PLUG_GAP / 2 + lw / 2), y0 / 2, 0) * Box(lw, LEDGE_D, LEDGE_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cr = fillet(cr.edges().group_by(Axis.Z)[-1], 1.0)
    part = Pos(0, 0, FRONT_H) * Rot(TILT, 0, 0) * cr

    # solid wedge under the plate (no overhangs) with a cable tunnel along the counter
    fy, fz = _world(y0, -PLATE_T / 2)
    by, bz = _world(PLATE_L, -PLATE_T)
    yc = _world(y0, 0)[0]                    # vertical front face (no down-facing faces)
    prof = Polygon((yc, 0), (by, 0), (by, bz), (fy, fz), (yc, fz), align=None)
    part += extrude(Plane.YZ * prof, out_w / 2, both=True)
    hw = CABLE_SLOT_W / 2
    tun = Polygon((-hw, 0), (hw, 0), (hw, CABLE_SLOT_H - hw), (0, CABLE_SLOT_H), (-hw, CABLE_SLOT_H - hw), align=None)
    part -= Pos(0, (fy + by) / 2, 0) * extrude(Plane.XZ * tun, (by - fy) / 2 + 1, both=True)
    part -= Pos(0, yc, 0) * Box(out_w + 2, 60, 200, align=(Align.CENTER, Align.MAX, Align.MIN))
    part = chamfer(part.edges().group_by(Axis.Z)[0], 0.4)
    return part
