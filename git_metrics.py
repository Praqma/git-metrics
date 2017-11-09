"""Calculate age of commits in open remote branches

Usage:
    git_metrics.py open-branches <path_to_git_repo>
    git_metrics.py open-branches --plot <path_to_git_repo>
    git_metrics.py open-branches --elastic=<elastic_url> --index=<elastic_index> <path_to_git_repo>
    git_metrics.py release-lead-time [--tag-pattern=<fn_match>] <path_to_git_repo>
    git_metrics.py release-lead-time --plot [--tag-pattern=<fn_match>] <path_to_git_repo>
    git_metrics.py (-h | --help)
"""
import time
from fnmatch import fnmatch
from subprocess import Popen, PIPE
from functools import partial
import csv

import docopt
import sys

import matplotlib
import matplotlib.dates

from git import for_each_ref, log
from columns import columns


def print_open_branches_metrics(run):
    now = int(time.time())
    for author_time, ref in commit_author_time_and_branch_ref(run):
        print(f"{now - int(author_time)}, {ref}")


def commit_author_time_and_branch_ref(run):
    get_refs = for_each_ref('refs/remotes/origin/**', format='%(refname:short) %(authordate:unix)')
    with run(get_refs) as program:
        for branch, t in columns(program.stdout):
            get_time = log(f"origin/master..{branch}", format='%at')
            with run(get_time) as inner_program:
                for author_time, in columns(inner_program.stdout):
                    yield int(author_time), branch


def commit_author_time_tag_author_time_and_from_to_tag_name(run, match_tag):
    get_refs = for_each_ref(
        'refs/tags/**',
        format='%(refname:short) %(*authordate:unix)%(authordate:unix)',
        sort='v:refname'
    )
    with run(get_refs) as program:
        tag_and_time = filter(lambda p: match_tag(p[0]), columns(program.stdout))
        old_tag, old_author_time = next(tag_and_time)
        for tag, tag_author_time in tag_and_time:
            get_time = log(f"refs/tags/{old_tag}..refs/tags/{tag}", format='%at')
            with run(get_time) as inner_program:
                for commit_author_time, in columns(inner_program.stdout):
                    yield int(commit_author_time), int(tag_author_time), old_tag, tag
            old_tag, old_author_time = tag, tag_author_time


def plot_open_branches_metrics(run):
    import matplotlib.pyplot as plt
    from pandas import DataFrame

    now = int(time.time())
    gen = commit_author_time_and_branch_ref(run)
    df = DataFrame(gen, columns=("time", "ref"))
    df["age"] = now - df["time"]
    df["age in days"] = df.age // 86400
    plt.xticks(rotation=40, horizontalalignment='right')
    plt.plot(
        df.ref,
        df["age in days"],
        'bo',
        label="commit age in days"
    )
    plt.plot(
        df.ref.unique(),
        df.groupby("ref")["age in days"].median(),
        'r^',
        label="median commit age in days"
    )
    plt.legend()
    plt.tight_layout()
    plt.show()


def send_open_branches_metrics_to_elastic(run, elastic_host, index):
    import requests
    now = int(time.time())
    for t, r in commit_author_time_and_branch_ref(run):
        age = (now - t)
        requests.post(
            f"http://{elastic_host}/{index}/open_branches",
            json={
                'git_ref': r,
                'time': t,
                'time_in_days': t // 86400,
                'age': age,
                'age_in_days': age // 86400
            }
        )


def plot_tags(data):
    import matplotlib.pyplot as plt
    from pandas import DataFrame

    df = DataFrame(data, columns=("commit_time", "tag_time", "from_tag", "tag"))
    df["age"] = df["tag_time"] - df["commit_time"]
    df["label"] = df["from_tag"] + '..' + df["tag"]
    df["tag_date"] = matplotlib.dates.epoch2num(df["tag_time"])
    df["age in days"] = df.age // 86400
    tmp = df[df["tag"] < "REL-4.4.10"]
    age_in_days_ = tmp["age in days"]
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
    plt.show()


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)
    run = partial(
        Popen,
        stdout=PIPE,
        cwd=arguments['<path_to_git_repo>'],
        universal_newlines=True
    )
    if arguments["open-branches"]:
        if arguments['--plot']:
            plot_open_branches_metrics(run)
        elif arguments['--elastic']:
            send_open_branches_metrics_to_elastic(run, arguments['--elastic'], arguments['--index'])
        else:
            print_open_branches_metrics(run)
    else:
        pattern = arguments['--tag-pattern'] or '*'
        data = commit_author_time_tag_author_time_and_from_to_tag_name(
            run,
            partial(fnmatch, pat=pattern)
        )
        if arguments['--plot']:
            plot_tags(
                data
            )
        else:
            writer = csv.writer(sys.stdout, delimiter=',')
            writer.writerows(
                data
            )
