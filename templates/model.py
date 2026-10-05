"""{{NAME}}: one-line description.

Spec: what it is for, key dimensions, what it mates with.
Assumptions: anything guessed (state it so it can be corrected).
"""

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm. The audit picks the print orientation.
META = dict(
    material="PLA",            # see config/printer.toml [materials]
    quality="standard",        # draft | standard | strong | fine
    standing=False,            # True if it must stand on its own in use (tip-over audit)
    loads=[],                  # extra masses in use: [dict(at=(x, y, z), grams=200)]
    print_orientation="auto",  # or (rx, ry, rz) degrees applied to the model before printing
    supports="auto",           # auto | on | off
    brim="auto",               # auto | on | off
)

# Parameters
WIDTH = 40.0
DEPTH = 30.0
HEIGHT = 10.0


def build() -> Part:
    part = rounded_box(WIDTH, DEPTH, HEIGHT, radius=3)
    return part
