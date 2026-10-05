from __future__ import annotations

import os
import platform
import tomllib
from dataclasses import dataclass
from functools import cache
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MODELS_DIR = REPO / "models"
CONFIG_FILE = REPO / "config" / "printer.toml"
CACHE_DIR = Path(os.environ.get("CAD_CACHE_DIR", Path.home() / ".cache" / "cad-studio"))

MAC_APP = Path("/Applications/BambuStudio.app")
LINUX_SLICER_DIR = CACHE_DIR / "bambu-studio"


@cache
def settings() -> dict:
    with CONFIG_FILE.open("rb") as handle:
        return tomllib.load(handle)


def audit_cfg() -> dict:
    return settings()["audit"]


def printer_cfg() -> dict:
    return settings()["printer"]


@dataclass(frozen=True)
class SlicerInstall:
    binary: Path
    profiles: Path


def slicer_install() -> SlicerInstall | None:
    override = os.environ.get("CAD_SLICER_BIN")
    if override:
        binary = Path(override)
        profiles = Path(os.environ.get("CAD_SLICER_PROFILES", binary.parent.parent / "Resources/profiles/BBL"))
        return SlicerInstall(binary, profiles) if binary.exists() else None
    if platform.system() == "Darwin":
        install = SlicerInstall(MAC_APP / "Contents/MacOS/BambuStudio", MAC_APP / "Contents/Resources/profiles/BBL")
    else:
        root = LINUX_SLICER_DIR / "squashfs-root"
        install = SlicerInstall(root / "AppRun", root / "resources/profiles/BBL")
    return install if install.binary.exists() and install.profiles.exists() else None


def model_dir(name: str) -> Path:
    return MODELS_DIR / name


def out_dir(name: str) -> Path:
    path = model_dir(name) / "out"
    path.mkdir(parents=True, exist_ok=True)
    return path


def work_dir(name: str) -> Path:
    path = out_dir(name) / ".work"
    path.mkdir(parents=True, exist_ok=True)
    return path
