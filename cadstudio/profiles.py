"""Preset resolution: repo `profiles/` (your Bambu Studio user presets) first, then Bambu system presets."""

from __future__ import annotations

import json
import shutil
from functools import cache
from pathlib import Path

from .config import REPO, settings, slicer_install

USER_PROFILES = REPO / "profiles"
BAMBU_USER_DIR = Path.home() / "Library/Application Support/BambuStudio/user"
KINDS = ("filament", "process")
NIL = "nil"
DEFAULT_DENSITY = 1.25


class PresetError(Exception):
    pass


@cache
def user_index(kind: str) -> dict[str, Path]:
    folder = USER_PROFILES / kind
    if not folder.exists():
        return {}
    return {json.loads(path.read_text())["name"]: path for path in sorted(folder.glob("*.json"))}


def system_dir() -> Path | None:
    install = slicer_install()
    return install.profiles if install else None


def preset_path(kind: str, name: str, system: Path | None) -> Path | None:
    if name in user_index(kind):
        return user_index(kind)[name]
    if system and (system / kind / f"{name}.json").exists():
        return system / kind / f"{name}.json"
    return None


def merge(parent: dict, child: dict) -> dict:
    """Child overrides parent; per-extruder-variant list entries of "nil" keep the parent's value (or stay "nil")."""
    merged = dict(parent)
    for key, value in child.items():
        inherited = parent.get(key)
        if isinstance(value, list) and NIL in value and isinstance(inherited, list):
            value = [inherited[i] if v == NIL and i < len(inherited) else v for i, v in enumerate(value)]
        merged[key] = value
    return merged


def flatten(kind: str, name: str, system: Path | None = None) -> dict:
    """The CLI ignores `inherits` for files passed on the command line, so resolve the chain here."""
    system = system or system_dir()
    if kind == "machine":
        path = system / kind / f"{name}.json" if system else None
    else:
        path = preset_path(kind, name, system)
    if path is None or not path.exists():
        raise PresetError(f"{kind} preset not found: {name!r} (./cad materials lists options)")
    leaf = json.loads(path.read_text())
    parent = leaf.pop("inherits", None)
    base = flatten(kind, parent, system) if parent else {}
    merged = merge(base, leaf)
    merged.setdefault("type", kind)
    merged.setdefault("instantiation", "true")
    return merged


def known(kind: str, name: str) -> bool:
    system = system_dir()
    return preset_path(kind, name, system) is not None or system is None


def resolve_material(material: str) -> tuple[str, str]:
    """META material → (alias key or preset name, filament preset name)."""
    aliases = settings()["materials"]
    if material.upper() in aliases:
        key = material.upper()
        return key, aliases[key]["filament"]
    if known("filament", material):
        return material, material
    raise PresetError(f"unknown material {material!r}; run ./cad materials")


def resolve_quality(quality: str) -> tuple[str, str, dict]:
    """META quality → (key, process preset name, overrides)."""
    qualities = settings()["qualities"]
    if quality in qualities:
        return quality, qualities[quality], settings().get("quality_overrides", {}).get(quality, {})
    if known("process", quality):
        return quality, quality, {}
    raise PresetError(f"unknown quality {quality!r}; run ./cad materials")


def density(material: str) -> float:
    aliases = settings()["materials"]
    if material in aliases:
        return float(aliases[material]["density"])
    try:
        value = flatten("filament", material).get("filament_density", [DEFAULT_DENSITY])
        return float(value[0] if isinstance(value, list) else value)
    except (PresetError, TypeError, ValueError):
        return DEFAULT_DENSITY


def compatible(preset: dict, machine: str) -> bool:
    printers = preset.get("compatible_printers") or []
    return not printers or machine in printers


def sync_from_bambu() -> tuple[list[str], list[str]]:
    """Copy H2C-compatible user presets from the local Bambu Studio install into profiles/."""
    system = system_dir()
    if system is None or not BAMBU_USER_DIR.exists():
        raise PresetError("needs Bambu Studio on this machine (macOS user presets folder)")
    imported, skipped = [], []
    for kind in KINDS:
        target = USER_PROFILES / kind
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
        user_index.cache_clear()
        sources = sorted(p for p in BAMBU_USER_DIR.glob(f"*/{kind}/**/*.json"))
        for source in sources:
            shutil.copy2(source, target / source.name)
        user_index.cache_clear()
        for name, path in list(user_index(kind).items()):
            try:
                printers = flatten(kind, name, system).get("compatible_printers") or []
            except PresetError:
                printers = []
            if not any("H2C" in printer for printer in printers):
                path.unlink()
                skipped.append(f"{kind}: {name}")
            else:
                imported.append(f"{kind}: {name}")
        user_index.cache_clear()
    return imported, skipped
