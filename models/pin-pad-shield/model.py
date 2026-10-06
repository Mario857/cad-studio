"""pin-pad-shield: slide-on privacy shield that hides PIN entry on a card terminal keypad.

Spec: C-channel sleeve (bottom plate, two side walls, two top lips) that slides onto the keypad
end of a handheld/countertop card terminal, plus two privacy wings rising from the side walls
(48 mm high at the screen end, 20 mm at the user end) so bystanders left/right cannot see the
keys. Lips overlap the bezel by LIP mm only, keys stay free. Open at both ends: slide on from the
bottom (user) end; friction fit via CLEAR. Fits keypads KEYPAD_W 70-90 mm (default 80).

MEASURE BEFORE PRINTING: keypad width (KEYPAD_W), bezel width beside the keypad (BEZEL, must be
> LIP), terminal thickness at the keypad (TERM_T).
Assumptions: terminal width = KEYPAD_W + 2*BEZEL (96 mm), 22 mm thick, flat-sided at the keypad,
edge radius <= 2 mm. Wings vertical so the screen above the keypad stays fully visible.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation=(90, 0, 0),  # sleeve axis vertical: C-profile and lips print with no overhang
    supports="off",
    brim="on",                 # stands on its 5 cm2 end face, 80 mm tall
)

# Parameters
KEYPAD_W = 80.0          # 70..90
BEZEL = 8.0              # terminal edge beside the keypad, per side
TERM_T = 22.0            # terminal thickness at the keypad
CLEAR = 0.3              # per side / on thickness (slide fit)
SLEEVE_L = 80.0          # along the keypad (Y)
WALL = 2.5
PLATE_T = 2.5
LIP = 4.0                # overlap onto the bezel (< BEZEL)
LIP_T = 2.5
WING_H_FAR = 48.0        # wing height above the lip, screen end (+Y)
WING_H_NEAR = 20.0       # user end (-Y)
WING_T = 2.5


def build() -> Part:
    term_w = KEYPAD_W + 2 * BEZEL
    xi = term_w / 2 + CLEAR                 # inner wall face
    z_top = PLATE_T + TERM_T + CLEAR        # underside of the lips
    z_lip = z_top + LIP_T
    outer_w = 2 * (xi + WALL)

    sleeve = Box(outer_w, SLEEVE_L, z_lip, align=ON_BED)
    sleeve -= Pos(0, 0, PLATE_T) * Box(2 * xi, SLEEVE_L + 2, TERM_T + CLEAR, align=ON_BED)
    sleeve -= Pos(0, 0, PLATE_T) * Box(2 * (xi - LIP), SLEEVE_L + 2, z_lip, align=ON_BED)
    sleeve = chamfer(sleeve.edges().group_by(Axis.Z)[0].filter_by(Axis.Y), 0.4)

    y0, y1 = -SLEEVE_L / 2, SLEEVE_L / 2
    prof = Polygon((y0, 0), (y1, 0), (y1, WING_H_FAR), (y0, WING_H_NEAR), align=None)
    wing = extrude(Plane.YZ * prof, WING_T / 2, both=True)
    wing = fillet(wing.edges().group_by(Axis.Z)[-1].filter_by(Axis.X), 1.0)
    for sx in (-1, 1):
        sleeve += Pos(sx * (xi + WALL - WING_T / 2), 0, z_lip) * wing
    return sleeve
