# cad-studio

Code-first design of FDM parts for a **Bambu Lab H2C** (0.4 mm nozzle, 300×320×320 mm usable).
Each part is one parametric build123d script: `models/<category>/<name>/model.py`. `./cad check <name>` does
everything else (build, mesh + wall checks, gravity audit, print orientation, supports, Bambu Studio slice).

## Token budget rules (important — sessions are paid per token)

- Do NOT read anything in `models/*/out/` except `report.md`; never open STL/3MF/STEP/G-code or `.work/`.
- Do NOT open `preview.png` unless the user asks you to look at it.
- Do NOT explore `cadstudio/`, `cadlib/`, `.venv/` or build123d sources — the API you need is below.
  If a build123d call fails, fix it from the error message; look up source only after two failed tries.
- Do NOT read other models unless the user references them.
- Iterate with `./cad check <name> --no-slice` (fast); run the full `./cad check <name>` once at the end.
- At most 5 check iterations. If still FAIL, stop and report what blocks it and the options.
- Ask a question only if a critical dimension is unknowable; otherwise assume, and write assumptions
  in the model docstring.
- Final reply: ≤ 6 lines (what was made, key dims, print time/grams, assumptions, path to `.3mf`).

## Workflow

1. `./cad new <kebab-name> --category <dir>` (dirs: bathroom christmas garden home kitchen money music office outdoor pet phone) → edit `models/<category>/<name>/model.py` (docstring spec, `META`, params, `build()`).
2. `./cad check <name> --no-slice` → fix every FAIL; fix WARNs unless the reason is stated in META/docstring.
3. `./cad check <name>` (slices; first run on a fresh cloud session may wait for the slicer install).
4. Commit `models/<category>/<name>/` including `out/` (`.3mf` is the print file) with message
   `<name>: <what changed>` and push. One commit per finished design, not per iteration.

## Model contract

- Units mm. Model coordinates = in-use orientation, Z up, part resting on z=0 if it stands.
- `build()` returns a build123d `Part` (or list of parts → printed together).
- `META`: `material` (PLA, PLA-MATTE, PLA-TOUGH, PETG, ABS, ASA, TPU, PC, or the exact name of one of
  the user's own presets), `quality` (draft | standard | strong | fine, or a user process preset name).
  When the user names a brand/colour/preset, run `./cad materials` once and use the exact name.
  `standing` (tip-over audit in use), `loads`
  (`[dict(at=(x,y,z), grams=g)]` carried in use), `print_orientation` ("auto" or `(rx, ry, rz)` deg),
  `supports`/`brim` ("auto" | "on" | "off"), `copies`.
- Keep all dimensions as named UPPER_CASE parameters at the top so changes are one-line edits.

## FDM design rules (the audit enforces most of these)

- Walls ≥ 1.2 mm (≥ 2 mm structural); fail < 0.6 mm. Min feature ~0.8 mm. Text ≥ 5 mm tall, 0.6 mm deep.
- Overhangs ≤ 45° from vertical. Replace flat ceilings with 45° chamfers; horizontal holes → `teardrop_hole`.
- Bottom edges: 0.4 mm chamfer (elephant foot), never a fillet on the bed. Fillets fine elsewhere.
- Bridges ≤ 15 mm. Prefer designs that print with zero supports.
- Layers are weak in Z: for hooks/brackets/clips under bending, set `print_orientation` so the load
  runs along layers (the auto orientation optimizes printability, not strength).
- Fits: use `clearance(size, fit)`; vertical holes via `hole_d()`/`pin_hole()`. Threads: use heat-set
  inserts (`insert_hole`) or nut traps, not printed threads below M8.
- Free-standing parts need tip angle ≥ 12° incl. loads; widen the base on the reported weak side.

## cadlib (`from cadlib import *`)

Cutters point down (-Z) from z=0: place on the surface, then subtract.
- `rounded_box(l, w, h, radius=2, top_radius=0, bottom_chamfer=0.4)` → on bed, centered XY
- `teardrop_hole(d, length, along="Y"|"X")` → centered horizontal support-free hole
- `rib(length, height, thickness)` → triangular gusset, corner at origin, +X/+Z legs, centered on Y
- `label(text, size=6, depth=0.6)` → text solid z 0..depth
- `slot(length, width, depth)` → stadium slot cutter, long axis X
- `bolt_hole(size, depth, head="socket"|"csk"|None)`, `nut_trap(size, depth=None, rotation=0)`,
  `insert_hole(size, depth=None)`, `pin_hole(d, depth)`; sizes "M2".."M8"; `METRIC[size]` dims
- `clearance(size, fit="slide")`, `hole_d(nominal)`, `FIT` = press .10 / snug .15 / slide .25 / loose .40
- `at(x, y, z, rx, ry, rz) * shape`, `ON_BED` align tuple

## build123d cheat sheet (algebra mode)

```python
Box(l, w, h, align=ON_BED); Cylinder(r, h, align=ON_BED); Cone(r1, r2, h); Sphere(r)
Pos(x, y, z) * shape; Rot(rx, ry, rz) * shape; a + b; a - b; a & b
extrude(Plane.XY * sketch, amount, both=False)  # Plane.XZ: local y = +Z; Plane.YZ: local x = +Y, y = +Z
revolve(Plane.XZ * profile, Axis.Z, 360)        # profile at x>0
loft([Plane.XY * s1, Plane.XY.offset(h) * s2]); sweep(Plane.YZ * s, path=Line/Spline/Polyline)
Rectangle(w, h); RectangleRounded(w, h, r); Circle(r); Ellipse(a, b); RegularPolygon(r, n)
Polygon((x, y), ..., align=None); SlotOverall(l, w); Text("t", font_size=s)
offset(sketch_or_part, amount); mirror(part, about=Plane.YZ); split(part, bisect_by=Plane.XY)
fillet(part.edges().filter_by(Axis.Z), r); chamfer(part.edges().group_by(Axis.Z)[0], d)
part.edges().group_by(Axis.Z)[-1]  # top edges; .faces().sort_by(Axis.Z)[-1] top face
part.edges().filter_by(GeomType.CIRCLE); Locations((x, y), ...) / GridLocations(dx, dy, nx, ny) * shape
shell: offset(part, -t, openings=part.faces().sort_by(Axis.Z)[-1])
```
Fillet failures: reduce radius or fillet before booleans. Keep booleans simple; union then cut.
