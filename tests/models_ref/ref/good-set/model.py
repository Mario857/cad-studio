"""Reference: two parts printed together, 5 mm apart (mesh OK with 2 bodies, fit OK)."""
from build123d import *
from cadlib import *

META = dict(material="PLA", quality="standard")


def build():
    return [rounded_box(30, 30, 15, radius=2), Pos(35, 0, 0) * rounded_box(30, 30, 15, radius=2)]
