"""neck-rest: stepped two-height guitar neck rest for bench setup / maintenance.

Spec: wide flat base plate carrying a stepped block with two curved cradles side by side
(X axis = across the neck, Y axis = along the neck). Low cradle for a guitar lying flat on a
thin mat, high cradle for thicker bodies / a towel under the body. Cradle radius suits neck
backs of 20-25 mm depth (C/D/U profiles, ~42-56 mm wide). Every edge the guitar can touch is
filleted (FILLET_R >= 1 mm). Each cradle has a shallow recess for a self-adhesive felt or cork
strip so the finish never touches plastic.

FINISH WARNING: some rubbers / vinyls / silicone-free "gel" pads react with nitrocellulose
lacquer (marks or softens it). Use FELT (or cork) in the pad recesses, not rubber.

Assumptions:
- Neck back approximates an arc of R ~25 mm (50 mm chord, 22 mm sagitta); cradle R = 30 mm
  leaves room for a ~3 mm felt pad (recess 1.5 mm deep, felt protrudes ~1.5 mm).
- Felt strip per cradle: ~55 mm (around the curve) x PAD_L = 42 mm, 3 mm self-adhesive felt.
- Cradle heights (bottom of curve above bench): ~23 mm (low) and ~48 mm (high).
- Base plate bottom: optional stick-on felt/rubber feet (bench side only, never guitar side).
- Contact-edge rounding is done by offset (FILLET_R = 2 mm), concave junctions stay sharp.
- Load 1.5 kg (neck + part of guitar weight) on the high cradle for the tip-over audit.
"""

from build123d import *

from cadlib import *

# Coordinates = in-use orientation, Z up, mm. The audit picks the print orientation.

# Parameters
BASE_L = 180.0        # X, across the neck
BASE_W = 100.0        # Y, along the neck
BASE_T = 5.0
BASE_R = 8.0

BLOCK_W = 80.0        # X width of each step
BLOCK_D = 50.0        # Y depth of the blocks (support length along the neck)
LOW_H = 45.0          # top of low step
HIGH_H = 70.0         # top of high step

CRADLE_R = 30.0       # cradle radius (neck back R ~25 + felt)
CRADLE_DEPTH = 22.0   # depth of the curve below the step top
FILLET_R = 2.0        # guitar-contact edge fillets (>= 1 mm)

PAD_DEPTH = 1.5       # felt recess depth
PAD_MARGIN = 4.0      # recess inset from cradle ends (Y)
PAD_HALF_X = 24.0     # recess half-width in X (keeps filleted lips intact)
PAD_L = BLOCK_D - 2 * PAD_MARGIN

LOW_X = -BLOCK_W / 2
HIGH_X = BLOCK_W / 2

META = dict(
    material="AzureFilm ABS PLUS @BBL H2C 0.4 nozzle",
    quality="Guitar Core ABS+ 0.20mm @BBL H2C",
    standing=True,
    loads=[dict(at=(HIGH_X, 0, HIGH_H - CRADLE_DEPTH), grams=1500)],
    print_orientation="auto",
    supports="auto",
    brim="auto",
)


def _cradle_center_z(top):
    return top + CRADLE_R - CRADLE_DEPTH


def _cyl_y(r, length, x, z):
    return Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(r, length)


def build() -> Part:
    # Build the stepped block shrunk by FILLET_R, then offset outward with arcs:
    # every convex edge the guitar can touch becomes a FILLET_R round (clean mesh,
    # unlike 3-way fillet corner patches).
    r = FILLET_R
    z0 = 1.0  # block bottom buried inside the base plate
    prof = Polygon(
        (-BLOCK_W + r, z0 + r), (BLOCK_W - r, z0 + r), (BLOCK_W - r, HIGH_H - r),
        (r, HIGH_H - r), (r, LOW_H - r), (-BLOCK_W + r, LOW_H - r), align=None,
    )
    block = extrude(Plane.XZ * prof, BLOCK_D / 2 - r, both=True)
    for x, top in ((LOW_X, LOW_H), (HIGH_X, HIGH_H)):
        block -= _cyl_y(CRADLE_R + r, BLOCK_D + 2, x, _cradle_center_z(top))
    block = offset(block, r, kind=Kind.ARC)

    base = rounded_box(BASE_L, BASE_W, BASE_T, radius=BASE_R, top_radius=1.0)
    part = base + block

    # felt pad recesses
    for x, top in ((LOW_X, LOW_H), (HIGH_X, HIGH_H)):
        cz = _cradle_center_z(top)
        band = _cyl_y(CRADLE_R + PAD_DEPTH, PAD_L, x, cz) & Pos(x, 0, cz - CRADLE_R - 5) * Box(
            2 * PAD_HALF_X, PAD_L, CRADLE_R + 5, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
        part -= band
    return part
