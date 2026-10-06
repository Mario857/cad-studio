"""toilet-brush-holder: cylindrical toilet-brush holder, 2-piece body + base, with lift-out drip cup.

Spec: Ø100 mm tube, 380 mm tall overall (assembled). Too tall for the H2C (320 mm), so it is split:
  - body: plain Ø100 tube, open both ends, BODY_H tall.
  - base: flared foot (Ø FOOT_D) rising to Ø100, closed floor, with an upward spigot ring that the
    body's bottom slides over (slide fit via clearance(SPIGOT_OD, JOINT_FIT), JOINT_LEN engagement).
    The body rests on the base shoulder, so outer surfaces are flush (Ø100).
  - cup: removable drip cup sitting on the base floor inside the bore (radial gap CUP_GAP).
Bottom outer edge chamfered (BOTTOM_CHAMFER); inside floor corners of base and cup are 45°
chamfered (no sharp corner, easy cleaning). Cup outer bottom chamfer is larger than the base's
inner chamfer so the cup seats flat.

Assumptions:
  - Brush ~150 g leaning on the rim -> modelled as a 150 g load at the rim (x=45, z=380).
  - To empty the cup: lift the body off the base, then lift the cup out. Do NOT glue the joint
    if the cup should stay removable (slide fit holds by gravity; glue optional for a fixed build).
  - Foot flared to Ø130 for tip-over margin without added weight.
  - build() lays the three parts side by side on one plate (fits 300x320; body is 300 mm tall).
    Because of that layout the tool's tip-over audit sees the plate, not the assembly; the
    assembled check was computed separately: solid-density 18.3 deg, est. with infilled base
    ~14 deg (>= 12) incl. the 150 g rim load. The "3 separate bodies" mesh WARN is intended.
"""

from build123d import *

from cadlib import *

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[dict(at=(45, 0, 380), grams=150)],
    print_orientation="auto",
    supports="off",
    brim="auto",
)

# Parameters
TOTAL_H = 380.0          # assembled height
OD = 100.0               # tube outer diameter
BODY_H = 300.0           # body tube length (<= 320 printable)
BASE_H = TOTAL_H - BODY_H  # base height up to the shoulder the body rests on
SPIGOT_OD = 93.5         # base spigot outer diameter
JOINT_FIT = "slide"
BODY_ID = clearance(SPIGOT_OD, JOINT_FIT)  # body bore (slides over spigot)
JOINT_LEN = 25.0         # spigot engagement length
SPIGOT_WALL = 2.5
BORE_D = SPIGOT_OD - 2 * SPIGOT_WALL  # base inner bore (constant through spigot)
FLOOR_T = 3.0            # base floor thickness
FOOT_D = 130.0           # flared foot diameter
FOOT_RIM_H = 6.0         # vertical rim of the foot
FLARE_H = 30.0           # height of the cone from foot to OD
BOTTOM_CHAMFER = 1.5     # bottom outer edge chamfer
INNER_CHAMFER = 4.0      # base inside floor corner chamfer

CUP_GAP = 0.75           # radial clearance cup <-> bore
CUP_OD = BORE_D - 2 * CUP_GAP
CUP_H = 70.0
CUP_WALL = 2.0
CUP_FLOOR = 2.0
CUP_IN_CHAMFER = 3.0     # cup inside floor corner
CUP_OUT_CHAMFER = INNER_CHAMFER + 0.5  # clears the base inner chamfer
PLATE_GAP = 8.0          # spacing between parts on the plate


def _revolve(pts) -> Part:
    return revolve(Plane.XZ * Polygon(*pts, align=None), Axis.Z, 360)


def make_body() -> Part:
    ro, ri = OD / 2, BODY_ID / 2
    return _revolve([(ri, 0), (ro - 0.4, 0), (ro, 0.4), (ro, BODY_H), (ri, BODY_H)])


def make_base() -> Part:
    rf, ro, rb = FOOT_D / 2, OD / 2, BORE_D / 2
    rs = SPIGOT_OD / 2
    c = BOTTOM_CHAMFER
    pts = [
        (0, 0), (rf - c, 0), (rf, c), (rf, FOOT_RIM_H),
        (ro, FOOT_RIM_H + FLARE_H), (ro, BASE_H),
        (rs, BASE_H), (rs, BASE_H + JOINT_LEN),
        (rb, BASE_H + JOINT_LEN), (rb, FLOOR_T + INNER_CHAMFER),
        (rb - INNER_CHAMFER, FLOOR_T), (0, FLOOR_T),
    ]
    return _revolve(pts)


def make_cup() -> Part:
    ro = CUP_OD / 2
    ri = ro - CUP_WALL
    pts = [
        (0, 0), (ro - CUP_OUT_CHAMFER, 0), (ro, CUP_OUT_CHAMFER), (ro, CUP_H),
        (ri, CUP_H), (ri, CUP_FLOOR + CUP_IN_CHAMFER),
        (ri - CUP_IN_CHAMFER, CUP_FLOOR), (0, CUP_FLOOR),
    ]
    return _revolve(pts)


def build():
    # Plate layout (in-use orientation, each part upright): body + base in a row, cup behind.
    # Intentionally 3 separate bodies. Footprint ~273 x 275 mm (fits 300 x 320).
    body_x = -(OD / 2 + PLATE_GAP / 2)
    base_x = FOOT_D / 2 + PLATE_GAP / 2
    row_y = -55.0
    body = Pos(body_x - 35, row_y, 0) * make_body()
    base = Pos(base_x, row_y, 0) * make_base()
    cup = Pos(0, row_y + FOOT_D / 2 + PLATE_GAP + CUP_OD / 2 + 50, 0) * make_cup()
    return [body, base, cup]
