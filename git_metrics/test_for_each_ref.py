from git_metrics.git import for_each_ref


def test_normal():
    assert for_each_ref() == ["git", "for-each-ref"]


def test_ref_glob():
    assert for_each_ref('refs/heads/*') == [
        "git",
        "for-each-ref",
        "refs/heads/*"
    ]


def test_format():
    assert for_each_ref(format='%(authordate:unix)') == [
        "git",
        "for-each-ref",
        "--format=%(authordate:unix)"
    ]
