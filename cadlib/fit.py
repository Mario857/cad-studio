"""Clearances tuned for a Bambu 0.4 mm nozzle (per side, mm)."""

FIT = {
    "press": 0.10,   # interference-ish, needs force
    "snug": 0.15,    # hand-press, holds by friction
    "slide": 0.25,   # moves freely, little play
    "loose": 0.40,   # rattles, easy assembly
}

# Small vertical holes print undersized; add this to the diameter.
HOLE_COMPENSATION = 0.2


_material: str | None = None


def set_material(name: str | None) -> None:
    """Select the material whose measured offsets (config/calibration.toml) apply; None = none."""
    global _material
    _material = name


def _offset(key: str) -> float:
    """Measured per-material offset in mm (0.0 if the material is not calibrated)."""
    if not _material:
        return 0.0
    import os
    import tomllib
    from pathlib import Path

    path = Path(os.environ.get("CAD_CALIBRATION_FILE", Path(__file__).resolve().parent.parent / "config" / "calibration.toml"))
    try:
        with path.open("rb") as handle:
            return float(tomllib.load(handle).get(_material, {}).get(key, 0.0))
    except (OSError, ValueError):
        return 0.0


def hole_d(nominal: float) -> float:
    """Diameter to model so a printed vertical hole measures `nominal`."""
    return nominal + HOLE_COMPENSATION + _offset("hole_offset")


def wall_t(nominal: float) -> float:
    """Thickness to model so a printed thin wall/peg measures `nominal` (calibrated per material)."""
    return nominal + _offset("wall_offset")


def clearance(size: float, fit: str = "slide") -> float:
    """Socket size for a peg/shaft of `size` mm (adds clearance on both sides)."""
    return size + 2 * FIT[fit] + _offset("hole_offset")
