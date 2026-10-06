"""raised-bed-corner: outside corner bracket for a raised bed with a 150 mm ground spike.

Spec: an L-angle that wraps the outside of a 90° corner of two 145 x 20 mm boards, full board
height, with 3 countersunk wood-screw holes per leg, and a tapering L-section spike that
continues 150 mm below the boards into the ground. Set of 4 (one per corner) via copies.
Load: ~20 kg (≈ 200 N) of soil pressure pushing the boards outward per corner. On an outside
bracket the boards bear against the legs (screws only locate), the legs carry it as horizontal
bending/tension into the corner. Printed upside down (rim on the bed, spike up) so those
horizontal stresses run along the layers.
Material: AzureFilm ABS PLUS. ABS+ yellows/embrittles after a season or two in full sun; the
user's "AzureFilm ASA @BBL H2C 0.4 nozzle" preset is the long-life swap (same geometry).

Assumptions:
- Butt joint: board A runs along +X (outer face y = 0), board B along +Y (outer face x = 0)
  butting against A's inner face; screw columns sit SCREW_INSET from the outside corner so both
  bite into side grain (not into the other board's end).
- Screws: 4.0 mm countersunk wood screws, ≥ 30 mm long (e.g. 4 x 35, stainless for outdoors).
- Spike: 150 mm below the board bottom (z = 0 = board bottom / soil line).
- Horizontal holes are teardrops; the countersink cone is 90°.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="strong",
    standing=False,
    loads=[],                     # outward soil load is horizontal; documented above
    print_orientation=(180, 0, 0),  # rim on the bed, spike up: horizontal stresses along layers
    supports="off",
    brim="on",
    copies=4,
)

BOARD_H = 145.0
BOARD_T = 20.0
LEG = 70.0             # leg length from the outside corner
T = 6.0                # leg thickness
SPIKE_LEN = 150.0
SPIKE_LEG = 30.0       # spike L-flange width at the top
SPIKE_TIP = 8.0        # flange width left at the tip
SCREW_D = 4.0
SCREW_CLEAR = clearance(SCREW_D, "loose")
SCREW_HEAD_D = 8.0
SCREW_INSET = 45.0     # screw column distance from the outside corner
SCREW_ZS = (25.0, 72.5, 120.0)
TOP_CHAMFER = 0.4


def leg_profile(width_top: float, width_tip: float) -> Sketch:
    """Leg outline in its own plane (local x along the leg from the corner, local y = Z)."""
    return Polygon(
        (-T, BOARD_H), (LEG, BOARD_H), (LEG, 0), (width_top - T, 0),
        (width_tip - T, -SPIKE_LEN), (-T, -SPIKE_LEN), align=None,
    )


def csk_cutter() -> Part:
    """Countersunk screw hole along +Y into the material from y = 0 (outer face at y = 0)."""
    shank = teardrop_hole(SCREW_CLEAR, 2 * T + 2, along="Y", tip="-Z")
    head = Cone(SCREW_HEAD_D / 2 + 0.3, SCREW_CLEAR / 2, SCREW_HEAD_D / 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return shank + Rot(-90, 0, 0) * head


def build() -> Part:
    prof = leg_profile(SPIKE_LEG, SPIKE_TIP)
    leg_a = extrude(Plane.XZ * prof, T, dir=(0, -1, 0))                 # y in [-T, 0]
    leg_b = mirror(leg_a, about=Plane(origin=(0, 0, 0), x_dir=(1, 1, 0), z_dir=(1, -1, 0)))
    part = leg_a + leg_b
    part = chamfer(part.edges().group_by(Axis.Z)[-1], TOP_CHAMFER)
    for z in SCREW_ZS:
        part -= Pos(SCREW_INSET, -T, z) * csk_cutter()
        part -= Pos(-T, SCREW_INSET, z) * Rot(0, 0, -90) * csk_cutter()
    return part
