import subprocess

import time
import sys

from git_metrics.git import for_each_ref, log
from git_metrics.parser import columns, decode
cwd = sys.argv[1]


def run(cmd):
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        cwd=cwd
    )


now = int(time.time())
get_refs = for_each_ref('refs/remotes/origin/*', format='%(refname) %(authordate:unix)')

with run(get_refs) as pipe:
    for branch, t in columns(decode(pipe.stdout)):
        get_time = log(f"origin/master..{branch}", format='%at')
        with run(get_time) as inner_pipe:
            for author_time, in columns(decode(inner_pipe.stdout)):
                print(f"{now - int(author_time)}, {branch}")

