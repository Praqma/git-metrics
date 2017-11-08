"""Calculate age of commits in open remote branches

Usage:
    git_metrics.py open-branches <path_to_git_repo>
    git_metrics.py open-branches --plot <path_to_git_repo>
    git_metrics.py open-branches --elastic=<elastic_url> --index=<elastic_index> <path_to_git_repo>
    git_metrics.py (-h | --help)
"""

import time
from subprocess import Popen, PIPE
from functools import partial

import docopt

from git import for_each_ref, log
from columns import columns


def print_to_stdout(run):
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


def plot_it(run):
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
        label="median commit age oin days"
    )
    plt.legend()
    plt.tight_layout()
    plt.show()


def send_to_elastic(run, elastic_host, index):
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


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)
    run = partial(
        Popen,
        stdout=PIPE,
        cwd=arguments['<path_to_git_repo>'],
        universal_newlines=True
    )
    if arguments['--plot']:
        plot_it(run)
    elif arguments['--elastic']:
        send_to_elastic(run, arguments['--elastic'], arguments['--index'])
    else:
        print_to_stdout(run)
