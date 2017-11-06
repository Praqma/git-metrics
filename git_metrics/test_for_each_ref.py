from .git import for_each_ref


def test_normal():
    assert for_each_ref() == "git for-each-ref"
