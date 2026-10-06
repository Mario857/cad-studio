"""towel-hook-double: wall robe/towel hook with two prongs (short upper, long lower).

Spec: one constant YZ profile extruded 25 mm wide: back plate, lower J-prong reaching
55 mm from the wall and an upper J-prong reaching 30 mm, both with up-turned tips and
filleted corners. Printed lying on its side (print_orientation (0,90,0)) so the whole
profile is in the layer plane: zero overhangs and prong bending runs along layers.
2 x 4.5 mm teardrop screw holes, below the lower prong and above the upper one,
with straight screwdriver access.
Assumptions: wet bath towel / robe <= 2 kg per prong; 4 mm pan-head screws + plugs.
"""

from build123d import *

from cadlib import *

# Parameters
WIDTH = 25.0
PLATE_T = 6.0
PLATE_H = 100.0
T = 10.0                 # prong thickness
LOW_Z, LOW_D, LOW_TIP = 20.0, 55.0, 32.0     # bottom of arm, reach, tip height
UP_Z, UP_D, UP_TIP = 58.0, 32.0, 22.0
FILLET_R = 3.0
SCREW_D = 4.5
SCREW_Z = (9.0, PLATE_H - 9.0)
LOAD_G = 2000

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[dict(at=(0, LOW_D - T, LOW_Z + T), grams=LOAD_G),
           dict(at=(0, UP_D - T, UP_Z + T), grams=LOAD_G)],
    print_orientation=(0, 90, 0),
    supports="auto",
    brim="on",              # ABS: thin profile, small contact area per feature
)


def prong(z, d, tip) -> Sketch:
    arm = Pos(d / 2, z + T / 2) * Rectangle(d, T)
    up = Pos(d - T / 2, z + tip / 2) * Rectangle(T, tip)
    return arm + up


def profile() -> Sketch:
    s = Pos(PLATE_T / 2, PLATE_H / 2) * Rectangle(PLATE_T, PLATE_H)
    s += prong(LOW_Z, LOW_D, LOW_TIP)
    s += prong(UP_Z, UP_D, UP_TIP)
    return fillet(s.vertices(), FILLET_R)


def build() -> Part:
    part = extrude(Plane.YZ * profile(), WIDTH / 2, both=True)
    for z in SCREW_Z:
        # tip toward -X = up in the print orientation
        part -= Pos(0, PLATE_T / 2, z) * Rot(0, -90, 0) * teardrop_hole(SCREW_D, PLATE_T + 2, along="Y")
    return part
