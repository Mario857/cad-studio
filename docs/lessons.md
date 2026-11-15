# Lessons (read before designing; append when a real print fails)

Rule: every entry = symptom → cause → rule. Keep each ≤ 3 lines. Add via `./cad log <name> fail "<note>"`
then distil here. Entries marked (seed) are inferred from history, not yet confirmed by a print.

- (seed) Thin walls (<1.2 mm) next to screw holes crack → keep ≥ 2 mm around any screw/insert; the audit's
  walls check passes at 0.6 mm but that is only "slices", not "survives".
- (seed) Mating parts printed at nominal size do not fit → never trust nominal; use `clearance()`, and when
  the mate is an object you do not have measured, print a fit gauge first (see models/music/guitar-knob-fit-gauge).
- (seed) Parts that hold a load in bending split along layers → set `print_orientation` so load runs along layers.
- (seed) ABS/ASA/PC warp on big flat footprints → corner brim, avoid > 100 mm flat slabs, round the corners.
