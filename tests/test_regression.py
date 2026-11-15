from cadstudio.__main__ import run_check


def verdict(name):
    return run_check(name, do_slice=False, do_preview=False)


def status_of(report, check):
    return next(c.status for c in report.checks if c.name == check)


def test_good_box_passes(models_dir):
    report = verdict("good-box")
    assert report.verdict == "PASS", report.terminal()
    assert status_of(report, "status") == "OK"
    assert status_of(report, "walls") != "FAIL"


def test_thin_wall_fails(models_dir):
    report = verdict("bad-thin-wall")
    assert report.verdict == "FAIL", report.terminal()
    assert any(c.status == "FAIL" and "wall" in c.name for c in report.checks)


def test_overhang_slab_flagged(models_dir):
    report = verdict("bad-overhang-slab")
    flagged = [c for c in report.checks if c.status in ("WARN", "FAIL") and c.name != "slice"]
    assert flagged, report.terminal()


def test_models_dir_untouched(models_dir):
    from pathlib import Path

    assert not list((Path(__file__).parent.parent / "models").glob("ref"))
