"""litter-scoop: cat litter scoop with sifting slots, raised side walls and ribbed handle.

Spec: 280 mm overall. Flat blade 150 x 125 mm with 8 mm lengthwise sifting slots (SLOT_W),
open front with a bevelled leading edge, back + side walls (sides taper from 32 mm at the back
to 10 mm at the front). Handle 130 mm long, 32 mm wide channel section (6 mm plate + 2 edge
rims + centre stiffening rib that ramps up into the back wall), Ø10 mm hang hole at the end.
Printed flat as used (walls up), so the handle's bending load runs along the layers.

Safety: ABS must not hold food/water directly and the scoop is not a chew toy; keep it out of
reach of pets. Rinse with water / mild soap only (no solvents). Not dishwasher safe.
Assumptions: 8 mm slots pass clumping litter granules (~1-4 mm) and retain clumps;
~400 g of litter/clumps carried at the blade centre; handle held at its middle.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=False,
    loads=[dict(at=(75, 0, 10), grams=400)],
    print_orientation=(0, 0, 0),  # flat as used: handle length along layers (strength)
    supports="off",
    brim="auto",
)

# Parameters
OVERALL_L = 280.0
BLADE_L = 150.0          # blade length (x 0..BLADE_L), front at x=0
BLADE_W = 125.0
FLOOR_T = 3.0
WALL_T = 2.4
WALL_H_BACK = 32.0
WALL_H_FRONT = 10.0
CORNER_R = 8.0
EDGE_FILLET = 1.0
LEAD_CHAMFER = 1.6       # bevel on the top of the front leading edge

SLOT_W = 8.0             # sifting slot width
SLOT_PITCH = 12.0        # slot centre spacing (4 mm bars)
SLOT_X0 = 14.0           # slot start from front
SLOT_X1 = BLADE_L - 14.0

HANDLE_W = 32.0
HANDLE_T = 6.0
RIM_W = 3.0
RIM_H = 5.0              # edge rim height above plate
RIB_T = 5.0
RIB_H = 10.0             # centre rib height above plate
HANG_D = 10.0
HANG_FROM_END = 14.0


def build() -> Part:
    hx0 = BLADE_L - WALL_T  # handle starts inside back wall
    # --- walls: ring minus interior, front removed, tops sloped
    ext = BLADE_L + CORNER_R  # extend past the front, then trim, so side-wall ends are flat
    outer = Pos(BLADE_L - ext / 2, 0, 0) * rounded_box(ext, BLADE_W, WALL_H_BACK, radius=CORNER_R)
    outer = outer & Box(BLADE_L, BLADE_W + 2, WALL_H_BACK + 2, align=(Align.MIN, Align.CENTER, Align.MIN))
    inner = Pos(BLADE_L - WALL_T - ext / 2, 0, -1) * rounded_box(
        ext, BLADE_W - 2 * WALL_T, WALL_H_BACK + 2, radius=CORNER_R - WALL_T, bottom_chamfer=0)
    walls = outer - inner
    # --- blade floor
    floor = Pos(BLADE_L - ext / 2, 0, 0) * rounded_box(ext, BLADE_W, FLOOR_T, radius=CORNER_R)
    floor = floor & Box(BLADE_L, BLADE_W + 2, FLOOR_T + 2, align=(Align.MIN, Align.CENTER, Align.MIN))
    wedge = extrude(Plane.XZ * Polygon(
        (0, WALL_H_FRONT), (BLADE_L + 1, WALL_H_BACK), (BLADE_L + 1, WALL_H_BACK + 20),
        (-5, WALL_H_BACK + 20), (-5, WALL_H_FRONT), align=None), BLADE_W, both=True)
    walls = walls - wedge
    walls = fillet([e for e in walls.edges() if e.bounding_box().min.Z > WALL_H_FRONT - 0.5], EDGE_FILLET)

    # --- handle plate with round end
    hl = OVERALL_L - hx0 - HANDLE_W / 2
    plate = extrude(Pos(hx0 + hl / 2, 0) * Rectangle(hl, HANDLE_W)
                    + Pos(OVERALL_L - HANDLE_W / 2, 0) * Circle(HANDLE_W / 2), HANDLE_T)
    rim_l = OVERALL_L - HANG_FROM_END - HANG_D - hx0 - 4
    rims = [Pos(hx0 + rim_l / 2, s * (HANDLE_W / 2 - RIM_W / 2), 0)
            * Box(rim_l, RIM_W, HANDLE_T + RIM_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
            for s in (-1, 1)]
    rib_end = OVERALL_L - HANG_FROM_END - HANG_D - 4
    rib_prof = Polygon(
        (hx0 + 0.6, 0), (hx0 + 0.6, WALL_H_BACK - 2), (hx0 + 4, WALL_H_BACK - 2), (hx0 + 30, HANDLE_T + RIB_H),
        (rib_end - 12, HANDLE_T + RIB_H), (rib_end, HANDLE_T), (rib_end, 0), align=None)
    rib_prof = fillet(rib_prof.vertices().sort_by(Axis.Y)[2:], 1.5)  # rounded outline
    rib = extrude(Plane.XZ * rib_prof, RIB_T / 2, both=True)
    # fillet each feature on its own (robust), then union
    rib = fillet([e for e in rib.edges() if e.bounding_box().min.Z > 0.5
                  and not (abs(e.tangent_at(0.5).Y) > 0.99)], EDGE_FILLET)
    rims = [fillet([e for e in r.edges() if e.bounding_box().min.Z > HANDLE_T + 0.5], EDGE_FILLET)
            for r in rims]
    plate = fillet([e for e in plate.edges() if e.bounding_box().min.Z > HANDLE_T - 0.1
                    and e.bounding_box().max.X > hx0 + 1], EDGE_FILLET)
    handle = plate + rims[0] + rims[1] + rib

    part = floor + walls + handle
    # --- sifting slots
    n = int((BLADE_W - 2 * WALL_T - 6 - SLOT_W) // SLOT_PITCH) + 1
    y0 = -(n - 1) * SLOT_PITCH / 2
    sl = SLOT_X1 - SLOT_X0
    for i in range(n):
        part -= Pos(SLOT_X0 + sl / 2, y0 + i * SLOT_PITCH, FLOOR_T + 1) * slot(sl, SLOT_W, FLOOR_T + 2)
    # soften slot top edges (litter flows, nothing sharp)
    part = fillet([e for e in part.edges() if abs(e.center().Z - FLOOR_T) < 0.01
                   and SLOT_X0 - 1 < e.center().X < SLOT_X1 + 1
                   and abs(e.center().Y) < BLADE_W / 2 - WALL_T - 1], 0.8)
    # --- hang hole
    part -= Pos(OVERALL_L - HANG_FROM_END, 0, HANDLE_T + 1) * Cylinder(
        HANG_D / 2, HANDLE_T + 2, align=(Align.CENTER, Align.CENTER, Align.MAX))
    # --- bevel leading edge (top-front edge of floor)
    lead = part.edges().filter_by(Axis.Y).filter_by_position(Axis.X, -0.1, 0.1) \
        .filter_by_position(Axis.Z, FLOOR_T - 0.1, FLOOR_T + 0.1)
    part = chamfer(lead, LEAD_CHAMFER)
    return part
