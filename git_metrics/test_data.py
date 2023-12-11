from .data import columns
from .data import zip_with_tail


def test_single_column():
    assert list(columns(["a", "b"])) == [["a"], ["b"]]


def test_two_columns():
    assert list(columns(["a c", "b d"])) == [["a", "c"], ["b", "d"]]


def test_zip_with_tail():
    assert [(0, 1), (1, 2)] == list(zip_with_tail(range(3)))
