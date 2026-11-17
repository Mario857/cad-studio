"""Reference: one part with a detached crumb next to it (a feature that never got unioned)."""
from build123d import *
from cadlib import *

META = dict(material="PLA", quality="standard")


def build():
    return rounded_box(30, 30, 15, radius=2) + Pos(25, 0, 0) * Box(3, 3, 3, align=ON_BED)
