# Mechanism rules of thumb (FDM, 0.4 mm nozzle). Not yet confirmed by prints: update after real results.

- **Press/slip fit**: use `clearance()` / `hole_d()`; calibrate once with `./cad calibrate`. Print a gauge when mate is UNVERIFIED.
- **Screw into plastic**: heat-set insert (`insert_hole`) for reuse; boss wall ≥ 2 mm around hole; never < 1.2 mm.
- **Cantilever snap-fit**: strain ≈ 1.5·t·δ / L² (t arm thickness, δ deflection, L length). Keep ≤ ~1% for PLA-TOUGH/PETG/ABS,
  avoid PLA. Arm length ≥ 8·t; root fillet ≥ 0.5·t; arm runs ALONG layers (print the arm lying down). Add a 1-2 mm lead-in ramp.
- **Living hinge**: PETG/TPU only, 0.4-0.6 mm web along layers; prefer a pin hinge (clearance 0.3 mm) in rigid materials.
- **Pin hinge**: pin print orientation parallel to bed; Ø ≥ 3 mm; clearance `FIT["slide"]`.
- **Hooks / brackets under bending**: load along layers; thickness ≥ 3 mm at the root; gusset `rib()` at inside corners.
- **Wall mount (screw/adhesive)**: screws need countersink + ≥ 2 mm floor; VHB tape needs ≥ 15 cm² flat, clean, low-energy-surface warning.
- **Springs**: do not print compression springs; use a printed flex arm only in PETG/PC/TPU, or buy a metal spring.
- **Threads**: no printed threads < M8; use inserts/nut traps.
- **Large flat parts (> 100 mm)**: warp risk in ABS/ASA/PC: rounded corners, brim, ribs instead of thick slabs.
- **Tolerance stack**: more than 2 mating features in a chain → add 0.2 mm slack each or make one adjustable (slot instead of hole).
