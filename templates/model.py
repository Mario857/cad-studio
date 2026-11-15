"""{{NAME}}: one-line description.

Spec: what it is for, key dimensions, what it mates with.
Dimensions: tag each MEASURED (given by user / a standard) or UNVERIFIED (guessed, from photo/memory).
  e.g.  rod diameter 19.0  MEASURED;  frame lip 4.5  UNVERIFIED
Assumptions: anything guessed (state it so it can be corrected).
Risks: what breaks first in real use, and how the user will find out (e.g. "snap arm may crack at the root").
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
    # Multi-part fits (build() returns a list): assembly=True means the parts are in USE positions
    # -> FAIL on overlaps > 0.5 mm3. mates WARN if the min gap leaves the band (indices into the list).
    # assembly=False,
    # mates=[dict(a=0, b=1, clearance=(0.2, 0.6))],
)

# Parameters
WIDTH = 40.0
DEPTH = 30.0
HEIGHT = 10.0


def build() -> Part:
    part = rounded_box(WIDTH, DEPTH, HEIGHT, radius=3)
    return part
