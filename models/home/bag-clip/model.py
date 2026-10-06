"""bag-clip: slide-on spring clip that seals a folded snack/chip bag, ~100 mm jaw.

Spec: one-piece "U" spring clip, no hinge and no pin. Two stiff 3.2 mm arms joined by a
round U-bend; the arms converge to a 0.4 mm pre-load gap at the tip and flare out into a
lead-in so the folded bag top (roll it 2-3 times) slides in from the open end. The U-bend
and arms flex in the XY plane, which is also the print plane (profile lies flat on the bed,
12 mm extrusion in Z), so every layer carries the bending - no Z-layer weakness.
Jaw (usable clamping length) = JAW_LENGTH = 100 mm; overall ~118 x 13 x 12 mm.
Inner face has low grip ridges to stop the bag sliding out.

Assumptions: chip bags up to ~140 mm wide get folded/rolled to <= 3 mm thick bundle;
ABS+ arms open ~3 mm at the tip without yielding (root gap 6 mm gives a long lever).
"""

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm. The audit picks the print orientation.
META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # profile flat on bed: flex happens within layers
    supports="off",
    brim="auto",
)

# Parameters
JAW_LENGTH = 100.0    # clamping length of the arms
ARM_T = 3.2           # arm thickness (in-plane, the flexing dimension)
HEIGHT = 12.0         # extrusion height (clip width along the bag)
ROOT_GAP = 6.0        # gap between arms at the U-bend (half of it each side)
TIP_GAP = 0.4         # pre-load gap at the jaw tip
FLARE_LEN = 9.0       # lead-in flare length beyond the jaw
FLARE_OPEN = 3.5      # extra opening per side at the flare end
RIDGE_PITCH = 10.0    # grip ridges along the inner face
RIDGE_D = 1.2         # ridge diameter (half sticks out)
EDGE_CHAMFER = 0.4    # elephant-foot / edge break


def _arm() -> Face:
    """Upper arm (y > 0) incl. lead-in flare, as a 2D face."""
    g0, gt = ROOT_GAP / 2, TIP_GAP / 2
    L = JAW_LENGTH
    arm = Polygon((0, g0), (L, gt), (L, gt + ARM_T), (0, g0 + ARM_T), align=None)
    flare = Polygon(
        (L - 1, gt), (L + FLARE_LEN, gt + FLARE_OPEN),
        (L + FLARE_LEN, gt + FLARE_OPEN + ARM_T), (L - 1, gt + ARM_T), align=None,
    )
    return arm + flare


def build() -> Part:
    g0 = ROOT_GAP / 2
    upper = _arm()
    profile = upper + mirror(upper, about=Plane.XZ)
    # U-bend: half annulus on the x < 0 side
    ring = Circle(g0 + ARM_T) - Circle(g0)
    ring = ring - Pos(g0 + ARM_T, 0) * Rectangle(2 * (g0 + ARM_T), 2 * (g0 + ARM_T) + 2)
    profile = profile + ring
    part = extrude(Plane.XY * profile, HEIGHT)

    # grip ridges: vertical half-cylinders on the inner faces, stopping short of the tip
    n = int((JAW_LENGTH - 15) // RIDGE_PITCH)
    for i in range(1, n + 1):
        x = i * RIDGE_PITCH
        y = g0 - (g0 - TIP_GAP / 2) * x / JAW_LENGTH
        for s in (1, -1):
            part += Pos(x, s * y, 0) * Cylinder(RIDGE_D / 2, HEIGHT, align=ON_BED)

    try:
        part = chamfer(part.edges().group_by(Axis.Z)[0], EDGE_CHAMFER)
    except Exception:
        pass
    return part
