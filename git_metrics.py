"""Calculate age of commits in open remote branches

Usage:
    git_metrics.py open-branches [--master-branch=<branch>] <path_to_git_repo>
    git_metrics.py open-branches [--master-branch=<branch>] --plot <path_to_git_repo>
    git_metrics.py release-lead-time [--tag-pattern=<fn_match>] [--earliest-date=<timestamp>] <path_to_git_repo>
    git_metrics.py release-lead-time --plot [--tag-pattern=<fn_match>] <path_to_git_repo>
    git_metrics.py plot --open-branches <csv_file>
    git_metrics.py plot --release-lead-time <csv_file>
    git_metrics.py batch --open-branches <path_to_git_repos>...
    git_metrics.py (-h | --help)

    Options:
        --master-branch=<branch>    example: origin/gh-pages
"""
import time
from fnmatch import fnmatch
from itertools import chain
from subprocess import Popen, PIPE
from functools import partial
import csv
import os

import docopt
import sys

from git_metrics_open_branches import plot_open_branches_metrics
from git_metrics_open_branches import get_branches
from git_metrics_open_branches import commit_author_time_and_branch_ref
from git_metrics_release_lead_time import commit_author_time_tag_author_time_and_from_to_tag_name
from git_metrics_release_lead_time import plot_release_lead_time_metrics


def read_open_branches_csv_file(filename):
    with open(filename) as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        yield from ((int(n), int(t), b, repo_name) for n, t, b, repo_name in reader if n.isdigit())


def write_open_branches_csv_file(data):
    writer = csv.writer(sys.stdout, delimiter=',', lineterminator='\n')
    writer.writerow(("query timestamp", "commit timestamp", "branch name", "repo name"))
    writer.writerows(data)


def read_release_lead_time_csv_file(filename):
    with open(filename) as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        yield from ((int(n), int(t), tag1, tag2, repo_name) for n, t, tag1, tag2, repo_name in reader if n.isdigit())


def write_release_lead_time_csv_file(data):
    writer = csv.writer(sys.stdout, delimiter=',', lineterminator='\n')
    writer.writerow(("commit timestamp", "tag timestamp", "previous release tag", "release tag", "repo name"))
    writer.writerows(data)


def main():
    flags = docopt.docopt(__doc__)
    now = int(time.time())
    if flags['<path_to_git_repo>']:
        path_to_git_repo = flags['<path_to_git_repo>']
        repo_name = os.path.basename(os.path.abspath(path_to_git_repo))
        run = mk_run(path_to_git_repo)
        if flags["open-branches"]:
            master_branch = flags['--master-branch'] or 'origin/master'
            assert_master_branch(run, master_branch)
            gen = commit_author_time_and_branch_ref(run, master_branch)
            data = ((now, t, b, repo_name) for t, b in gen)
            if flags['--plot']:
                plot_open_branches_metrics(data)
            else:
                write_open_branches_csv_file(data)
        elif flags["release-lead-time"]:
            earliest_date = int(flags["--earliest-date"] or 0)
            pattern = flags['--tag-pattern'] or '*'
            data = commit_author_time_tag_author_time_and_from_to_tag_name(
                run,
                partial(fnmatch, pat=pattern),
                earliest_date,
            )
            gen = ((cat, tat, old_tag, tag, repo_name ) for cat, tat, old_tag, tag in data)
            if flags['--plot']:
                plot_release_lead_time_metrics(gen)
            else:
                write_release_lead_time_csv_file(gen)
    if flags["plot"]:
        if flags["--open-branches"]:
            data = read_open_branches_csv_file(flags["<csv_file>"])
            plot_open_branches_metrics(data)
        elif flags["--release-lead-time"]:
            data = read_release_lead_time_csv_file(flags["<csv_file>"])
            plot_release_lead_time_metrics(data)
    elif flags["batch"] and flags["--open-branches"]:
        for path_to_git_repo in flags['<path_to_git_repos>']:
            print("checking master branch in repo:", path_to_git_repo, file=sys.stderr)
            run = mk_run(path_to_git_repo)
            assert_master_branch(run, 'origin/master')
        data = []
        for path_to_git_repo in flags['<path_to_git_repos>']:
            print("fetching data from in repo:", path_to_git_repo, file=sys.stderr)
            repo_name = os.path.basename(os.path.abspath(path_to_git_repo))
            run = mk_run(path_to_git_repo)
            gen = commit_author_time_and_branch_ref(run, 'origin/master')
            data.extend((now, t, b, repo_name) for t, b in gen)
        write_open_branches_csv_file(data)


def mk_run(path_to_git_repo):
    return partial(
        Popen,
        stdout=PIPE,
        cwd=path_to_git_repo,
        universal_newlines=True
    )


def assert_master_branch(run, master_branch):
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


if __name__ == "__main__":
    main()

