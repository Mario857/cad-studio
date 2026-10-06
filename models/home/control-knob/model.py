"""control-knob: numbered guitar volume/tone knob (set of 3), knurled press-fit or set-screw bore.

Spec: Ø19 x 18 mm "speed knob" style. Lower skirt Ø19 carries engraved 0-10 numbers and tick
marks (30° steps over a 300° arc, matching a standard pot's ~300° rotation; numbers increase
counter-clockwise seen from above, so turning the knob clockwise raises the number read at a
fixed reference). Upper grip Ø16 with 12 vertical flutes. VARIANT selects the bore:
  - "knurled":  18-tooth splined press-fit bore for a 6 mm split knurled shaft (CTS/Alpha style).
  - "setscrew": plain Ø6 slide-fit bore for a solid shaft + radial M3 grub screw through a
                captive M3 nut (nut slides into a slot from the underside; the felt washer
                covers the slot).
Underside (the face near the pickguard/top): outer edge filleted 1 mm, Ø15 x 0.8 mm recess for
a felt washer, and a Ø11 counterbore that clears the pot bushing tip.
FINISH NOTE: some rubbers/vinyls react with nitrocellulose finishes and leave marks - use a
felt (or cork) washer in the recess, never rubber.

Printed top-down (top face on the bed, print_orientation (180,0,0)): smooth top, the blind bore
end / nut slot / recesses all become floors (no supports), numbers are on a vertical wall.

Text size: Ø19 gives ~60 mm circumference; 11 numbers in 30° steps leave ~5 mm per step, so
the numbers use font size NUM_SIZE = 5 mm (the printable minimum; "10" is ~5.6 mm wide) and are
engraved TEXT_DEPTH 1.0 mm at the glyph centre (>= 0.6 mm at the glyph edges because the flat
text cut meets a curved wall). Tick marks above each number help where glyph detail blurs.

Assumptions: shaft 6.0 mm (metric pots; 1/4" solid shaft -> set SOLID_SHAFT_D = 6.35),
knurl major Ø6.0 with 18 teeth, ~0.3 mm tooth height, 0.10 mm diametral interference;
bushing tip <= Ø10.5 and protrudes <= 2 mm above the nut; felt washer Ø15 x ~1 mm.
Hardware (setscrew variant, per knob): 1x M3 hex nut, 1x M3x5/6 grub screw; any: Ø15 felt washer.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="fine",
    standing=False,
    loads=[],
    print_orientation=(180, 0, 0),  # top face on the bed: best top + clean bore/recess floors
    supports="off",
    brim="auto",
    copies=3,
)

# Parameters
VARIANT = "knurled"          # "knurled" | "setscrew"

KNOB_D = 19.0
KNOB_H = 18.0
SKIRT_H = 8.0                # Ø19 numbered skirt height
GRIP_D = 16.0                # upper grip diameter
TOP_CHAMFER = 0.6
BOTTOM_FILLET = 1.0          # guitar-facing edge

FLUTES = 12
FLUTE_R = 1.0
FLUTE_DEPTH = 0.6            # radial depth of each flute
FLUTE_Z0 = 11.5              # flutes start here (45° cone below)

# Underside
FELT_D = 15.0
FELT_DEPTH = 0.8
BUSHING_D = 11.0             # counterbore for pot bushing tip
BUSHING_DEPTH = 2.0          # below the felt recess

# Bore
BORE_DEPTH = 13.0            # from underside
KNURL_OD = 6.0
KNURL_TEETH = 18
KNURL_TOOTH_H = 0.3
KNURL_INTERFERENCE = 0.10    # diametral press-fit interference on the knurl major diameter
SOLID_SHAFT_D = 6.0
SOLID_FIT = "slide"

# Set screw (setscrew variant)
SCREW_D = 3.0               # M3 grub screw
SCREW_Z = 5.0                # axis height above underside
SCREW_ANGLE = 0.0            # deg, centred in the gap between "10" and "0"
NUT_AF = 5.5 + 0.3           # M3 nut across flats + clearance (tangential slot width)
NUT_T = 2.4 + 0.25           # M3 nut thickness + clearance (radial slot thickness)
NUT_WALL = 1.2               # wall between bore and nut slot

# Numbering
NUM_SIZE = 5.0
TEXT_DEPTH = 1.0
NUM_Z = 4.2                  # centre height of numbers
NUM_STEP = 30.0              # deg between numbers
NUM_START = 30.0             # angle of "0" (deg, CCW from +X)
TICK_W = 0.8
TICK_H = 1.4
TICK_Z = 7.0                 # tick centre height
TICK_DEPTH = 0.8


def _body() -> Part:
    r, rg = KNOB_D / 2, GRIP_D / 2
    step = r - rg
    prof = Polygon((0, 0), (r, 0), (r, SKIRT_H), (rg, SKIRT_H + step), (rg, KNOB_H), (0, KNOB_H),
                   align=None)
    body = revolve(Plane.XZ * prof, Axis.Z, 360)
    circles = body.edges().filter_by(GeomType.CIRCLE)
    body = fillet(circles.group_by(Axis.Z)[0], BOTTOM_FILLET)
    circles = body.edges().filter_by(GeomType.CIRCLE)
    body = chamfer(circles.group_by(Axis.Z)[-1], TOP_CHAMFER)
    return body


def _flutes() -> Part:
    rc = GRIP_D / 2 + FLUTE_R - FLUTE_DEPTH
    one = Pos(0, 0, FLUTE_Z0) * Cylinder(FLUTE_R, KNOB_H - FLUTE_Z0 + 1, align=ON_BED)
    one += Pos(0, 0, FLUTE_Z0 - FLUTE_R) * Cone(0, FLUTE_R, FLUTE_R, align=ON_BED)
    out = None
    for i in range(FLUTES):
        a = 360 / FLUTES * (i + 0.5)
        f = Rot(0, 0, a) * Pos(rc, 0, 0) * one
        out = f if out is None else out + f
    return out


def _numbers() -> Part:
    r = KNOB_D / 2
    out = None
    for i in range(11):
        a = math.radians(NUM_START + NUM_STEP * i)
        rad = Vector(math.cos(a), math.sin(a), 0)
        tan = Vector(-math.sin(a), math.cos(a), 0)
        pl = Plane(origin=rad * (r - TEXT_DEPTH) + Vector(0, 0, NUM_Z), x_dir=tan, z_dir=rad)
        t = extrude(pl * Text(str(i), font_size=NUM_SIZE), TEXT_DEPTH + 1.0)
        tick = Rot(0, 0, math.degrees(a)) * Pos(r, 0, TICK_Z) * Box(2 * TICK_DEPTH, TICK_W, TICK_H)
        for s in (t, tick):
            out = s if out is None else out + s
    return out


def _bore() -> Part:
    if VARIANT == "knurled":
        ro = (hole_d(KNURL_OD) - KNURL_INTERFERENCE) / 2
        ri = ro - KNURL_TOOTH_H
        pts = []
        for k in range(2 * KNURL_TEETH):
            a = math.pi * k / KNURL_TEETH
            rr = ro if k % 2 == 0 else ri
            pts.append((rr * math.cos(a), rr * math.sin(a)))
        return extrude(Plane.XY * Polygon(*pts, align=None), BORE_DEPTH)
    d = _solid_d()
    return Cylinder(d / 2, BORE_DEPTH, align=ON_BED)


def _solid_d() -> float:
    return clearance(SOLID_SHAFT_D, SOLID_FIT)


def _setscrew(bore_r: float) -> Part:
    r = KNOB_D / 2
    r_in = bore_r + NUT_WALL
    nut = Pos(r_in + NUT_T / 2, 0, 0) * Box(NUT_T, NUT_AF, SCREW_Z + NUT_AF / 2, align=ON_BED)
    sd = clearance(SCREW_D, "slide")
    length = r + 1 - (bore_r - 0.5)
    hole = Pos((r + 1 + bore_r - 0.5) / 2, 0, SCREW_Z) * Rot(180, 0, 0) * teardrop_hole(sd, length, along="X")
    return Rot(0, 0, SCREW_ANGLE) * (nut + hole)


def build() -> Part:
    knob = _body()
    under = Cylinder(FELT_D / 2, FELT_DEPTH, align=ON_BED) + Cylinder(
        BUSHING_D / 2, FELT_DEPTH + BUSHING_DEPTH, align=ON_BED)
    knob = knob - _flutes() - _numbers() - under - _bore()
    if VARIANT == "setscrew":
        knob = knob - _setscrew(_solid_d() / 2)
    return knob
