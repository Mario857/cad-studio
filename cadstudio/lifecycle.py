"""Model status lifecycle (draft | proto | validated) and first-print cost/risk."""

from __future__ import annotations

import re
import subprocess
from datetime import date, datetime
from pathlib import Path

from .config import model_dir, settings
from .report import Check

STATUSES = ("draft", "proto", "validated")
PRINTLOG = "PRINTLOG.md"


def log_ok(directory: Path) -> bool:
    """True when PRINTLOG.md exists and its last non-empty line is `ok`."""
    log = directory / PRINTLOG
    if not log.exists():
        return False
    lines = [l.strip().lower().rstrip(".!") for l in log.read_text().splitlines() if l.strip()]
    return bool(lines) and (lines[-1] == "ok" or lines[-1].endswith(" ok") or lines[-1].endswith(": ok"))


def declared_status(directory: Path) -> str | None:
    """META status read from model.py text, without importing it."""
    path = directory / "model.py"
    match = re.search(r"""\bstatus\s*=\s*["'](\w+)["']""", path.read_text()) if path.exists() else None
    return match.group(1) if match and match.group(1) in STATUSES else None


def effective_status(directory: Path, declared: str | None = None) -> str:
    if log_ok(directory):
        return "validated"
    return declared or declared_status(directory) or "draft"


def _git(directory: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(["git", "-C", str(directory), *args], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def _git_date(directory: Path, filename: str) -> date | None:
    stamp = _git(directory, "log", "-1", "--format=%cI", "--", filename)
    try:
        return datetime.fromisoformat(stamp).date() if stamp else None
    except ValueError:
        return None


def _log_date(directory: Path) -> date | None:
    dates = re.findall(r"\d{4}-\d{2}-\d{2}", (directory / PRINTLOG).read_text())
    if dates:
        try:
            return date.fromisoformat(dates[-1])
        except ValueError:
            pass
    return _git_date(directory, PRINTLOG)


def status_check(name: str, declared: str | None = None) -> Check:
    directory = model_dir(name)
    status = effective_status(directory, declared)
    facts = {"status": status}
    if status != "validated" or not log_ok(directory):
        return Check("status", "OK", status, facts)
    logged = _log_date(directory)
    changed = _git_date(directory, "model.py")
    dirty = bool(_git(directory, "status", "--porcelain", "--", "model.py"))
    if dirty or (logged and changed and changed > logged):
        return Check("status", "WARN", "validated part changed: justify in commit message", facts)
    return Check("status", "OK", "validated", facts)


def price_per_kg(material: str) -> float:
    cfg = settings()
    entry = cfg["materials"].get(str(material).upper(), {})
    return float(entry.get("price_per_kg", cfg.get("cost", {}).get("default_price_per_kg", 25)))


def cost_check(name: str, meta: dict, checks: list[Check], sliced: Check) -> Check:
    cfg = settings().get("cost", {})
    grams = float(sliced.facts["grams"])
    minutes = round(sliced.facts["seconds"] / 60)
    euros = grams / 1000 * price_per_kg(meta["material"])
    unverified = sum(int(c.facts.get("unverified", 0) or 0) for c in checks)
    validated = effective_status(model_dir(name), meta.get("status")) == "validated"
    big = minutes >= cfg.get("risk_minutes", 60) or grams >= cfg.get("risk_grams", 40)
    if big and (unverified > 0 or not validated):
        risk = "HIGH"
    elif big or unverified > 0 or not validated:
        risk = "MEDIUM"
    else:
        risk = "LOW"
    summary = f"cost: ~{grams:.0f} g, {minutes} min, ~{cfg.get('currency', 'EUR')} {euros:.2f}; first print risk: {risk}"
    facts = {"grams": grams, "minutes": minutes, "price": round(euros, 2), "risk": risk}
    if risk == "HIGH":
        return Check("cost", "WARN", summary + "; print a small prototype coupon of the critical features first", facts)
    return Check("cost", "OK", summary, facts)
