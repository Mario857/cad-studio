"""Compact pass/warn/fail report: terse for the terminal (what Claude reads), fuller for report.md."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

RANK = {"OK": 0, "SKIP": 0, "WARN": 1, "FAIL": 2}


@dataclass
class Check:
    name: str
    status: str
    summary: str
    facts: dict = field(default_factory=dict)


@dataclass
class Report:
    model: str
    checks: list[Check] = field(default_factory=list)
    files: dict[str, str] = field(default_factory=dict)

    def add(self, check: Check) -> Check:
        self.checks.append(check)
        return check

    @property
    def verdict(self) -> str:
        worst = max((RANK[c.status] for c in self.checks), default=0)
        return {0: "PASS", 1: "PASS", 2: "FAIL"}[worst]

    def counts(self) -> str:
        warns = sum(c.status == "WARN" for c in self.checks)
        return f" ({warns} warn)" if warns else ""

    def terminal(self) -> str:
        lines = [f"{self.model}: {self.verdict}{self.counts()}"]
        for check in self.checks:
            lines.append(f"  {check.status:<4} {check.name:<7} {check.summary}")
        for label, path in self.files.items():
            lines.append(f"  file {label:<7} {path}")
        return "\n".join(lines)

    def markdown(self) -> str:
        lines = [f"# {self.model} — {self.verdict}{self.counts()}", "", "| check | status | result |", "|---|---|---|"]
        for check in self.checks:
            lines.append(f"| {check.name} | {check.status} | {check.summary} |")
        if self.files:
            lines += ["", "## Files", ""]
            lines += [f"- **{label}**: `{Path(path).name}`" for label, path in self.files.items()]
        return "\n".join(lines) + "\n"

    def write(self, out: Path) -> None:
        (out / "report.md").write_text(self.markdown())
        (out / "report.json").write_text(json.dumps(
            {"model": self.model, "verdict": self.verdict, "checks": [asdict(c) for c in self.checks], "files": self.files},
            indent=1,
            default=lambda value: value.item() if hasattr(value, "item") else str(value),
        ))
