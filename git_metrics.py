"""Calculate age of commits in open remote branches

Usage:
    git_metrics.py open-branches [--master-branch=<branch>] <path_to_git_repo>
    git_metrics.py open-branches [--master-branch=<branch>] --plot <path_to_git_repo>
    git_metrics.py release-lead-time [--tag-pattern=<fn_match>] [--earliest-date=<timestamp>] <path_to_git_repo>
    git_metrics.py release-lead-time --plot [--tag-pattern=<fn_match>] <path_to_git_repo>
    git_metrics.py plot --open-branches [--repo-name=<repo_name>] <csv_file>
    git_metrics.py plot --release-lead-time [--repo-name=<repo_name>] <csv_file>
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

from git_metrics_open_branches import plot_open_branches_metrics
from git_metrics_open_branches import get_branches
from git_metrics_open_branches import commit_author_time_and_branch_ref
from git_metrics_release_lead_time import commit_author_time_tag_author_time_and_from_to_tag_name
from git_metrics_release_lead_time import plot_release_lead_time_metrics


def read_open_branches_csv_file(filename):
    with open(filename) as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        yield from ((int(n), int(t), b) for n, t, b in reader if n.isdigit())


def write_open_branches_csv_file(data):
    writer = csv.writer(sys.stdout, delimiter=',', lineterminator='\n')
    writer.writerow(("query timestamp", "commit timestamp", "branch name"))
    writer.writerows(data)

def read_release_lead_time_csv_file(filename):
    with open(filename) as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        yield from ((int(n), int(t), tag1, tag2) for n, t, tag1, tag2 in reader if n.isdigit())

def write_release_lead_time_csv_file(data):
    writer = csv.writer(sys.stdout, delimiter=',', lineterminator='\n')
    writer.writerow(("commit timestamp", "tag timestamp", "previous release tag", "release tag"))
    writer.writerows(data)

#1451297815.853977

def main():
    flags = docopt.docopt(__doc__)
    now = int(time.time())
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
            assert_master_branch(run, master_branch)
            gen = commit_author_time_and_branch_ref(run, master_branch)
            data = ((now, t, b) for t, b in gen)
            if flags['--plot']:
                plot_open_branches_metrics(data, repo_name)
            else:
                write_open_branches_csv_file(data)
        elif flags["release-lead-time"]:
            earliest_date = flags["--earliest-date"]
            pattern = flags['--tag-pattern'] or '*'
            data = commit_author_time_tag_author_time_and_from_to_tag_name(
                run,
                partial(fnmatch, pat=pattern),
                earliest_date,
            )
            if flags['--plot']:
                plot_release_lead_time_metrics(data, repo_name)
            else:
                write_release_lead_time_csv_file(data)
    if flags["plot"]:
        repo_name = flags['--repo-name']
        if flags["--open-branches"]:
            data = read_open_branches_csv_file(flags["<csv_file>"])
            plot_open_branches_metrics(data, flags["<csv_file>"])
        elif flags["--release-lead-time"]:
            data = read_release_lead_time_csv_file(flags["<csv_file>"])
            plot_release_lead_time_metrics(data, repo_name)


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

