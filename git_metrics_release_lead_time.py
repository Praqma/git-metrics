from typing import Tuple, Iterable

import matplotlib

from columns import columns
from git import for_each_ref, log
from process import proc_to_stdout

TAGS_WITH_AUTHOR_DATE_CMD = for_each_ref(
    'refs/tags/**',
    format='%(refname:short) %(*authordate:unix)%(authordate:unix)',
    sort='v:refname'
)


def tags_with_author_date(run) -> Iterable[Tuple[str, int]]:
    proc = run(TAGS_WITH_AUTHOR_DATE_CMD)
    stdout = proc_to_stdout(proc)
    return parse_tags_with_author_date(stdout)


def parse_tags_with_author_date(lines: Iterable[str]) -> Iterable[Tuple[str, int]]:
    return ((tag, int(date)) for tag, date in columns(lines))


def commit_author_time_tag_author_time_and_from_to_tag_name(run, match_tag, earliest_date=0):
    with run(TAGS_WITH_AUTHOR_DATE_CMD) as program:
        tag_and_time = filter(lambda p: match_tag(p[0]), columns(program.stdout))
        old_tag, old_author_time = next(tag_and_time)
        for tag, tag_author_time in tag_and_time:
            get_time = log(f"refs/tags/{old_tag}..refs/tags/{tag}", format='%at')
            with run(get_time) as inner_program:
                for commit_author_time, in columns(inner_program.stdout):
                    if int(tag_author_time) > earliest_date:
                        yield int(commit_author_time), int(tag_author_time), old_tag, tag
            old_tag, old_author_time = tag, tag_author_time


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