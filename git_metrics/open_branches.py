import subprocess

import time
import sys

from git_metrics.git import for_each_ref, log
from git_metrics.parser import columns
cwd = sys.argv[1]


def run(cmd):
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        cwd=cwd,
        universal_newlines=True
    )


now = int(time.time())
get_refs = for_each_ref('refs/remotes/origin/**', format='%(refname) %(authordate:unix)')
with run(get_refs) as program:
    for branch, t in columns(program.stdout):
        get_time = log(f"origin/master..{branch}", format='%at')
        with run(get_time) as inner_program:
            for author_time, in columns(inner_program.stdout):
                print(f"{now - int(author_time)}, {branch}")

