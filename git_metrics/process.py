from functools import partial
from subprocess import Popen, PIPE
from typing import Iterable


def mk_run(path_to_git_repo):
    return partial(
        Popen,
        stdout=PIPE,
        cwd=path_to_git_repo,
        universal_newlines=True
    )


def proc_to_stdout(proc) -> Iterable[str]:
    with proc as p:
        yield from p.stdout