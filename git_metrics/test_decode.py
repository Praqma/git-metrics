from git_metrics.parser import decode


def test_single_byte_string():
    assert list(decode([b'a'])) == ["a"]
