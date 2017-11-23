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

from git_metrics_open_branches import plot_open_branches_metrics, get_branches
from git_metrics_open_branches import commit_author_time_and_branch_ref
from git_metrics_open_branches import send_open_branches_metrics_to_elastic
from git_metrics_release_lead_time import commit_author_time_tag_author_time_and_from_to_tag_name
from git_metrics_release_lead_time import plot_tags


def read_open_branches_csv_file(filename):
    with open(filename) as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        yield from ((int(n), int(t), b) for n, t, b in reader if n.isdigit())


def write_open_branches_csv_file(data):
    writer = csv.writer(sys.stdout, delimiter=',', lineterminator='\n')
    writer.writerow(("query timestamp", "commit timestamp", "branch name"))
    writer.writerows(data)


def write_release_lead_time_csv_file(data):
    writer = csv.writer(sys.stdout, delimiter=',')
    writer.writerows(data)


def main():
    flags = docopt.docopt(__doc__)
    now = int(time.time())
    if flags['<path_to_git_repo>']:
        path_to_git_repo = flags['<path_to_git_repo>']
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
            if flags['--elastic']:
                send_open_branches_metrics_to_elastic(
                    gen,
                    flags['--elastic'],
                    flags['--index']
                )
            else:
                data = ((now, t, b) for t, b in gen)
                if flags['--plot']:
                    repo_name = os.path.basename(os.path.abspath(path_to_git_repo))
                    plot_open_branches_metrics(data, repo_name)
                else:
                    write_open_branches_csv_file(data)
        elif flags["release-lead-time"]:
            pattern = flags['--tag-pattern'] or '*'
            data = commit_author_time_tag_author_time_and_from_to_tag_name(
                run,
                partial(fnmatch, pat=pattern)
            )
            if flags['--plot']:
                plot_tags(data)
            else:
                write_release_lead_time_csv_file(data)
    if flags["plot"]:
        if flags["--open-branches"]:
            plot_open_branches_metrics(
                read_open_branches_csv_file(flags["<csv_file>"]),
                flags["<csv_file>"]
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

