"""Fit check: overlaps between parts, declared mate clearances, and parts that would print fused."""

from __future__ import annotations

from .config import audit_cfg
from .report import Check

MAX_OVERLAP_MM3 = 0.5
FUSE_GAP_MM = 0.2  # default for [audit] fuse_gap_mm: closer than this, neighbouring bodies weld together
MAX_PAIRS = 300


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


def near(a, b, pad: float) -> bool:
    """Bounding boxes within `pad` of each other (cheap reject before the exact distance)."""
    low_a, high_a, low_b, high_b = tuple(a.min), tuple(a.max), tuple(b.min), tuple(b.max)
    return all(low_a[k] - pad <= high_b[k] and low_b[k] - pad <= high_a[k] for k in range(3))


def fuse_risks(pieces: list, min_gap: float = FUSE_GAP_MM) -> Check | None:
    """Pieces are sliced exactly where build() put them, so bodies that overlap, touch or sit closer than
    `min_gap` come off the bed as one lump. Pure function over build123d shapes."""
    if len(pieces) < 2:
        return None
    boxes = [piece.bounding_box() for piece in pieces]
    pairs = [(i, j) for i in range(len(pieces)) for j in range(i + 1, len(pieces)) if near(boxes[i], boxes[j], min_gap)]
    risks, facts, closest = [], {}, None
    for i, j in pairs[:MAX_PAIRS]:
        gap = float(pieces[i].distance_to(pieces[j]))
        if gap >= min_gap:
            closest = gap if closest is None else min(closest, gap)
            continue
        if gap > 0:
            risks.append(f"parts {i}&{j} only {gap:.2f} mm apart")
            facts[f"gap_{i}_{j}"] = round(gap, 3)
            continue
        volume = overlap_volume(pieces[i], pieces[j])
        risks.append(f"parts {i}&{j} overlap {volume:.1f} mm3" if volume > MAX_OVERLAP_MM3 else f"parts {i}&{j} touch")
        facts[f"overlap_{i}_{j}"] = round(volume, 3)
    skipped = f" (first {MAX_PAIRS} of {len(pairs)} close pairs checked)" if len(pairs) > MAX_PAIRS else ""
    if risks:
        more = f" (+{len(risks) - 3} more)" if len(risks) > 3 else ""
        return Check("fit", "WARN", f"{'; '.join(risks[:3])}{more} — they will print fused: separate by >= "
                     f"{min_gap} mm, or union them{skipped}", facts)
    apart = f"closest pair {closest:.2f} mm" if closest is not None else f"all > {min_gap} mm apart"
    return Check("fit", "OK", f"{len(pieces)} parts print separately, {apart}{skipped}", facts)


def merge(first: Check | None, second: Check | None) -> Check | None:
    if first is None or second is None:
        return first or second
    rank = {"OK": 0, "WARN": 1, "FAIL": 2}
    status = max(first.status, second.status, key=rank.__getitem__)
    return Check("fit", status, f"{first.summary}; {second.summary}", {**first.facts, **second.facts})


def check_fit(result) -> Check | None:
    parts = result.parts
    mates = result.meta.get("mates") or []
    assembly = bool(result.meta.get("assembly"))
    for m in mates:
        if not (0 <= m["a"] < len(parts) and 0 <= m["b"] < len(parts)):
            return Check("fit", "FAIL", f"mate {m['a']}-{m['b']}: part index out of range (have {len(parts)} parts)")
    try:
        declared = evaluate(parts, mates, assembly)
        # assembly=True shows the parts mated in their use positions, where contact is the point.
        pieces = [] if assembly else (getattr(result, "pieces", None) or parts)
        fused = fuse_risks(pieces, float(audit_cfg().get("fuse_gap_mm", FUSE_GAP_MM)))
        return merge(declared, fused)
    except Exception as error:  # never break the whole check over this
        return Check("fit", "WARN", f"interference check failed: {error}")
