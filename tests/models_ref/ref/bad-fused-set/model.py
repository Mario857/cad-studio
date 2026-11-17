"""Reference: two parts printed together only 0.05 mm apart -> they come off the bed as one lump."""
from build123d import *
from cadlib import *

META = dict(material="PLA", quality="standard")


def build():
    return [Box(30, 30, 15, align=ON_BED), Pos(30.05, 0, 0) * Box(30, 30, 15, align=ON_BED)]
