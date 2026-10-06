"""headphone-hook: under-desk headphone hanger, screwed to the underside of a desk.

Spec: J-shaped side profile, 30 mm wide. A 70 mm mounting plate goes under the desktop; a stem at the
back drops 50 mm and a flat arm comes forward to a raised lip near the desk edge. The headband
slides in from the front (31 mm opening) and rests on the arm, out of sight under the desk.
Two M4 countersunk wood screws go up through the plate; Ø10 access holes in the arm below each
screw let a screwdriver through.

Assumptions:
- Fits headbands up to ~38 mm thick (GAP below); load ~400 g.
- Desk front edge at x=0, plate top (z=HEIGHT) against the desk underside, hook opening faces -X.
- Printed on its side so the bending load runs along the layers.
"""

from build123d import *

from cadlib import *

META = dict(
    material="PLA",
    quality="strong",
    standing=False,
    loads=[dict(at=(35, 0, 6), grams=400)],  # headphones resting on the arm
    print_orientation=(90, 0, 0),  # on its side: J profile flat on the bed
    supports="off",  # remaining WARN (~0.8 cm2) = tops of the Ø4.5-10 screw/access holes, which bridge fine
    brim="auto",
)

# Parameters
WIDTH = 30.0       # along Y
DEPTH = 70.0       # plate length under the desk (X)
HEIGHT = 50.0      # total drop below the desk
PLATE = 6.0        # mounting plate thickness
STEM = 7.0         # back stem thickness
ARM = 6.0          # arm thickness
LIP = 14.0         # lip height above the bed of the arm (z)
LIP_X = 5.0        # lip front face, set back from the desk edge
LIP_T = 6.0        # lip thickness
ROUND = 2.5        # profile corner radius
EDGE = 1.0         # chamfer on the side-face edges
SCREW = "M4"
SCREW_X = (24.0, 50.0)
ACCESS_D = 10.0    # screwdriver access holes in the arm
GAP = HEIGHT - PLATE - ARM


def build() -> Part:
    profile = Polygon(
        (0, HEIGHT),
        (DEPTH, HEIGHT),
        (DEPTH, 0),
        (LIP_X, 0),
        (LIP_X, LIP),
        (LIP_X + LIP_T, LIP),
        (LIP_X + LIP_T, ARM),
        (DEPTH - STEM, ARM),
        (DEPTH - STEM, HEIGHT - PLATE),
        (0, HEIGHT - PLATE),
        align=None,
    )
    hook = extrude(Plane.XZ * profile, WIDTH / 2, both=True)
    hook = fillet(hook.edges().filter_by(Axis.Y), ROUND)
    try:
        # 45 deg chamfer, not a fillet: the -Y face sits on the bed when printed
        hook = chamfer(hook.edges().filter_by(Axis.Y, reverse=True), EDGE)
    except Exception:
        pass  # side-face edge break is cosmetic

    for x in SCREW_X:
        # countersunk head on the plate's underside, screw goes up into the desk
        hook -= at(x, 0, HEIGHT - PLATE, 180, 0, 0) * bolt_hole(SCREW, PLATE + 1, head="csk")
        hook -= Pos(x, 0, -1) * _teardrop_z(ACCESS_D, ARM + 2)
    return hook


def _teardrop_z(d: float, h: float) -> Part:
    """Vertical-in-use hole with its point toward +Y, which is 'up' when printed on its side."""
    r = d / 2
    k = r * 0.7071
    s = Circle(r) + Polygon((-k, k), (0, r * 1.4142), (k, k), (0, 0), align=None)
    return extrude(s, h)
