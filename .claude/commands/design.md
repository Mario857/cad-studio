---
description: Design a new printable part from a short description (staged, gated, independently reviewed)
argument-hint: <what it is, key sizes, what it attaches to / holds>
---
Design this part for the H2C: $ARGUMENTS

Follow CLAUDE.md. Work in stages; do not skip a stage. Stay terse: stage outputs live in the model docstring.

**0. Context (cheap).** Read `docs/lessons.md`. If it mates with a real object, run `./cad objects <query>`; reuse
entries, never re-guess them. If the input is an image, use `/fromphoto` rules instead.

**1. Brief → docstring (before any geometry).** Write in `model.py`'s docstring:
- Function + environment (indoor/outdoor, heat, UV, wet, food contact) → pick material per `docs/materials.md`.
- Loads: static/dynamic N, direction, number of cycles → declare `force=` / `loads=` in META.
- Every dimension tagged `MEASURED` or `UNVERIFIED`. Mechanism choice per `docs/mechanisms.md`.
- `Risks:` the 2-3 ways it will fail in real use. `Accept:` 3-5 pass/fail statements checkable on the real part
  (e.g. "slides onto 19 mm rod with light hand pressure", "holds 500 g for 24 h").

**2. Gate.** UNVERIFIED mating dimension, or first-print cost HIGH → build the fit gauge/coupon only
(`./cad coupon <name> --feature "<desc>"`), report, and stop. Otherwise continue.

**3. Build + verify.** Iterate `./cad check <name> --no-slice` (max 5). For parts with clearances also run
`--sweep`; for assemblies set `assembly`/`mates`; for loaded parts set `force`. Fix every FAIL and WARN
(or justify the WARN in the docstring). Then one full `./cad check <name>`.

**4. Independent review.** Spawn ONE fresh subagent (Agent tool, general-purpose) with only: the docstring,
`out/report.md`, and the instruction "act as a skeptical print-farm engineer: list the top 5 ways this part
fails or wastes a print in real use, citing docstring lines; reply <= 10 lines". Fix valid issues (max 1 extra
round); record the rest under `Risks:`.

**5. Deliver.** Commit `models/<category>/<name>/`, push. Reply <= 6 lines: what, key dims, time/grams/cost,
UNVERIFIED list (what to measure), the `Accept:` tests to run, and "after printing: /printed <name> ok|fail|tweak <note>".
