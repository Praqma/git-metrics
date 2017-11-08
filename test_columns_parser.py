from columns import columns


def test_single_column():
    assert list(columns(["a", "b"])) == [["a"], ["b"]]


def test_two_columns():
    assert list(columns(["a c", "b d"])) == [["a", "c"], ["b", "d"]]
