from collections import namedtuple
from contextlib import contextmanager

from git_metrics_release_lead_time import parse_tags_with_date
from git_metrics_release_lead_time import tags_with_author_date
from git_metrics_release_lead_time import fetch_tags_and_sha
import git_metrics_release_lead_time


def test_parse_tags_with_author_date():
    out = parse_tags_with_date(["refs/tags/VER-1.0.0 18298732"])
    assert [("refs/tags/VER-1.0.0", 18298732)] == list(out)


def test_tags_with_author_date(monkeypatch):
    monkeypatch.setattr(
        git_metrics_release_lead_time,
        "parse_tags_with_date",
        lambda x: [("refs/tags/VER-1.0.0", 18298732)]
    )
    out = tags_with_author_date(lambda cmd: None)
    assert [("refs/tags/VER-1.0.0", 18298732)] == list(out)


def stdout(lines):
    @contextmanager
    def context():
        yield namedtuple("proc", ["stdout"])(lines)
    return context()


def test_fetch_tags_and_sha():
    result = fetch_tags_and_sha(lambda _: stdout([
        "annotated-tag sha",
        "lightweight-tag"
    ]), lambda _: True)
    assert list(result) == [
        ("annotated-tag", "sha")
    ]