---
description: Design a new printable part from a short description
argument-hint: <what it is, key sizes, what it attaches to / holds>
---
Design this part for the H2C: $ARGUMENTS

Follow CLAUDE.md exactly (workflow, token budget rules, FDM rules). Pick a short kebab-case name,
state assumptions in the docstring, iterate with `--no-slice`, finish with a full `./cad check`,
then commit and push `models/<name>/`. Reply in ≤ 6 lines.
