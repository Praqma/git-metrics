"""Calculate age of commits in open remote branches

Usage:
    open_branches.py <path_to_git_repo>
    open_branches.py (-h | --help)
"""

import time
from subprocess import Popen, PIPE
from functools import partial

import docopt

from git_metrics.git import for_each_ref, log
from git_metrics.parser import columns


def main(run):
    now = int(time.time())
    for author_time, ref in commit_author_time_and_branch_ref(run):
        print(f"{now - int(author_time)}, {ref}")


def commit_author_time_and_branch_ref(run):
    get_refs = for_each_ref('refs/remotes/origin/**', format='%(refname) %(authordate:unix)')
    with run(get_refs) as program:
        for branch, t in columns(program.stdout):
            get_time = log(f"origin/master..{branch}", format='%at')
            with run(get_time) as inner_program:
                for author_time, in columns(inner_program.stdout):
                    yield author_time, branch


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)
    main(partial(
        Popen,
        stdout=PIPE,
        cwd=arguments['<path_to_git_repo>'],
        universal_newlines=True
    ))
