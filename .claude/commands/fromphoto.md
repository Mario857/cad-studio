---
description: Design a part from a photo or sketch (all photo-derived dims are UNVERIFIED)
argument-hint: <image path> [reference object + its real size, e.g. "credit card 85.6 mm"] [what to make]
---
Design from image: $ARGUMENTS

1. Read `docs/lessons.md` and `docs/photo-guide.md`. Open the image ONCE with Read (images cost tokens; never re-open).
2. Write down, before any CAD: (a) what the object is and what it must do, (b) the scale reference used (named
   object in the frame with its known size, or "none"), (c) each dimension as `value ±error`, tagged `MEASURED`
   only if it is printed/written in the image or is a standard (M4, 608...), else `UNVERIFIED`.
3. Follow CLAUDE.md waste-prevention: any UNVERIFIED mating dimension → design the fit gauge/coupon FIRST
   (`/design` rules), then stop and ask the user to measure/test. Do not design the final part from photo sizes alone.
4. If there is no scale reference, do not guess sizes: reply with the list of dimensions you need measured
   (calipers) and a one-line photo tip. At most 6 lines.
