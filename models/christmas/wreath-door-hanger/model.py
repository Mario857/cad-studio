"""wreath-door-hanger: over-the-door wreath hanger, 300 mm drop, 3 kg rated.

Spec: a flat C/J-shaped strap. A thin (2.5 mm) strap rides over the top edge of the door
so the door still closes. A short inner leg grips the inside face, and a long outer leg drops
300 mm down the outside face to a J-hook that holds the wreath. Door thickness is the
DOOR_T parameter (35-45 mm doors; set it to your door and reprint). The side profile is
extruded WIDTH mm and printed lying flat (profile on the bed), so the hook and corner bending
loads run along the layers, not across them. The part is 307.5 mm long, which fits along the
H2C's 320 mm plate axis.

Assumptions:
- DOOR_T = 40 mm default (range 35-45); DOOR_CLR = 1.0 mm total slip clearance across the door.
- The door-to-frame head gap is >= 3 mm (strap is 2.5 mm). Legs are 3-4 mm thick on the faces;
  the door stop / weatherstrip must tolerate that (same as commercial metal hangers).
- "300 mm drop" = from the door top to the hook seat.
- 3 kg static load on the hook seat; ABS-type filament, quality="strong" (thick walls+infill).
"""

from build123d import *

from cadlib import *

# Parameters (mm)
DOOR_T = 40.0          # door thickness (35-45)
DOOR_CLR = 1.0         # total clearance across the door thickness
DROP = 300.0           # door top -> hook seat
WIDTH = 30.0           # strap width (print height)
STRAP_T = 2.5          # strap over door top (must be <= 3 for the door to close)
INNER_LEG_T = 3.0      # inner (room-side) leg thickness
INNER_LEG_L = 50.0     # inner leg length below door top
OUTER_LEG_T = 4.0      # outer leg thickness
HOOK_T = 5.0           # hook arm / lip thickness
HOOK_REACH = 25.0      # clear depth of the hook (wreath frame fits in here)
HOOK_LIP = 20.0        # lip height above hook bottom
EDGE_R = 1.0           # profile edge rounding
HOOK_INNER_R = 3.0     # fillet in the hook's inside corners
BED_CHAMFER = 0.4      # elephant-foot chamfer on the bed face
LOAD_G = 3000          # wreath mass

GAP = DOOR_T + DOOR_CLR
TOP = DROP + HOOK_T    # z of the door top (underside of strap)

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[dict(at=(GAP + OUTER_LEG_T + HOOK_REACH / 2, 0, HOOK_T), grams=LOAD_G)],
    print_orientation=(90, 0, 0),   # lying flat: profile on the bed, load along layers
    supports="off",
    brim="auto",
)


def build() -> Part:
    x_lip = GAP + OUTER_LEG_T + HOOK_REACH
    pts = [
        (-INNER_LEG_T, TOP - INNER_LEG_L),
        (0, TOP - INNER_LEG_L),
        (0, TOP),
        (GAP, TOP),
        (GAP, 0),
        (x_lip + HOOK_T, 0),
        (x_lip + HOOK_T, HOOK_LIP),
        (x_lip, HOOK_LIP),
        (x_lip, HOOK_T),
        (GAP + OUTER_LEG_T, HOOK_T),
        (GAP + OUTER_LEG_T, TOP + STRAP_T),
        (-INNER_LEG_T, TOP + STRAP_T),
    ]
    prof = Polygon(*pts, align=None)
    part = extrude(Plane.XZ * prof, WIDTH / 2, both=True)

    # Round the profile corners (edges parallel to Y); larger radius inside the hook.
    y_edges = part.edges().filter_by(Axis.Y)
    hook_inner = [e for e in y_edges
                  if abs(e.center().Z - HOOK_T) < 1e-3
                  and (abs(e.center().X - x_lip) < 1e-3
                       or abs(e.center().X - (GAP + OUTER_LEG_T)) < 1e-3)]
    part = fillet(hook_inner, HOOK_INNER_R)
    others = [e for e in part.edges().filter_by(Axis.Y)
              if e.length > WIDTH - 1e-3 and not (abs(e.center().Z - HOOK_T) < HOOK_INNER_R + 0.1)]
    # keep the two door-top inner corners sharp-ish (door edge sits there)
    others = [e for e in others
              if not (abs(e.center().Z - TOP) < 1e-3 and (abs(e.center().X) < 1e-3
                                                        or abs(e.center().X - GAP) < 1e-3))]
    part = fillet(others, EDGE_R)

    # Elephant-foot chamfer on the face that lies on the bed (min Y after rx=90).
    bed_face = part.faces().sort_by(Axis.Y)[0]
    part = chamfer(bed_face.edges(), BED_CHAMFER)
    return part
