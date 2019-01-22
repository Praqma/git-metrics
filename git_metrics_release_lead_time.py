from itertools import zip_longest
from typing import Tuple, Iterable, List

import matplotlib

from data import columns, zip_with_tail
from git import for_each_ref, show
from git import cherry
from process import proc_to_stdout

TAGS_WITH_AUTHOR_DATE_CMD = for_each_ref(
    'refs/tags/**',
    format='%(refname:short) %(creatordate:unix)',
    sort='taggerdate'
)


def tags_with_author_date(run) -> Iterable[Tuple[str, int]]:
    proc = run(TAGS_WITH_AUTHOR_DATE_CMD)
    stdout = proc_to_stdout(proc)
    return parse_tags_with_author_date(stdout)


def parse_tags_with_author_date(lines: Iterable[str]) -> Iterable[Tuple[str, int]]:
    return ((tag, int(date)) for tag, date in columns(lines))


def diff_of_commits_between(run, upstream: str, head: str) -> Iterable[str]:
    cmd = cherry(upstream, head)
    proc = run(cmd)
    stdout = proc_to_stdout(proc)
    for sign, commit in columns(stdout):
        if sign == '+':
            yield commit


def date_from_git_objects(run, objects: Iterable[str]) -> List[int]:
    cmd = show(objects=objects, diff=False, format='%at')
    proc = run(cmd)
    stdout = proc_to_stdout(proc)
    return list(int(line) for line in stdout)


def commit_author_time_tag_author_time_and_from_to_tag_name(run, match_tag, earliest_date=0):
    tags_and_date = tags_with_author_date(run)
    filtered_on_tags_date = filter(
        lambda p: match_tag(p[0]) and p[1] > earliest_date,
        tags_and_date
    )
    ziped = zip_with_tail(filtered_on_tags_date)
    for (old_tag, old_author_time), (tag, tag_author_time) in ziped:
        commits = diff_of_commits_between(run, old_tag, tag)
        for chunked_commits in zip_longest(*([iter(commits)] * 25)):
            removed_fill_value = filter(lambda x: x is not None, chunked_commits)
            for commit_author_time in date_from_git_objects(run, removed_fill_value):
                yield int(commit_author_time), int(tag_author_time), old_tag, tag


def plot_release_lead_time_metrics(data):
    import matplotlib.pyplot as plt
    from pandas import DataFrame

    df = DataFrame(data, columns=("commit_time", "tag_time", "from_tag", "tag", "repo_name"))
    repo_name = df["repo_name"][0]
    df["age"] = df["tag_time"] - df["commit_time"]
    df["label"] = df["from_tag"] + '..' + df["tag"]
    df["tag_date"] = matplotlib.dates.epoch2num(df["tag_time"])
    df["age in days"] = df.age // 86400
    tmp = df[df["tag"] < "REL-4.4.10"]
    df = df.sort_values('tag_time')
    fig, ax = plt.subplots()
    plt.plot_date(
        df["tag_date"],
        df["age in days"],
        'bo',
        label="commit age in days"
    )
    plt.plot_date(
        df["tag_date"].unique(),
        df.groupby("tag_date")["age in days"].median(),
        'r^',
        label="median commit age in days",

    )
    for tag_date, group in df.groupby("tag_date"):
        ax.annotate(
            group["label"].max(),
            (tag_date, group["age in days"].max() + 5),
            horizontalalignment='center',
            verticalalignment='bottom',
            rotation=90
        )
    plt.legend()
    plt.tight_layout()
    plt.title(repo_name)
    plt.show()