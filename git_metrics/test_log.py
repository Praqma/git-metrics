from git_metrics.git import log


def test_normal():
    assert log() == [
        "git",
        "log"
    ]


def test_selector():
    assert log('selector') == [
        "git",
        "log",
        "selector"
    ]


def test_format():
    assert log(format='%a') == [
        "git",
        "log",
        "--format=%a"
    ]
