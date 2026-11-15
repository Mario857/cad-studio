"""Reference: known-good solid box, prints with no supports."""
from build123d import *
from cadlib import *

META = dict(material="PLA", quality="standard")


def build():
    return rounded_box(30, 30, 15, radius=2)
