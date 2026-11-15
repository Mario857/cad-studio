"""Assembly fit check: unintended overlaps between parts and declared mate clearances."""

from __future__ import annotations

from .report import Check

MAX_OVERLAP_MM3 = 0.5


def overlap_volume(a, b) -> float:
    inter = a & b
    return float(inter.volume) if inter is not None else 0.0


def evaluate(parts: list, mates: list[dict], assembly: bool) -> Check | None:
    """Pure function over build123d shapes (testable without a model)."""
    if len(parts) < 2 or not (assembly or mates):
        return None
    fails, warns, facts = [], [], {}
    if assembly:
        for i in range(len(parts)):
            for j in range(i + 1, len(parts)):
                if parts[i].distance_to(parts[j]) > 0:
                    continue
                vol = overlap_volume(parts[i], parts[j])
                if vol > MAX_OVERLAP_MM3:
                    fails.append(f"parts {i}&{j} overlap {vol:.2f} mm3")
                    facts[f"overlap_{i}_{j}"] = round(vol, 3)
    for m in mates:
        a, b = m["a"], m["b"]
        lo, hi = m["clearance"]
        gap = float(parts[a].distance_to(parts[b]))
        facts[f"gap_{a}_{b}"] = round(gap, 3)
        if not lo <= gap <= hi:
            warns.append(f"mate {a}-{b} gap {gap:.2f} outside {lo}-{hi}")
    if fails:
        return Check("fit", "FAIL", "; ".join(fails + warns), facts)
    if warns:
        return Check("fit", "WARN", "; ".join(warns), facts)
    gaps = ", ".join(f"{k[4:].replace('_', '-')}: {v}" for k, v in facts.items() if k.startswith("gap"))
    return Check("fit", "OK", "no overlaps" + (f"; gaps {gaps}" if gaps else ""), facts)


def check_fit(result) -> Check | None:
    parts = result.parts
    mates = result.meta.get("mates") or []
    for m in mates:
        if not (0 <= m["a"] < len(parts) and 0 <= m["b"] < len(parts)):
            return Check("fit", "FAIL", f"mate {m['a']}-{m['b']}: part index out of range (have {len(parts)} parts)")
    try:
        return evaluate(parts, mates, bool(result.meta.get("assembly")))
    except Exception as error:  # never break the whole check over this
        return Check("fit", "WARN", f"interference check failed: {error}")
