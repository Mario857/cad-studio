"""floating-bedside-shelf: wall-mounted shelf replacing a nightstand.

Spec: 200 mm wide (X) x 150 mm deep (Y) shelf. Wall face at y=0, shelf front at y=-150.
Constant cross-section (YZ profile) extruded along X: back wall plate, top plate, front lip
and a full-width diagonal web underneath. Two diamond windows in the web turn it into a truss of
gussets and give screwdriver access to the two hidden countersunk wall screws (heads sit inside
the closed box, only visible looking up through the windows). A 25 mm cable hole at the back runs
straight down through the top plate and the web, for a charger cable from an outlet below.
Load: 3 kg at the front edge.

Strength orientation: printed on its side (+X up, end face on the bed). Every layer is a full YZ
cross-section, so all bending stresses from the front load (top plate tension, web compression,
back plate) run inside layers, never across them. The profile is prismatic, so it prints
without supports; horizontal (in print) holes are teardrops pointing up (+X).

Assumptions:
- Wall screws: 2x 4 mm countersunk (90 deg) wood/chipboard screws, >= 40 mm long, with suitable
  wall anchors (e.g. 6 mm plugs in masonry, or metal hollow-wall anchors in drywall).
- Shelf top surface 70 mm above the bottom of the back plate; mounting height is up to the user.
- Front lip 12 mm tall stops a phone / glasses from sliding off; lip is 4 mm thick.
- ABS: brim forced on - the part stands 200 mm tall on a ~14 cm2 end face; print enclosed.
"""

import math

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm. The audit picks the print orientation.
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,            # wall mounted
    loads=[dict(at=(0, -148, 72), grams=3000)],  # 3 kg at the front edge
    print_orientation=(0, -90, 0),  # on its side, +X up: load runs along layers
    supports="off",
    brim="on",                 # tall (200 mm) side-standing ABS print, small footprint
)

# Parameters
WIDTH = 200.0          # X, along the wall
DEPTH = 150.0          # Y, wall to front face of lip
HEIGHT = 70.0          # bottom of back plate to top surface of shelf
TOP_T = 5.0            # top plate thickness
BACK_T = 6.0           # back (wall) plate thickness
LIP_H = 12.0           # front lip height above shelf top
LIP_T = 4.0            # front lip thickness
WEB_T = 4.0            # diagonal web (gusset) thickness, measured normal to web
WEB_REACH = 100.0      # web meets top plate this far from the wall

WINDOW_X = 55.0        # windows / screws at x = +-WINDOW_X
WINDOW_L = 50.0        # window length along the web slope
WINDOW_W = 50.0        # window width along X (pointed 45 deg ends for printing)

CABLE_D = 25.0         # cable hole diameter
CABLE_Y = -24.0        # cable hole centre (from wall)

SCREW_D = 4.0                          # wood screw nominal
SCREW_HOLE_D = clearance(SCREW_D, "loose")
SCREW_HEAD_D = 8.4                     # countersunk head diameter
SCREW_HEAD_SINK = 0.6                  # head sits this far below the plate face
SCREW_Z = HEIGHT / 2 - TOP_T / 2       # screw height on back plate (aligned with window)

BED_CHAMFER = 0.4


def _web_profile():
    """Diagonal web polygon in (y, z): from foot of back plate to under the top plate."""
    p0 = (-BACK_T, 0.0)
    p1 = (-WEB_REACH, HEIGHT - TOP_T)
    dy, dz = p1[0] - p0[0], p1[1] - p0[1]
    ln = math.hypot(dy, dz)
    # web thickness extends up/back (into the cavity side is fine either way)
    a = WEB_T * ln / abs(dy)      # vertical attach length on back plate
    b = WEB_T * ln / abs(dz)      # horizontal attach length under top plate
    return [p0, (p1[0] - b, p1[1]), p1, (p0[0], p0[1] + a)], (p0, p1)


def _teardrop_sketch(d):
    """Teardrop in local (u, v), point toward +u."""
    r = d / 2
    s = r / math.sqrt(2)
    return Circle(r) + Polygon((0, -s), (s, -s), (r * math.sqrt(2), 0), (s, s), (0, s), align=None)


def build() -> Part:
    x0 = -WIDTH / 2
    prof = Plane.YZ.offset(x0)  # local x = +Y, local y = +Z, extrudes along +X

    back = Polygon((-BACK_T, 0), (0, 0), (0, HEIGHT), (-BACK_T, HEIGHT), align=None)
    top = Polygon((-DEPTH, HEIGHT - TOP_T), (0, HEIGHT - TOP_T), (0, HEIGHT), (-DEPTH, HEIGHT),
                  align=None)
    lip = Polygon((-DEPTH, HEIGHT), (-DEPTH + LIP_T, HEIGHT), (-DEPTH + LIP_T, HEIGHT + LIP_H),
                  (-DEPTH, HEIGHT + LIP_H), align=None)
    web_pts, (p0, p1) = _web_profile()
    web = Polygon(*reversed(web_pts), align=None)  # CCW so it extrudes +X
    part = extrude(prof * back, WIDTH)
    for sk in (top, lip, web):
        part += extrude(prof * sk, WIDTH)

    # elephant-foot chamfer on the bed face (x = -WIDTH/2 in print)
    try:
        part = chamfer(part.edges().group_by(Axis.X)[0], BED_CHAMFER)
    except Exception:
        pass

    # web direction / normal (in YZ)
    dy, dz = p1[0] - p0[0], p1[1] - p0[1]
    ln = math.hypot(dy, dz)
    uy, uz = dy / ln, dz / ln
    mid = (p0[0] + uy * ln / 2, p0[1] + uz * ln / 2)
    ang = math.degrees(math.atan2(uz, uy))  # slope angle of web in YZ

    # diamond windows: local u along X (print up -> pointed ends), v along web slope
    hw, hl = WINDOW_W / 2, WINDOW_L / 2
    diamond = Polygon((hw, 0), (hw - hl, hl), (-hw + hl, hl), (-hw, 0), (-hw + hl, -hl),
                      (hw - hl, -hl), align=None) if hw > hl else \
        Polygon((hw, 0), (0, hl), (-hw, 0), (0, -hl), align=None)
    for sx in (-WINDOW_X, WINDOW_X):
        # plane origin at web middle, x dir = +X, y dir = along web slope
        pl = Plane(origin=(sx, mid[0], mid[1]), x_dir=(1, 0, 0), z_dir=(0, -uz, uy))
        cut = extrude(pl * diamond, 30, both=True)
        part -= cut

    # cable chase: vertical through top plate and web, teardrop pointing +X (print up)
    cable = extrude(Plane.XY.offset(-5) * Pos(0, CABLE_Y) * _teardrop_sketch(CABLE_D),
                    HEIGHT + 10)
    part -= cable

    # hidden wall screws: horizontal along Y through back plate, countersink on cavity side
    head_h = (SCREW_HEAD_D - SCREW_HOLE_D) / 2
    for sx in (-WINDOW_X, WINDOW_X):
        shank = extrude(Plane(origin=(sx, 1, SCREW_Z), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
                        * _teardrop_sketch(SCREW_HOLE_D), BACK_T + 2)
        csk = Pos(sx, -BACK_T + head_h + SCREW_HEAD_SINK, SCREW_Z) * Rot(90, 0, 0) * Cone(
            SCREW_HOLE_D / 2, SCREW_HEAD_D / 2, head_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
        recess = Pos(sx, -BACK_T + SCREW_HEAD_SINK, SCREW_Z) * Rot(90, 0, 0) * Cylinder(
            SCREW_HEAD_D / 2, 5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        part -= shank + csk + recess
    return part
