from functools import partial
from subprocess import Popen, PIPE


def mk_run(path_to_git_repo):
    return partial(
        Popen,
        stdout=PIPE,
        cwd=path_to_git_repo,
        universal_newlines=True
    )
