"""paper-towel-holder: under-cabinet paper towel holder for a 280 mm roll.

Spec: two identical arm brackets screw to the underside of a wall cabinet, 298 mm
apart outside (286 mm clear between arms). Each arm is one constant YZ profile (12 mm
thick): a flange (2 screw holes, 45 deg gussets) and an arm with a slot that runs
forward and 30 deg up to a round seat; the octagonal hollow spindle's stubs drop into
the seats, so a new roll is swapped by lifting the spindle out.
Print set (one plate): 2 brackets + 1 spindle. Bracket coordinates are in-use
(cabinet underside at z = TOP, roll axis along X at y=0, z=AXIS_Z); the second
bracket and the spindle are laid out beside it so that print_orientation (0,90,0)
puts every part flat on the bed: brackets lie on their side (arm bending runs along
the layers), spindle lies along the bed (octagon, flat face down, diamond core: all
faces <= 45 deg). The 3 separate bodies are intended.
Assumptions: roll 280 mm long, up to Ø150 mm, core Ø >= 38 mm, ~700 g; #8 / 4 mm
wood screws (Ø4.5 holes); bed axis >= 296 mm for the spindle.
"""

import math

from build123d import *

from cadlib import *

# Parameters
ROLL_L = 280.0
ROLL_D = 150.0
END_PLAY = 3.0            # per side
ARM_T = 12.0              # bracket thickness along X
ARM_W = 30.0              # arm width along Y
TOP_GAP = 7.0             # roll to cabinet
AXIS_Z = 18.0             # roll axis above the arm bottom
FLANGE_T = 6.0
FLANGE_BACK = 45.0        # flange reach behind / in front of the axis
FLANGE_FRONT = 45.0
GUSSET = 15.0
SCREW_D = 4.5
SCREW_IN = 10.0           # hole centre from flange tip
STUB_D = 12.0
STUB_L = 6.0
SLOT_CLR = 0.6
SLOT_ANGLE = 30.0
SPINDLE_D = 28.0          # octagon across flats
SPINDLE_WALL = 4.0
VENT_D = 4.0
ROLL_G = 700

TOP = AXIS_Z + ROLL_D / 2 + TOP_GAP
GAP = ROLL_L + 2 * END_PLAY
SPINDLE_L = GAP - 2 * 0.5

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[dict(at=(0, 0, AXIS_Z), grams=ROLL_G / 2)],   # per bracket
    print_orientation=(0, 90, 0),
    supports="off",   # only overhangs: underside of the 6 mm long spindle stubs and the Ø4
                      # vent bore (0.9 cm2 total) -- short cantilevers that print clean
    brim="on",
)


def bracket_profile() -> Sketch:
    h = ARM_W / 2
    outline = Polygon(
        (-h, AXIS_Z), (h, AXIS_Z), (h, TOP - FLANGE_T - GUSSET), (h + GUSSET, TOP - FLANGE_T),
        (FLANGE_FRONT, TOP - FLANGE_T), (FLANGE_FRONT, TOP), (-FLANGE_BACK, TOP),
        (-FLANGE_BACK, TOP - FLANGE_T), (-h - GUSSET, TOP - FLANGE_T), (-h, TOP - FLANGE_T - GUSSET),
        align=None)
    outline += Pos(0, AXIS_Z) * Circle(h)
    w = STUB_D + SLOT_CLR
    a = math.radians(SLOT_ANGLE)
    slot_len = 2 * ARM_W
    slot2d = (Pos(0, AXIS_Z) * Circle(w / 2)
              + Pos(0, AXIS_Z) * Rot(0, 0, SLOT_ANGLE) * Pos(slot_len / 2, 0) * Rectangle(slot_len, w))
    return outline - slot2d


def bracket() -> Part:
    b = extrude(Plane.YZ * bracket_profile(), ARM_T / 2, both=True)
    for y in (-FLANGE_BACK + SCREW_IN, FLANGE_FRONT - SCREW_IN):
        # vertical (in use) screw hole; teardrop tip toward -X = up when printed
        b -= Pos(0, y, TOP - FLANGE_T / 2) * Rot(0, -90, 0) * teardrop_hole(SCREW_D, FLANGE_T + 2, along="X")
    return b


def spindle() -> Part:
    """Modeled along Z so the (0,90,0) print rotation lays it flat."""
    oct_r = SPINDLE_D / 2 / math.cos(math.radians(22.5))
    body = extrude(Rot(0, 0, 22.5) * RegularPolygon(oct_r, 8), SPINDLE_L)
    stub_r = STUB_D / 2 / math.cos(math.radians(22.5))
    stub = extrude(Rot(0, 0, 22.5) * RegularPolygon(stub_r, 8), STUB_L)
    s = body + Pos(0, 0, -STUB_L) * stub + Pos(0, 0, SPINDLE_L) * stub
    # diamond core (45 deg faces when lying flat) closed by 10 mm end plugs
    core = Pos(0, 0, 10) * extrude(RegularPolygon(SPINDLE_D / 2 - SPINDLE_WALL, 4), SPINDLE_L - 20)
    s -= core
    # vent bore through stubs into the core so it is not a sealed void
    s -= Pos(0, 0, -STUB_L - 1) * Cylinder(VENT_D / 2, 12 + STUB_L, align=ON_BED)
    return s


def build():
    b1 = bracket()
    b2 = Pos(0, 0, -TOP - 15) * b1          # second (identical) bracket, beside the first
    sp = Pos(ARM_T / 2 - SPINDLE_D / 2, 2 * FLANGE_FRONT + 25, -TOP - 15 - 40) * spindle()
    return [b1, b2, sp]
