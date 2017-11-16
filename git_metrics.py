"""Calculate age of commits in open remote branches

Usage:
    git_metrics.py open-branches [--master-branch=<branch>] <path_to_git_repo>
    git_metrics.py open-branches [--master-branch=<branch>] --plot <path_to_git_repo>
    git_metrics.py open-branches [--master-branch=<branch>] --elastic=<elastic_url> --index=<elastic_index> <path_to_git_repo>
    git_metrics.py release-lead-time [--tag-pattern=<fn_match>] <path_to_git_repo>
    git_metrics.py release-lead-time --plot [--tag-pattern=<fn_match>] <path_to_git_repo>
    git_metrics.py plot --open-branches <csv_file>
    git_metrics.py (-h | --help)

    Options:
        --master-branch=<branch>    example: origin/gh-pages
"""
import time
from fnmatch import fnmatch
from subprocess import Popen, PIPE
from functools import partial
import csv
import os

import docopt
import sys

import matplotlib
import matplotlib.dates
import numpy as np

from git import for_each_ref, log
from columns import columns


def commit_author_time_and_branch_ref(run, master_branch):
    get_refs = for_each_ref('refs/remotes/origin/**', format='%(refname:short) %(authordate:unix)')
    with run(get_refs) as program:
        for branch, t in columns(program.stdout):
            get_time = log(f"{master_branch}..{branch}", format='%at')
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


def plot_open_branches_metrics(gen, repo_name):
    import matplotlib.pyplot as plt
    from pandas import DataFrame

    now = int(time.time())
    df = DataFrame(gen, columns=("time", "ref"))
    df["age"] = now - df["time"]
    df["age in days"] = df.age // 86400
    unique_refs = df.ref.unique()
    df["ref_id"] = df.ref.map(lambda ref: np.where(unique_refs == ref)[0])
    plt.xticks(
        range(len(unique_refs)),
        unique_refs,
        rotation=40,
        horizontalalignment='right'
    )
    plt.plot(
        df.ref_id,
        df["age in days"],
        'bo',
        label="commit age in days"
    )
    plt.plot(
        range(len(unique_refs)),
        df.groupby("ref")["age in days"].median(),
        'r^',
        label="median commit age in days"
    )
    plt.title(f"Inventory - unmerged commits in {repo_name}")
    plt.tight_layout()
    plt.legend()
    plt.show()


def send_open_branches_metrics_to_elastic(gen, elastic_host, index):
    import requests
    now = int(time.time())
    for t, r in gen:
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


def get_branches(run):
    with run(for_each_ref(format='%(refname)')) as cmd:
        for line in cmd.stdout:
            yield line.strip()


if __name__ == "__main__":
    flags = docopt.docopt(__doc__)
    if flags['<path_to_git_repo>']:
        path_to_git_repo = flags['<path_to_git_repo>']
        repo_name = os.path.basename(os.path.abspath(path_to_git_repo))
        run = partial(
            Popen,
            stdout=PIPE,
            cwd=path_to_git_repo,
            universal_newlines=True
        )
        if flags["open-branches"]:
            master_branch = flags['--master-branch'] or 'origin/master'
            branches = list(get_branches(run))
            if not any(branch.endswith(master_branch) for branch in branches):
                error = partial(print, file=sys.stderr)
                error(f"branch {master_branch} does not exist")
                error()
                error(f"try one of:")
                for branch in branches:
                    error(branch)
                error()
                error("use -h for more help")
                exit(1)
            gen = commit_author_time_and_branch_ref(run, master_branch)
            if flags['--plot']:
                plot_open_branches_metrics(gen, repo_name)
            elif flags['--elastic']:
                send_open_branches_metrics_to_elastic(
                    gen,
                    flags['--elastic'],
                    flags['--index']
                )
            else:
                writer = csv.writer(sys.stdout, delimiter=',')
                writer.writerows(gen)
        elif flags["release-lead-time"]:
            pattern = flags['--tag-pattern'] or '*'
            data = commit_author_time_tag_author_time_and_from_to_tag_name(
                run,
                partial(fnmatch, pat=pattern)
            )
            if flags['--plot']:
                plot_tags(
                    data
                )
            else:
                writer = csv.writer(sys.stdout, delimiter=',')
                writer.writerows(
                    data
                )
    if flags["plot"]:
        if flags["--open-branches"]:
            with open(flags["<csv_file>"]) as csv_file:
                gen = ((int(t), b.strip()) for t, b in csv.reader(csv_file, delimiter=','))
                plot_open_branches_metrics(gen, flags["<csv_file>"])
