"""stink-bug-tongs: spring tongs that cup a stink bug without crushing it, to carry it outside.

Spec: 180 mm one-piece spring tongs (ABS+ flexes like tweezers). Each tip has a 15 mm round
cup (blind pocket, 3 mm floor) so the bug is held, not squeezed (crushing makes it stink).
Arms 3.2 mm thick x 14 mm tall, 3.5 deg open angle -> ~28 mm tip opening. Printed flat.
Assumptions: ABS+ (AzureFilm), adult bug ~14-17 mm long, grip with thumb and index finger,
arm thickness may need +-0.4 mm tuning for spring feel.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),
    supports="off",
    brim="auto",
)

# Parameters
LENGTH = 170.0
ARM_T = 3.2
HEIGHT = 14.0
OPEN_DEG = 3.5
ROOT_GAP = 1.0         # half gap between arm inner faces at the root
PAD_W = 8.8            # pad bulges outward from the inner face (cup centre sits on the face)
PAD_L = 28.0
CUP_D = 15.0
CUP_FLOOR = 3.0
ROOT_L = 12.0


def arm() -> Part:
    """Right arm: inner face at x=0, root at y=0, tip at y=LENGTH."""
    body = Box(ARM_T, LENGTH, HEIGHT, align=(Align.MIN, Align.MIN, Align.MIN))
    pad = Pos(0, LENGTH - PAD_L, 0) * Box(PAD_W, PAD_L, HEIGHT, align=(Align.MIN, Align.MIN, Align.MIN))
    cup = Pos(0, LENGTH - PAD_L / 2, CUP_FLOOR) * Cylinder(CUP_D / 2, HEIGHT, align=ON_BED)
    return (body + pad) - cup


def build() -> Part:
    right = Pos(ROOT_GAP, 0, 0) * Rot(0, 0, -OPEN_DEG) * arm()
    left = mirror(right, about=Plane.YZ)
    root = Pos(0, -ROOT_L / 2 + 3, 0) * Box(2 * (ROOT_GAP + ARM_T) + 6, ROOT_L, HEIGHT, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return root + right + left
