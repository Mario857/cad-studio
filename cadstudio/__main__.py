"""./cad <command> — see `./cad -h`."""

from __future__ import annotations

import argparse
import json
import re
import sys

from .config import MODELS_DIR, REPO, audit_cfg, model_dir, out_dir, settings, slicer_install, work_dir
from .report import Check, Report

TEMPLATE = REPO / "templates" / "model.py"


def rel(path) -> str:
    return str(path.relative_to(REPO))


def cmd_new(args) -> int:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*(/[a-z0-9][a-z0-9-]*)?", args.name):
        print("name must be kebab-case: lowercase letters, digits, dashes")
        return 2
    if "/" not in args.name and list(MODELS_DIR.glob(f"*/{args.name}/model.py")):
        print(f"exists: {args.name}")
        return 1
    if "/" not in args.name:
        args.name = f"{args.category}/{args.name}"
    target = MODELS_DIR / args.name / "model.py"
    if target.exists():
        print(f"exists: {rel(target)}")
        return 1
    target.parent.mkdir(parents=True)
    target.write_text(TEMPLATE.read_text().replace("{{NAME}}", args.name.split("/")[-1]))
    print(f"created {rel(target)}")
    return 0


def run_check(name: str, do_slice: bool, do_preview: bool) -> Report:
    from .build import BuildError, build
    from .gravity import plan_print, use_stability
    from .mesh_check import integrity, load_mesh, wall_thickness
    from .profiles import density

    report = Report(name)
    out = out_dir(name)
    try:
        result = build(name)
    except BuildError as error:
        report.add(Check("build", "FAIL", str(error)))
        return report
    report.add(Check("build", "WARN" if result.notes else "OK", "; ".join(result.notes) or "B-rep valid"))
    report.files.update(stl=rel(result.stl), step=rel(result.step))

    mesh = load_mesh(result.stl)
    if report.add(integrity(mesh, result.brep_valid)).status == "FAIL":
        return report
    report.add(wall_thickness(mesh))
    from .interference import check_fit

    if (fit := check_fit(result)):
        report.add(fit)
    estimated_grams = mesh.volume / 1000 * density(result.meta["material"]) * audit_cfg()["fill_fraction"]
    use_index = len(report.checks)
    report.add(use_stability(mesh, result.meta, estimated_grams))

    plan, checks = plan_print(mesh, result.meta)
    report.checks += checks

    blocked = any(c.status == "FAIL" for c in report.checks)
    if do_slice and plan.chosen.fits and not blocked:
        from .slicer import slice_model

        sliced = report.add(slice_model(name, result.meta, plan, work_dir(name), out))
        if sliced.facts.get("grams"):
            report.checks[use_index] = use_stability(mesh, result.meta, sliced.facts["grams"])
        if (out / f"{name}.3mf").exists():
            report.files["print"] = rel(out / f"{name}.3mf")
    else:
        reason = "--no-slice" if not do_slice else "fix FAILs first" if blocked else "does not fit bed"
        report.add(Check("slice", "SKIP", reason))
        (out / f"{name}.3mf").unlink(missing_ok=True)

    if do_preview:
        from .preview import render

        report.files["preview"] = rel(render(mesh, plan.mesh, out / "preview.png"))
    return report


def cmd_check(args) -> int:
    report = run_check(args.name, do_slice=not args.no_slice, do_preview=not args.no_preview)
    report.write(out_dir(args.name))
    print(report.terminal())
    return 1 if report.verdict == "FAIL" else 0


def cmd_preview(args) -> int:
    from .build import BuildError, build
    from .gravity import plan_print
    from .mesh_check import load_mesh
    from .preview import render

    try:
        result = build(args.name)
    except BuildError as error:
        print(f"build FAIL: {error}")
        return 1
    mesh = load_mesh(result.stl)
    plan, _ = plan_print(mesh, result.meta)
    print(rel(render(mesh, plan.mesh, out_dir(args.name) / "preview.png")))
    return 0


def cmd_list(_args) -> int:
    for path in sorted(MODELS_DIR.glob("*/*/model.py")):
        report = path.parent / "out" / "report.json"
        verdict = json.loads(report.read_text())["verdict"] if report.exists() else "-"
        doc = (path.read_text().split('"""')[1].strip().splitlines() or [""])[0] if '"""' in path.read_text() else ""
        print(f"{path.parent.parent.name + "/" + path.parent.name:<36} {verdict:<5} {doc}")
    return 0


def cmd_materials(_args) -> int:
    from .profiles import PresetError, compatible, flatten, user_index

    cfg = settings()
    machine = cfg["printer"]["machine"]

    def usable(kind: str) -> str:
        names = []
        for name in user_index(kind):
            try:
                if compatible(flatten(kind, name), machine):
                    names.append(name)
            except PresetError:
                names.append(name)
        return "; ".join(names)

    print("materials (META material=):")
    print("  aliases: " + ", ".join(f"{k}={v['filament']}" for k, v in cfg["materials"].items()))
    print("  user presets: " + usable("filament"))
    print("qualities (META quality=):")
    print("  aliases: " + ", ".join(f"{k}={v}" for k, v in cfg["qualities"].items()))
    print("  user presets: " + usable("process"))
    print(f"machine: {machine} (presets for other nozzles hidden)")
    return 0


def cmd_profiles_sync(_args) -> int:
    from .profiles import PresetError, sync_from_bambu

    try:
        imported, skipped = sync_from_bambu()
    except PresetError as error:
        print(error)
        return 1
    print(f"imported {len(imported)} presets into profiles/; skipped {len(skipped)} (not for H2C):")
    for line in skipped:
        print(f"  skip {line}")
    return 0


def cmd_doctor(_args) -> int:
    import build123d
    import trimesh

    print(f"python   {sys.version.split()[0]}")
    print(f"build123d {build123d.__version__}, trimesh {trimesh.__version__}")
    install = slicer_install()
    print(f"slicer   {install.binary if install else 'missing (Linux: scripts/install-slicer.sh)'}")
    print(f"printer  {settings()['printer']['machine']}")
    return 0 if install else 1


def main() -> int:
    parser = argparse.ArgumentParser(prog="./cad", description="Design -> audit -> slice for the Bambu Lab H2C")
    commands = parser.add_subparsers(dest="command", required=True)

    new = commands.add_parser("new", help="scaffold models/<name>/model.py")
    new.add_argument("name", help="kebab-case name, or <category>/<name>")
    new.add_argument("--category", default="misc", help="subfolder of models/ (default: misc)")
    new.set_defaults(run=cmd_new)

    check = commands.add_parser("check", help="build + mesh/walls/gravity audit + orient + slice + preview")
    check.add_argument("name")
    check.add_argument("--no-slice", action="store_true", help="skip slicing (fast geometry iteration)")
    check.add_argument("--no-preview", action="store_true")
    check.set_defaults(run=cmd_check)

    preview = commands.add_parser("preview", help="render out/preview.png only")
    preview.add_argument("name")
    preview.set_defaults(run=cmd_preview)

    commands.add_parser("list", help="models and last verdict").set_defaults(run=cmd_list)
    commands.add_parser("materials", help="filament/process presets usable in META").set_defaults(run=cmd_materials)
    commands.add_parser("profiles-sync", help="import your Bambu Studio user presets (macOS)").set_defaults(
        run=cmd_profiles_sync)
    commands.add_parser("doctor", help="toolchain status").set_defaults(run=cmd_doctor)

    args = parser.parse_args()
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
