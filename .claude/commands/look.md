---
description: Visually review a model's rendered review sheet (costs image tokens)
argument-hint: <model-name> [what to look for]
---
Run `./cad render <name>` for: $ARGUMENTS (add `--cut x|y|z[=mm]` when the question is about the inside).
Then open `models/<category>/<name>/out/render.png` once and judge it against the docstring spec.
If it prints `render FAIL`, fall back to `./cad preview <name>` and `out/preview.png`.
Report problems in ≤ 5 lines; fix them only if they are clear errors, then follow the CLAUDE.md workflow.
