from build123d import Box, Pos

from cadstudio.interference import evaluate


def test_overlap_fails():
    a, b = Box(10, 10, 10), Pos(5, 0, 0) * Box(10, 10, 10)
    assert evaluate([a, b], [], True).status == "FAIL"


def test_gap_in_band_ok():
    a, b = Box(10, 10, 10), Pos(10.3, 0, 0) * Box(10, 10, 10)
    assert evaluate([a, b], [dict(a=0, b=1, clearance=(0.2, 0.6))], True).status == "OK"


def test_gap_out_of_band_warns():
    a, b = Box(10, 10, 10), Pos(11, 0, 0) * Box(10, 10, 10)
    assert evaluate([a, b], [dict(a=0, b=1, clearance=(0.2, 0.6))], True).status == "WARN"
