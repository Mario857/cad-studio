"""castanets: two pairs of castanets (4 hollowed shells) with cord holes and a cord groove.

Spec
- Each shell: round cup Ø SHELL_D with an ear lobe (EAR_W wide, EAR_EXT beyond the cup) carrying
  two vertical Ø3.2 cord holes and a 90 deg V cord groove joining them on the back.
- Cup depth H = 14 mm, rim 3 mm wide (the clapping face), back plate 2.5 mm. The back has a 45 deg
  chamfer of 5 mm, so the shell prints rim-up with no supports.
- Pair "macho" (left hand, lower) Ø55, pair "hembra" (right hand, higher) Ø52; 2 shells per pair.
- Model coordinates = print orientation (rim up, back on the bed). In use, two shells of a pair face
  each other rim-to-rim, hinged by the cord through the ears.

Assumptions
- ABS-like E = 2.2 GPa, rho = 1050 kg/m3, nu = 0.35. Walls up to 3 mm print solid (standard profile)
  so plate formulas apply.
- 4 separate bodies on one plate (intended).
- Cord 2 mm (Ø3.2 holes leave room for doubling the cord through).

TUNING (c = 343 m/s; computed in tuning())
Helmholtz of the closed pair: f = c/(2 pi) sqrt(A/(V L_eff)), V = 2 x cup volume,
A = rim slit = perimeter x gap g, L_eff = rim width + 1.7 (g/2).
Back plate (clamped circular plate, first mode): f = 10.22/(2 pi a^2) sqrt(D/(rho h)), D = E h^3/(12(1-nu^2)).
| shell | target | computed |
|-------|--------|----------|
| macho Ø55: cavity V (pair) | -      | 37.6 cm3 |
| macho Ø55: Helmholtz g = 2 / 1 / 0.5 mm | ~1-2.5 kHz "click" | 2349 / 1835 / 1376 Hz |
| macho Ø55: back plate h = 2.5, a = 21.1 | ~4 kHz ring | 4094 Hz |
| hembra Ø52: cavity V (pair) | - | 32.8 cm3 |
| hembra Ø52: Helmholtz g = 2 / 1 / 0.5 mm | higher | 2440 / 1907 / 1429 Hz |
| hembra Ø52: back plate a = 19.6 | higher | 4746 Hz |
Fine-tuning: thinning the back plate (sanding the back flat) LOWERS the plate ring (f ~ h).
Thinning the rim (narrower clapping face) shortens the slit neck -> RAISES the Helmholtz click and
removes edge mass -> slightly raises the ring. Deepening the cup (more V) LOWERS the click.
Sand the rims flat on 240 grit on glass so the shells close airtight; this makes the crispest click.

Hardware to buy: 1 m of 2 mm braided cord (nylon/cotton), lighter to seal the ends.

Assembly (per pair): 1. Sand the rims flat. 2. Put two shells rim-to-rim with the ears aligned. 3. Thread
the cord down through hole A of both ears, along the back groove, up through hole B of both, and along
the other back groove. 4. Tie a loop sized to your thumb (the knot sits on the ear top), then seal the cord ends.
5. Adjust the loop so the shells rest ~2 mm open; play the lower pair (macho) in the left hand.
"""

import math

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(0, 0, 0),  # rim up, back on bed
    supports="off",
    brim="auto",
)

C_SOUND = 343.0
E_MOD = 2.2e9
RHO_P = 1050.0
NU = 0.35
SHELL_D = (55.0, 52.0)     # macho (low), hembra (high)
H = 14.0
RIM_W = 3.0
BACK_T = 2.5
BACK_CHAMFER = 5.0
CAV_TAPER = 0.3            # cavity wall: radial inset per mm depth (bowl shape)
EAR_W = 24.0
EAR_EXT = 12.0
CORD_HOLE = 3.2
HOLE_X = 4.0
HOLE_Y = 3.0               # beyond the cup radius
GROOVE = 2.4               # V groove width (90 deg)
GAPS = (2.0, 1.0, 0.5)
SPACING = 75.0


def outline(R):
    ear_c = R + EAR_EXT - EAR_W / 2
    return (Circle(R) + Pos(0, ear_c / 2) * Rectangle(EAR_W, ear_c) + Pos(0, ear_c) * Circle(EAR_W / 2))


def cavity(R):
    depth = H - BACK_T
    r_top = R - RIM_W
    return Pos(0, 0, BACK_T) * Cone(r_top - CAV_TAPER * depth, r_top, depth + 0.01,
                                    align=(Align.CENTER, Align.CENTER, Align.MIN))


def shell(R):
    o = outline(R)
    lower = loft([Plane.XY * offset(o, -BACK_CHAMFER), Plane.XY.offset(BACK_CHAMFER) * o])
    upper = extrude(Plane.XY.offset(BACK_CHAMFER) * o, H - BACK_CHAMFER)
    s = lower + upper
    s = s - cavity(R)
    hy = R + HOLE_Y
    for x in (-HOLE_X, HOLE_X):
        s = s - Pos(x, hy, -1) * Cylinder(CORD_HOLE / 2, H + 2, align=ON_BED)
    g = GROOVE / 2
    groove = extrude(Plane.YZ * Polygon((hy - g - 0.5, -0.5), (hy + g + 0.5, -0.5), (hy, g + 0.5), align=None),
                     HOLE_X, both=True)
    return s - groove


def tuning(R):
    depth = H - BACK_T
    r1 = R - RIM_W
    r2 = r1 - CAV_TAPER * depth
    v_cup = math.pi * depth / 3 * (r1 * r1 + r1 * r2 + r2 * r2) * 1e-9
    V = 2 * v_cup
    P = 2 * math.pi * (R - RIM_W / 2) * 1e-3
    helm = []
    for g in GAPS:
        A = P * g * 1e-3
        L = (RIM_W + 1.7 * g / 2) * 1e-3
        helm.append(C_SOUND / (2 * math.pi) * math.sqrt(A / (V * L)))
    h = BACK_T * 1e-3
    a = r2 * 1e-3
    D = E_MOD * h**3 / (12 * (1 - NU**2))
    f_plate = 10.22 / (2 * math.pi * a * a) * math.sqrt(D / (RHO_P * h))
    return V * 1e6, helm, f_plate, r2


def build():
    parts = []
    s = SPACING / 2
    for i, d in enumerate(SHELL_D):
        sh = shell(d / 2)
        for j in range(2):
            parts.append(Pos((-s if j == 0 else s), (s if i == 0 else -s) - 8, 0) * sh)
    return parts


if __name__ == "__main__":
    for d in SHELL_D:
        print(d, tuning(d / 2))
