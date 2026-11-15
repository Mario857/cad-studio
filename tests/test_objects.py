import pytest

from cadlib import list_objects, obj
from cadlib.fasteners import METRIC
from cadlib.objects import STATUSES


def test_lookup_and_dims():
    assert obj("aa-battery")["d"] == 14.5
    assert obj("AA Battery").name == "aa-battery"


def test_unknown_lists_close_names():
    with pytest.raises(KeyError, match="aa-battery"):
        obj("aa-batery")


def test_all_entries_valid():
    for o in list_objects():
        assert o.status in STATUSES and o.source and o.dims
        assert all(isinstance(v, (int, float)) and v > 0 for v in o.dims.values())


def test_fasteners_match_metric():
    for size, s in METRIC.items():
        assert obj(f"{size}-screw")["head_d"] == s["head_d"]


def test_query_and_unverified():
    assert "eur-2-coin" in {o.name for o in list_objects("coin")}
    assert obj("curtain-rod").status == "UNVERIFIED"
