"""Reference: known-bad, 0.4 mm walled open box (below the 0.6 mm fail limit)."""
from build123d import *
from cadlib import *

META = dict(material="PLA", quality="standard")


def build():
    outer = Box(30, 30, 20, align=ON_BED)
    inner = Pos(0, 0, 0.8) * Box(29.2, 29.2, 30, align=ON_BED)
    return outer - inner
