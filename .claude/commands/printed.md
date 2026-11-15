---
description: Record the real-world result of a print and learn from it
argument-hint: <model-name> <ok|fail|tweak> <what happened>
---
Real print result: $ARGUMENTS

Run `./cad log <name> <result> "<note>"`. If the result is `fail` or `tweak`: add ONE entry to
`docs/lessons.md` (symptom → cause → rule, ≤ 3 lines; generalise so it helps other parts), then apply the fix
to the model per `/tweak` (edit the UPPER_CASE parameter, never re-guess others). Reply in ≤ 3 lines.
