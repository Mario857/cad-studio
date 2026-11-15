"""Real-world mating-object dimensions (mm). Look here before guessing: `obj("aa-battery")`, `./cad objects [query]`.

status: MEASURED (user calipers), STANDARD (published standard / manufacturer datasheet),
UNVERIFIED (taken from an existing model's docstring or memory: tag it UNVERIFIED in your docstring).
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from types import MappingProxyType

from .fasteners import METRIC

STATUSES = ("MEASURED", "STANDARD", "UNVERIFIED")


@dataclass(frozen=True)
class MatingObject:
    name: str
    dims: dict
    source: str
    status: str
    notes: str = field(default="")

    def __post_init__(self):
        if self.status not in STATUSES:
            raise ValueError(f"{self.name}: status must be one of {STATUSES}, got {self.status!r}")

    def __getitem__(self, key: str) -> float:
        return self.dims[key]

    def __str__(self) -> str:
        d = ", ".join(f"{k}={v:g}" for k, v in self.dims.items())
        note = f"  ({self.notes})" if self.notes else ""
        return f"{self.name} [{self.status}] {d}  <{self.source}>{note}"


_REG: dict[str, MatingObject] = {}


def _add(name, dims, source, status, notes=""):
    _REG[name] = MatingObject(name, dict(dims), source, status, notes)


# --- fasteners (from cadlib.fasteners.METRIC; head/nut across-flats per ISO 4762 / ISO 4032) ---
for _size, _s in METRIC.items():
    _add(f"{_size.lower()}-screw", dict(head_d=_s["head_d"], head_h=_s["head_h"], clear_hole=_s["clear"]),
         "ISO 4762 socket head; clearance hole = cadlib table", "STANDARD")
    _add(f"{_size.lower()}-nut", dict(af=_s["nut_af"], h=_s["nut_h"]),
         "ISO 4032 across-flats; h = cadlib table (can be below ISO max for M5+)", "STANDARD")

# --- bearings, batteries, coins ---
_add("608-bearing", dict(bore=8.0, od=22.0, width=7.0), "ISO 15 (608 skate bearing)", "STANDARD")
_add("aa-battery", dict(d=14.5, l=50.5), "IEC 60086 (R6)", "STANDARD", "models/home/battery-organizer")
_add("aaa-battery", dict(d=10.5, l=44.5), "IEC 60086 (R03)", "STANDARD", "models/home/battery-organizer")
_add("9v-battery", dict(w=26.5, t=17.5, h=48.5), "IEC 60086 (6F22)", "STANDARD", "models/home/battery-organizer")
_add("cr2032", dict(d=20.0, t=3.2), "IEC 60086 (CR2032)", "STANDARD")
_add("eur-2-coin", dict(d=25.75, t=2.20), "ECB euro coin specifications", "STANDARD")
_add("eur-1-coin", dict(d=23.25, t=2.33), "ECB euro coin specifications", "STANDARD")
_add("eur-50c-coin", dict(d=24.25, t=2.38), "ECB euro coin specifications", "STANDARD")
_add("eur-10c-coin", dict(d=19.75, t=1.93), "ECB euro coin specifications", "STANDARD")
_add("us-quarter", dict(d=24.26, t=1.75), "US Mint specifications", "STANDARD")
_add("us-dime", dict(d=17.91, t=1.35), "US Mint specifications", "STANDARD")
_add("us-nickel", dict(d=21.21, t=1.95), "US Mint specifications", "STANDARD")
_add("us-penny", dict(d=19.05, t=1.52), "US Mint specifications", "STANDARD")

# --- phone ---
_add("iphone-15-pro-max", dict(w=76.7, h=159.9, t=8.25, grams=221), "Apple tech specs (bare phone)", "STANDARD",
     "camera plateau excluded; add case thickness separately")
_add("iphone-case", dict(wall_per_side=2.5, grams=30), "models/phone/ip15pm-magsafe-desk-stand assumption",
     "UNVERIFIED", "measure your case")
_add("magsafe-puck", dict(d=56.0, t=5.5, centre_from_phone_bottom=80.0),
     "models/phone/ip15pm-magsafe-desk-stand docstring", "UNVERIFIED", "third-party pucks differ")

# --- home / hardware documented in existing models (not independently verified) ---
_add("curtain-rod", dict(d=9.0), "models/home/curtain-hook-* docstrings (user's rod)", "UNVERIFIED",
     "measure with calipers")
_add("upvc-window-frame", dict(outer_wall=2.75, screw_max_len=12.0, screw_d=3.5),
     "models/home/curtain-hook-latch docstring (2.5-3 mm outer wall; steel liner >=10 mm behind surface)",
     "UNVERIFIED", "keep screws <= 12 mm")
_add("vhb-tape", dict(width=19.0), "models/home/curtain-rod-hook-vhb PLATE_W", "UNVERIFIED")
_add("guitar-pot-shaft", dict(d=6.0, bushing_tip_d=10.5, bushing_protrusion=2.0),
     "models/home/control-knob assumptions (6 mm split-knurl, metric pots)", "UNVERIFIED",
     "1/4 inch solid shafts are 6.35")
_add("mason-jar-regular-mouth", dict(thread_major_d=70.0, thread_pitch=4.23, thread_depth=1.6),
     "models/garden/mason-jar-tip-lid docstring (6 TPI)", "UNVERIFIED", "measure the jar glass")

OBJECTS = MappingProxyType(_REG)


def list_objects(query: str = "") -> list[MatingObject]:
    """All objects, or those whose name/source/notes contain `query` (case-insensitive)."""
    q = query.lower().strip()
    return [o for o in _REG.values() if not q or q in f"{o.name} {o.source} {o.notes}".lower()]


def obj(name: str) -> MatingObject:
    """Look up an object by name; raises KeyError listing close names."""
    key = name.lower().strip().replace("_", "-").replace(" ", "-")
    if key in _REG:
        return _REG[key]
    close = difflib.get_close_matches(key, _REG, n=5, cutoff=0.5)
    close += [n for n in _REG if key in n and n not in close]
    hint = f"close names: {', '.join(close[:8])}" if close else f"known: {', '.join(_REG)}"
    raise KeyError(f"unknown object {name!r}; {hint}")
