"""Reference: known-bad, wide flat slab on a thin pillar, orientation pinned, supports off."""
from build123d import *
from cadlib import *

META = dict(material="PLA", quality="standard", print_orientation=(0, 0, 0), supports="off")


def build():
    pillar = Cylinder(4, 20, align=ON_BED)
    slab = Pos(0, 0, 20) * Box(60, 60, 3, align=ON_BED)
    return pillar + slab
