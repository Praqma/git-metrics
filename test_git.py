from git import for_each_ref, cherry
from git import log


def test_for_each_ref_normal():
    assert for_each_ref() == ["git", "for-each-ref"]


def test_for_each_ref_ref_glob():
    assert for_each_ref('refs/heads/*') == [
        "git",
        "for-each-ref",
        "refs/heads/*"
    ]


def test_for_each_ref_format():
    assert for_each_ref(format='%(authordate:unix)') == [
        "git",
        "for-each-ref",
        "--format=%(authordate:unix)"
    ]


def test_for_each_ref_sort():
    assert for_each_ref(sort='v:refname') == [
        "git",
        "for-each-ref",
        "--sort=v:refname"
    ]


def test_log_normal():
    assert log() == [
        "git",
        "log"
    ]


def test_log_selector():
    assert log('selector') == [
        "git",
        "log",
        "selector"
    ]


def test_log_format():
    assert log(format='%a') == [
        "git",
        "log",
        "--format=%a"
    ]


def test_cherry():
    assert cherry() == [
        "git",
        "cherry"
    ]


def test_cherry_upstream_and_head_arguments():
    assert cherry(upstream="<upstream>", head="<head>") == [
        "git",
        "cherry",
        "<upstream>",
        "<head>"
    ]
