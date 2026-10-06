"""door-wall-bumper: wall-mounted dome bumper that stops a door handle hitting the wall.

Spec: Ø60 mm dome, 20 mm proud of the wall. Hollow inside with an A-frame (45°) annular cavity
crossed by radial ribs = crush zone that absorbs the handle impact. Screw version: one
countersunk M4 wood screw through a central column, head hidden under a press-fit cap that is
flush with the dome. Adhesive version: same dome with a closed flat back for a Ø60 adhesive pad.
build() returns [screw bumper, cap, adhesive bumper], laid out side by side (3 bodies: intended).

Model coordinates: wall = z=0 plane (back on the bed), dome points +Z (away from the wall).

ASSUMPTIONS:
- Screw: M4 countersunk (e.g. 4x30 wood screw into a wall plug); head Ø8 sinks below the cap.
- Cap press fit uses FIT["press"] diametral interference-free gap (0.10 mm); a dab of glue
  makes it permanent. A 1 mm pry notch lets you pop it off with a small screwdriver.
- Back of the screw version is open (ring + column touch the wall); adhesive version has a
  2 mm solid back so the full Ø60 face carries the pad; its ribs stop 3 mm short of the
  central pillar so the cavity is one void, vented by a Ø2 hole in the back (under the pad).
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation="auto",  # back (wall side) flat on the bed is the natural orientation
    supports="auto",
    brim="auto",
)

# Parameters
DOME_D = 60.0          # outer diameter
SKIRT_H = 3.0          # vertical cylindrical skirt at the wall
DOME_H = 20.0          # total height from wall
SCREW = "M4"
COL_R = 8.5            # central screw column radius
CAP_RECESS_D = 12.0    # recess over the screw head
CAP_RECESS_DEPTH = 5.0 # depth at the centre (from dome apex)
CAP_FIT = FIT["press"]
PRY_W = 1.0            # pry notch width (in the recess wall)
CAV_OUT_R = 27.0       # cavity outer radius at the wall (outer skirt wall = 3 mm)
CAV_Z1 = 3.0           # cavity vertical part before the 45° roof
RIB_N = 8
RIB_T = 1.6
ADH_BACK_T = 2.0       # closed back thickness for the adhesive version
ADH_RIB_GAP = 3.0      # adhesive version: ribs stop short of the pillar -> one connected void
ADH_VENT_D = 2.0       # vent so the void is not sealed (pad covers it)
GAP = 12.0             # layout spacing between printed parts
CHAMFER = 0.4
APEX_FLAT_R = 1.0      # tiny flat at the apex (avoids a degenerate mesh pole)

R_OUT = DOME_D / 2
CAP_H = DOME_H - SKIRT_H
SPHERE_R = (R_OUT**2 + CAP_H**2) / (2 * CAP_H)
SPHERE_Z = DOME_H - SPHERE_R


def dome_profile(r: float, z0: float) -> Part:
    """Revolved solid: radius r cylinder from z0 up to the dome sphere, 0.4 bottom chamfer."""
    zt = apex_z(r)
    ztop = apex_z(APEX_FLAT_R)
    a = (math.atan2(zt - SPHERE_Z, r) + math.atan2(ztop - SPHERE_Z, APEX_FLAT_R)) / 2
    mid = (SPHERE_R * math.cos(a), SPHERE_Z + SPHERE_R * math.sin(a))
    face = make_face([
        Line((0, z0), (r - CHAMFER, z0)),
        Line((r - CHAMFER, z0), (r, z0 + CHAMFER)),
        Line((r, z0 + CHAMFER), (r, zt)),
        ThreePointArc((r, zt), mid, (APEX_FLAT_R, ztop)),
        Line((APEX_FLAT_R, ztop), (0, ztop)),
        Line((0, ztop), (0, z0)),
    ])
    return revolve(Plane.XZ * face, Axis.Z, 360)


def dome() -> Part:
    return dome_profile(R_OUT, 0)


def cavity(z0: float, rib_gap: float = 0.0) -> Part:
    """Annular A-frame cavity (45° roof both sides) minus radial ribs."""
    r_in, r_out = COL_R, CAV_OUT_R
    r_mid = (r_in + r_out) / 2
    half = (r_out - r_in) / 2
    prof = Polygon(
        (r_in, z0), (r_out, z0), (r_out, CAV_Z1), (r_mid, CAV_Z1 + half), (r_in, CAV_Z1),
        align=None,
    )
    cav = revolve(Plane.XZ * prof, Axis.Z, 360)
    for i in range(RIB_N):
        cav -= Rot(0, 0, i * 360 / RIB_N) * Pos(r_in + rib_gap if rib_gap else r_in - 1, 0, 0) * Box(
            R_OUT, RIB_T, 2 * DOME_H, align=(Align.MIN, Align.CENTER, Align.CENTER)
        )
    return cav


def apex_z(r: float) -> float:
    return SPHERE_Z + math.sqrt(SPHERE_R**2 - r**2)


def screw_bumper() -> Part:
    floor_z = DOME_H - CAP_RECESS_DEPTH
    part = dome() - cavity(0)
    part -= Pos(0, 0, DOME_H + 1) * Cylinder(
        CAP_RECESS_D / 2, DOME_H + 1 - floor_z, align=(Align.CENTER, Align.CENTER, Align.MAX)
    )
    part -= Pos(CAP_RECESS_D / 2, 0, DOME_H + 1) * Box(
        3, PRY_W, DOME_H + 1 - floor_z + 1, align=(Align.CENTER, Align.CENTER, Align.MAX)
    )
    part -= Pos(0, 0, floor_z) * bolt_hole(SCREW, floor_z + 1, head="csk")
    return part


def cap() -> Part:
    floor_z = DOME_H - CAP_RECESS_DEPTH
    d = CAP_RECESS_D - CAP_FIT
    return Pos(0, 0, -floor_z) * dome_profile(d / 2, floor_z)


def adhesive_bumper() -> Part:
    part = dome() - cavity(ADH_BACK_T, ADH_RIB_GAP)
    # vent through the back into the (now single, connected) cavity
    part -= Pos(COL_R + ADH_RIB_GAP / 2, 0, ADH_BACK_T + 0.5) * Cylinder(
        ADH_VENT_D / 2, ADH_BACK_T + 1, align=(Align.CENTER, Align.CENTER, Align.MAX)
    )
    return part


def build():
    step = DOME_D + GAP
    return [
        screw_bumper(),
        Pos(-(R_OUT + GAP + CAP_RECESS_D / 2), 0, 0) * cap(),
        Pos(step, 0, 0) * adhesive_bumper(),
    ]
