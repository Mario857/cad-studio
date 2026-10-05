# cad-studio

Design 3D-printable parts by talking to Claude Code (from your phone), print them on a **Bambu Lab H2C**.

Claude writes a small parametric [build123d](https://github.com/gumyr/build123d) script; deterministic,
free tools in this repo do the rest and hand back a ~10-line verdict:

| stage | what it checks / does |
|---|---|
| build | runs `models/<name>/model.py`, exports STEP + STL, B-rep validity |
| mesh | watertight, winding, separate bodies, volume, size |
| walls | ray-cast wall thickness (fail < 0.6 mm, warn < 1.2 mm) |
| use (gravity) | in-use tip-over angle incl. carried loads, weak side to widen |
| orient (gravity) | searches stable resting poses for least support / overhang, best bed contact |
| support | floating bodies, auto tree supports, auto brim for small/tall footprints |
| slice | headless Bambu Studio, H2C presets → ready-to-print `.3mf`, time + grams |
| preview | 4-view PNG for you (Claude doesn't read it unless asked: images cost tokens) |

## From your phone

1. Open the Claude app → **Code** → choose this GitHub repo.
2. Type `/design wall bracket for a 25 mm pipe, two M4 screws` (or just describe it).
3. Claude iterates until `PASS`, commits `models/<name>/` and pushes a branch.
4. In the GitHub app, open `models/<name>/out/`: `<name>.stl` renders as a rotatable 3D view,
   `preview.png` shows all views, `<name>.3mf` is the sliced print file
   (`git pull`, open it in Bambu Studio, press Print — it is already sliced for the H2C).

Other commands: `/tweak <name> <change>`, `/look <name>` (visual review, costs image tokens).

## Locally

```bash
./cad new my-part          # scaffold from templates/model.py
./cad check my-part        # full pipeline (add --no-slice for fast iteration)
./cad preview my-part      # only the PNG
./cad list                 # models + last verdict
./cad doctor               # toolchain status
scripts/test-cloud-env.sh  # replay a fresh cloud session in Docker (x86_64 Ubuntu 24.04)
```

Requires [uv](https://docs.astral.sh/uv/); macOS uses the installed Bambu Studio app, Linux/cloud installs
the pinned Bambu Studio AppImage automatically (`scripts/install-slicer.sh`, ~250 MB, background on
session start).

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
cadstudio/          pipeline: build, mesh_check, gravity, slicer, preview, report
cadlib/             helpers for models: fasteners, fits, teardrops, ribs, labels
config/printer.toml printer, plate, materials, qualities, audit thresholds
models/<name>/      model.py + out/ (stl, step, 3mf, preview.png, report.md)
templates/model.py  scaffold for ./cad new
scripts/            setup.sh (SessionStart), install-slicer.sh, test-cloud-env.sh
.claude/            settings (model, hook, permissions) and /design /tweak /look commands
```

## Changing printer setup

Edit `config/printer.toml`: nozzle profile (`machine`), `plate`, material → filament preset,
quality → process preset (+ overrides like the `strong` quality), audit thresholds.
