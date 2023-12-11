import os
from subprocess import Popen, PIPE

from .process import proc_to_stdout


def test_proc_to_pocess():
    proc = Popen(
        ['echo', 'hello world'],
        stdout=PIPE,
        universal_newlines=True,
        shell=(os.name == 'nt')
    )
    assert list(line.strip('"\n') for line in proc_to_stdout(proc)) == ['hello world']
