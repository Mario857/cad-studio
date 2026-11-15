"""./cad calibrate | calibration | coupon: per-material printer offsets and fit-gauge scaffolds."""

from __future__ import annotations

import re
import tomllib

from .config import MODELS_DIR, REPO, model_dir

CALIBRATION_FILE = REPO / "config" / "calibration.toml"
TEMPLATES = REPO / "templates"
KEBAB = re.compile(r"[a-z0-9][a-z0-9-]*")
HEADER = (
    "# Per-material measured offsets (mm), written by `./cad calibration`; read by cadlib.fit.\n"
    "# hole_offset: added by hole_d()/clearance(). wall_offset: added by wall_t().\n"
)


def _rel(path) -> str:
    return str(path.relative_to(REPO))


def _scaffold(template: str, target, **fields) -> int:
    if target.exists():
        print(f"exists: {_rel(target)}")
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    text = (TEMPLATES / template).read_text()
    for key, value in fields.items():
        text = text.replace("{{" + key + "}}", value)
    target.write_text(text)
    print(f"created {_rel(target)}")
    return 0


def cmd_calibrate(_args) -> int:
    rc = _scaffold("calibration_coupon.py", MODELS_DIR / "misc" / "calibration-coupon" / "model.py")
    print("next: set META material, ./cad check calibration-coupon, print, measure, ./cad calibration <material> ...")
    return rc


def load_calibration(path=CALIBRATION_FILE) -> dict:
    if not path.exists():
        return {}
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _quote(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_calibration(data: dict, path=CALIBRATION_FILE) -> None:
    lines = [HEADER]
    for material in sorted(data):
        lines.append(f"\n[{_quote(material)}]")
        for key, value in data[material].items():
            lines.append(f"{key} = {_quote(value) if isinstance(value, str) else value}")
    path.write_text("\n".join(lines) + "\n")


def record(data: dict, material: str, hole=None, wall=None, note=None, absolute=False) -> dict:
    """Return `data` with the material's offsets updated (residuals accumulate unless `absolute`)."""
    entry = dict(data.get(material, {}))
    for key, value in (("hole_offset", hole), ("wall_offset", wall)):
        if value is not None:
            entry[key] = round(value if absolute else entry.get(key, 0.0) + value, 4)
    if note:
        entry["note"] = note
    return {**data, material: entry}


def cmd_calibration(args) -> int:
    from .profiles import PresetError, resolve_material

    if args.hole_offset is None and args.wall_offset is None:
        data = load_calibration()
        for material, entry in sorted(data.items()):
            print(f"{material}: " + ", ".join(f"{k}={v}" for k, v in entry.items()))
        if not data:
            print("no calibration recorded (see ./cad calibrate)")
        return 0
    try:
        material, _ = resolve_material(args.material)
    except PresetError as error:
        print(error)
        return 2
    data = record(load_calibration(), material, args.hole_offset, args.wall_offset, args.note, args.set)
    write_calibration(data)
    print(f"{_rel(CALIBRATION_FILE)}: {material}: " + ", ".join(f"{k}={v}" for k, v in data[material].items()))
    return 0


def add_commands(commands) -> None:
    commands.add_parser("calibrate", help="scaffold models/misc/calibration-coupon").set_defaults(run=cmd_calibrate)
    cal = commands.add_parser("calibration", help="record measured per-material offsets (config/calibration.toml)")
    cal.add_argument("material", nargs="?", default="PLA")
    cal.add_argument("--hole-offset", type=float, help="mm to add to holes (nominal - measured)")
    cal.add_argument("--wall-offset", type=float, help="mm to add to pegs/walls (nominal - measured)")
    cal.add_argument("--note")
    cal.add_argument("--set", action="store_true", help="overwrite instead of accumulating")
    cal.set_defaults(run=cmd_calibration)
    coupon = commands.add_parser("coupon", help="scaffold models/<cat>/<name>-fit-gauge (graded-size test)")
    coupon.add_argument("name")
    coupon.add_argument("--feature", required=True, help="what the gauge tests")
    coupon.add_argument("--category", help="default: the model's own category, else misc")
    coupon.set_defaults(run=cmd_coupon)


def cmd_coupon(args) -> int:
    if not KEBAB.fullmatch(args.name):
        print("name must be kebab-case: lowercase letters, digits, dashes")
        return 2
    existing = model_dir(args.name)
    category = args.category or (existing.parent.name if (existing / "model.py").exists() else "misc")
    name = f"{args.name}-fit-gauge"
    if list(MODELS_DIR.glob(f"*/{name}/model.py")):
        print(f"exists: {name}")
        return 1
    rc = _scaffold("fit_gauge.py", MODELS_DIR / category / name / "model.py", NAME=name, FEATURE=args.feature)
    if rc == 0:
        print(f"next: set NOMINAL/STEP/COUNT, replace test_cutter(), ./cad check {name} --no-slice")
    return rc
