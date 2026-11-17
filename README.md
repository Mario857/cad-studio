# cad-studio

Design 3D-printable parts by talking to Claude Code (from your phone), print them on a **Bambu Lab H2C**.

Claude writes a small parametric [build123d](https://github.com/gumyr/build123d) script; deterministic,
free tools in this repo do the rest and hand back a ~10-line verdict:

| stage | what it checks / does |
|---|---|
| build | runs `models/<category>/<name>/model.py`, exports STEP + STL, B-rep validity |
| mesh | watertight, winding, volume, size, stray bodies (more bodies than `build()` returns parts) |
| walls | ray-cast wall thickness (fail < 0.6 mm, warn < 1.2 mm) |
| fit | parts of one print that overlap, touch or sit < 0.2 mm apart (they would print fused); assembly overlaps, mate gaps |
| use (gravity) | in-use tip-over angle incl. carried loads, weak side to widen |
| orient (gravity) | searches stable resting poses for least support / overhang, best bed contact |
| support | floating bodies, auto tree supports, auto brim for small/tall footprints |
| slice | headless Bambu Studio, H2C presets → ready-to-print `.3mf`, time + grams |
| preview | 4-view PNG for you (Claude doesn't read it unless asked: images cost tokens) |
| render (on demand) | `./cad render`: ray-traced 8-view sheet with a section cut, via Blender (not part of `check`) |

## From your phone

1. Open the Claude app → **Code** → choose this GitHub repo.
2. Type `/design wall bracket for a 25 mm pipe, two M4 screws` (or just describe it).
3. Claude iterates until `PASS`, commits `models/<category>/<name>/` and pushes a branch.
4. In the GitHub app, open `models/<category>/<name>/out/`: `<name>.stl` renders as a rotatable 3D view,
   `preview.png` shows all views, `<name>.3mf` is the sliced print file
   (`git pull`, open it in Bambu Studio, press Print — it is already sliced for the H2C).

Other commands: `/printed <name> ok|fail|tweak <note>` (log the real print result → lessons), `/tweak <name> <change>`, `/look <name>` (visual review, costs image tokens).

## Locally

```bash
./cad new my-part          # scaffold from templates/model.py
./cad check my-part        # full pipeline (add --no-slice for fast iteration)
./cad preview my-part      # only the PNG
./cad render my-part       # Blender review sheet -> out/render.png (--cut z=12, --hero for out/hero.png)
./cad list                 # models + last verdict
./cad doctor               # toolchain status
scripts/test-cloud-env.sh  # replay a fresh cloud session in Docker (x86_64 Ubuntu 24.04)
```

Requires [uv](https://docs.astral.sh/uv/); macOS uses the installed Bambu Studio app, Linux/cloud installs
the pinned Bambu Studio AppImage automatically (`scripts/install-slicer.sh`, ~250 MB, background on
session start).

## Rendered review sheet (`./cad render`)

`out/render.png` shows eight ray-traced views: iso front/back, front, side, top, bottom, a capped
section cut and the as-printed pose, with one colour per body. `--cut x|y|z[=mm]` moves the section
(default: through the middle of the biggest body), `--hero` adds a large perspective shot (`out/hero.png`).

No Blender install is needed: the first run lets uv fetch the pinned `bpy` wheel (Blender as a Python
module, ~250 MB on macOS, ~430 MB on Linux) into uv's own cache; the project environment is untouched.
To use an installed Blender instead: `CAD_BLENDER_BIN=/Applications/Blender.app/Contents/MacOS/Blender`.
It renders on the CPU with Cycles, so it works headless in cloud sessions (about 5-10 s per view on
a 2-core cloud machine). `CAD_TEST_BLENDER=1 uv run pytest tests/test_render.py` runs a real render.

## Keeping Claude cheap

- `.claude/settings.json` defaults to **Sonnet**; switch to Opus with `/model` only for hard geometry.
- `CLAUDE.md` has token-budget rules: no reading meshes/3MF/images, iterate with `--no-slice`,
  max 5 iterations, short replies, the cadlib + build123d API inline so nothing needs exploring.
- Read-deny rules block STL/3MF/STEP/`.work`/`.venv` reads.
- All heavy lifting (audit, orientation search, slicing) is local CPU, not tokens.
- The SessionStart hook prints a single line.

## Layout

```
cad                 entry point (uv run python -m cadstudio)
cadstudio/          pipeline: build, mesh_check, gravity, slicer, preview, report; render + blender_scene (Blender sheet)
cadlib/             helpers for models: fasteners, fits, teardrops, ribs, labels
config/printer.toml printer, plate, materials, qualities, audit thresholds
models/<category>/<name>/      model.py + out/ (stl, step, 3mf, preview.png, report.md, render.png on demand)
templates/model.py  scaffold for ./cad new
scripts/            setup.sh (SessionStart), install-slicer.sh, test-cloud-env.sh
.claude/            settings (model, hook, permissions) and /design /tweak /look commands
```

## Changing printer setup

Edit `config/printer.toml`: nozzle profile (`machine`), `plate`, material → filament preset,
quality → process preset (+ overrides like the `strong` quality), audit thresholds.

## Your own Bambu Studio presets

`profiles/filament/` and `profiles/process/` hold the user presets from Bambu Studio (H2C ones only).
Use them by exact name in `META`, e.g. `material="Hyperspeed PETG", quality="Small stuff"`;
`./cad materials` lists everything usable with the configured nozzle. Inheritance from Bambu system
presets (including per-nozzle `"nil"` entries) is resolved at slice time, so they work in the cloud too.
Supports are still switched on/off by the gravity audit (META `supports`); the rest of the process
preset is kept.

After creating or editing presets in Bambu Studio on the Mac: `./cad profiles-sync`, commit, push.
