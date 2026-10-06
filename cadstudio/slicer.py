"""Headless Bambu Studio slicing with flattened H2C system presets."""

from __future__ import annotations

import json
import platform
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

from .config import CACHE_DIR, REPO, settings, slicer_install
from .gravity import PrintPlan
from .profiles import PresetError, compatible, flatten, resolve_material, resolve_quality
from .report import Check

SLICE_INFO = "Metadata/slice_info.config"
BRIM_WIDTH_MM = "5"


def ensure_installed():
    install = slicer_install()
    if install is None and platform.system() == "Linux":
        subprocess.run(["bash", str(REPO / "scripts/install-slicer.sh")], check=False)
        install = slicer_install()
    return install


def build_presets(profiles: Path, meta: dict, plan: PrintPlan, work: Path) -> tuple[Path, Path, Path, str]:
    cfg = settings()
    machine_name = cfg["printer"]["machine"]
    machine = flatten("machine", machine_name, profiles)
    _, process_name, overrides = resolve_quality(meta["quality"])
    process = flatten("process", process_name, profiles)
    _, filament_name = resolve_material(meta["material"])
    filament = flatten("filament", filament_name, profiles)
    for kind, preset, name in (("process", process, process_name), ("filament", filament, filament_name)):
        if not compatible(preset, machine_name):
            raise PresetError(f"{kind} preset {name!r} is for {preset['compatible_printers']}, not {machine_name}")
    for preset in (process, filament):
        preset["from"] = "system"

    process.update(overrides)
    process["curr_bed_type"] = cfg["printer"]["plate"]
    process["enable_support"] = "1" if plan.supports else "0"
    if plan.supports:
        process["support_type"] = "tree(auto)"
    if plan.brim:
        process["brim_type"] = "outer_only"
        process["brim_width"] = BRIM_WIDTH_MM

    paths = []
    for kind, preset in (("machine", machine), ("process", process), ("filament", filament)):
        path = work / f"{kind}.json"
        path.write_text(json.dumps(preset))
        paths.append(path)
    return paths[0], paths[1], paths[2], f"{process_name} + {filament_name}"


def parse_slice_info(three_mf: Path) -> dict:
    with zipfile.ZipFile(three_mf) as archive:
        text = archive.read(SLICE_INFO).decode()
    seconds = sum(int(v) for v in re.findall(r'key="prediction"\s+value="(\d+)"', text))
    grams = sum(float(v) for v in re.findall(r'key="weight"\s+value="([\d.]+)"', text))
    warnings = sorted(set(re.findall(r'<warning msg="([^"]+)"', text)))
    return {"seconds": seconds, "grams": round(grams, 1), "warnings": warnings}


def duration(seconds: int) -> str:
    hours, minutes = divmod(round(seconds / 60), 60)
    return f"{hours}h{minutes:02d}m" if hours else f"{minutes}m"


def slice_model(name: str, meta: dict, plan: PrintPlan, work: Path, out: Path) -> Check:
    install = ensure_installed()
    if install is None:
        return Check("slice", "SKIP", "Bambu Studio not installed (scripts/install-slicer.sh)")

    stl = work / f"{name}.stl"
    plan.mesh.export(stl)
    try:
        machine, process, filament, preset_label = build_presets(install.profiles, meta, plan, work)
    except PresetError as error:
        return Check("slice", "FAIL", str(error))
    target = out / f"{name}.3mf"
    target.unlink(missing_ok=True)
    datadir = CACHE_DIR / "bambu-datadir"
    datadir.mkdir(parents=True, exist_ok=True)

    command = [
        str(install.binary),
        "--datadir", str(datadir),
        "--orient", "0",
        "--arrange", "1",
        "--load-settings", f"{machine};{process}",
        "--load-filaments", str(filament),
        "--slice", "0",
        "--outputdir", str(work),
        "--export-3mf", target.name,
    ]
    if meta.get("copies", 1) > 1:
        command += ["--clone-objects", str(meta["copies"] - 1)]
    command.append(str(stl))

    timeout = settings()["slicer"]["timeout_s"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, cwd=work)
    except subprocess.TimeoutExpired:
        return Check("slice", "FAIL", f"slicer timed out after {timeout}s")
    produced = work / target.name
    if result.returncode != 0 or not produced.exists():
        log = work / "slicer.log"
        log.write_text(result.stdout + "\n" + result.stderr)
        return Check("slice", "FAIL", f"slicer exit {result.returncode}: {slicer_error(work, result)} (log: {log.relative_to(REPO)})")
    shutil.move(produced, target)

    info = parse_slice_info(target)
    facts = {**info, "preset": preset_label}
    summary = f"{duration(info['seconds'])}, {info['grams']} g ({preset_label})"
    if info["warnings"]:
        return Check("slice", "WARN", f"{summary}; slicer warnings: {'; '.join(info['warnings'])}", facts)
    return Check("slice", "OK", summary, facts)


def slicer_error(work: Path, result: subprocess.CompletedProcess) -> str:
    report = work / "result.json"
    if report.exists():
        try:
            data = json.loads(report.read_text())
            return str(data.get("error_string") or data.get("return_code"))[:300]
        except json.JSONDecodeError:
            pass
    lines = [l for l in (result.stderr or result.stdout).splitlines() if "error" in l.lower()]
    return (lines[-1] if lines else "unknown error")[-300:]
