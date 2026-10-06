"""furniture-glide: push-on cup glide for round chair/table legs, felt pad underneath.

Spec: a cup that presses onto the end of a round leg (LEG_D, default 30 mm) with a press fit
(bore = clearance(LEG_D, "press")). Underneath, a 2 mm deep round recess takes a self-adhesive
felt pad (FELT_D) so the felt sits slightly proud of the plastic rim. Lead-in chamfer at the
mouth eases pushing it on. Printed as a set of 4.

Assumptions:
- Leg end is flat and round; LEG_D is the measured diameter (change one line for other legs).
- Felt pad: standard 28 mm round self-adhesive pad, ~3 mm thick, so it protrudes ~1 mm
  below the rim (FELT_DEPTH 2 mm recess as specified). Recess dia has 0.4 mm loose fit.
- Socket depth 12 mm is enough grip for a press fit; wall 2.4 mm (6 perimeters).
- Printed in use orientation (felt recess on the bed side): the recess ceiling is a short
  bridge only 2 mm above the bed; the slicer bridges it, it is hidden under the felt.
  The audit's support WARN for that ceiling is accepted on purpose (supports=off): supports
  in a 2 mm pocket would be unremovable, and any bridge sag is covered by the felt.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[],
    print_orientation="auto",
    supports="off",            # only overhang is the 2 mm-high felt-recess ceiling: bridged, hidden under felt
    brim="auto",
    copies=4,
)

# Parameters
LEG_D = 30.0                          # leg diameter
BORE_D = clearance(LEG_D, "press")    # socket bore
WALL = 2.4                            # side wall
SOCKET_DEPTH = 12.0                   # how far the leg goes in
FLOOR = 2.0                           # solid floor between socket and felt recess
FELT_D = 28.0                         # felt pad diameter
FELT_RECESS_D = FELT_D + 0.4          # recess diameter (loose)
FELT_DEPTH = 2.0                      # recess depth
LEAD_IN = 1.0                         # mouth chamfer
TOP_FILLET = 1.0                      # outer top edge round

OUTER_D = BORE_D + 2 * WALL
HEIGHT = FELT_DEPTH + FLOOR + SOCKET_DEPTH


def build() -> Part:
    body = Cylinder(OUTER_D / 2, HEIGHT, align=ON_BED)
    body = chamfer(body.edges().group_by(Axis.Z)[0], 0.4)
    body = fillet(body.edges().group_by(Axis.Z)[-1], TOP_FILLET)

    # socket with lead-in chamfer
    socket = Pos(0, 0, HEIGHT - SOCKET_DEPTH) * Cylinder(BORE_D / 2, SOCKET_DEPTH + 1, align=ON_BED)
    lead = Pos(0, 0, HEIGHT - LEAD_IN) * Cone(BORE_D / 2, BORE_D / 2 + LEAD_IN + 0.01,
                                              LEAD_IN + 0.01, align=ON_BED)
    # felt recess from below
    recess = Pos(0, 0, -0.01) * Cylinder(FELT_RECESS_D / 2, FELT_DEPTH + 0.01, align=ON_BED)
    return body - socket - lead - recess
