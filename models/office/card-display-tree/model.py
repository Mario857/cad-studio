"""card-display-tree: stepped Christmas-tree stand that holds 20 greeting cards upright in slots.

Spec: seen from the front the stand is a tree silhouette made of 6 stepped tiers
(5, 5, 4, 3, 2, 1 cards = 20). Each tier's top surface has card slots; inside a tier the
cards alternate between a front and a back slot line so neighbours can overlap sideways
without touching. Tiers rise RISE and step back TIER_D, so every row shows above the one in
front (stadium seating). The tiers are one sloped slab whose underside is parallel to the
stair nosing (31 deg from vertical -> support-free), on a thin base plate that extends
behind for backward tip stability. One piece, fits the plate, no assembly.

Assumptions:
- Cards are up to 105 mm wide x 150 mm tall (portrait, folded) and <= 1 mm thick.
  Landscape cards (150 wide) would need PITCH >= 78 (fewer cards per row).
- Each card ~20 g (400 g total), load modelled at each card's centroid.
- Slot 1.6 mm wide (1 mm stock + 0.6 clearance), 12 mm deep: cards stand vertically.
"""

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm. Front of the tree faces -Y.

# Parameters - cards / slots
CARD_W = 105.0            # max card width (portrait)
CARD_H = 150.0            # max card height
CARD_T = 1.0              # max card stock thickness
CARD_GRAMS = 20.0         # per card (20 cards ~ 400 g)
SLOT_CLEAR = 0.6          # total clearance across the slot
SLOT_W = CARD_T + SLOT_CLEAR  # slot width
SLOT_LEN = 30.0           # slot length along X (card is wider, only its bottom centre sits in it)
SLOT_D = 12.0             # slot depth
PITCH = 55.0              # X spacing of cards in a row (2*PITCH > CARD_W -> no collisions per line)
SLOT_Y = (4.0, 12.0)      # front / back slot line, measured from the tier's front edge

# Parameters - tree
ROW_CARDS = (5, 5, 4, 3, 2, 1)  # bottom -> top, sum = 20
TIER_D = 18.0             # tread depth of one tier (Y)
RISE = 30.0               # height step between tiers
H0 = 25.0                 # top of the bottom tier
SLAB_V = 40.0             # vertical thickness of the sloped slab below the stair nosing
END_MARGIN = 8.0          # solid material beyond the outer slots in X
BASE_T = 4.0              # base plate thickness
BASE_BACK = 40.0          # base plate extension behind the last tier
EF_CHAMFER = 0.4          # elephant-foot chamfer on bed edges

SLOPE = RISE / TIER_D


def tier_width(n: int) -> float:
    return (n - 1) * PITCH + SLOT_LEN + 2 * END_MARGIN


def tier_top(k: int) -> float:
    return H0 + k * RISE


def tier_y(k: int) -> float:
    return k * TIER_D


def z_under(y: float) -> float:
    """Underside of the sloped slab (parallel to the stair nosing line)."""
    return H0 - SLAB_V + y * SLOPE


def card_positions():
    for k, n in enumerate(ROW_CARDS):
        for j in range(n):
            x = (j - (n - 1) / 2) * PITCH
            y = tier_y(k) + SLOT_Y[j % 2]
            yield k, x, y


META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="standard",
    standing=True,
    loads=[
        dict(at=(x, y, tier_top(k) - SLOT_D + CARD_H / 2), grams=CARD_GRAMS)
        for k, x, y in card_positions()
    ],
    print_orientation="auto",
    supports="off",
    brim="auto",
)


def build() -> Part:
    total_d = len(ROW_CARDS) * TIER_D
    top = tier_top(len(ROW_CARDS) - 1)

    part = None
    for k, n in enumerate(ROW_CARDS):
        y0, y1, h = tier_y(k), tier_y(k) + TIER_D, tier_top(k)
        prof = Polygon((y0, h), (y1, h), (y1, z_under(y1)), (y0, z_under(y0)), align=None)
        tier = extrude(Plane.YZ * prof, amount=tier_width(n) / 2, both=True)
        part = tier if part is None else part + tier

    # clip anything below the bed, add base plate
    w0 = tier_width(ROW_CARDS[0])
    part = part & Pos(0, total_d / 2, top / 2 + 1) * Box(w0 + 2, total_d + 2, top + 2)
    base = Pos(0, (total_d + BASE_BACK) / 2, 0) * Box(w0, total_d + BASE_BACK, BASE_T, align=ON_BED)
    part = part + base

    # card slots
    for k, x, y in card_positions():
        cut = Pos(x, y, tier_top(k) - SLOT_D / 2) * Box(SLOT_LEN, SLOT_W, SLOT_D + 0.01)
        part = part - cut

    part = chamfer(part.edges().group_by(Axis.Z)[0], EF_CHAMFER)
    return part
