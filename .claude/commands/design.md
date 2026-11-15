---
description: Design a new printable part from a short description
argument-hint: <what it is, key sizes, what it attaches to / holds>
---
Design this part for the H2C: $ARGUMENTS

Read `docs/lessons.md`. Follow CLAUDE.md exactly (incl. the real-world waste prevention gate: tag dims MEASURED/UNVERIFIED; if a mating dim is UNVERIFIED, design a fit gauge first and stop there) (workflow, token budget rules, FDM rules). Pick a short kebab-case name,
state assumptions in the docstring, iterate with `--no-slice`, finish with a full `./cad check`,
then commit and push `models/<category>/<name>/`. Reply in ≤ 6 lines.
