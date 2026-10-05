"""Clearances tuned for a Bambu 0.4 mm nozzle (per side, mm)."""

FIT = {
    "press": 0.10,   # interference-ish, needs force
    "snug": 0.15,    # hand-press, holds by friction
    "slide": 0.25,   # moves freely, little play
    "loose": 0.40,   # rattles, easy assembly
}

# Small vertical holes print undersized; add this to the diameter.
HOLE_COMPENSATION = 0.2


def hole_d(nominal: float) -> float:
    """Diameter to model so a printed vertical hole measures `nominal`."""
    return nominal + HOLE_COMPENSATION


def clearance(size: float, fit: str = "slide") -> float:
    """Socket size for a peg/shaft of `size` mm (adds clearance on both sides)."""
    return size + 2 * FIT[fit]
