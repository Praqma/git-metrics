from data import columns
from git import for_each_ref, log


def plot_open_branches_metrics(data):
    import numpy as np
    import matplotlib.pyplot as plt
    from pandas import DataFrame

    df = DataFrame(data, columns=("now", "time", "ref", "repo_name"))
    repo_name = df["repo_name"][0]
    df["age"] = df["now"] - df["time"]
    df["age in days"] = df.age // 86400
    unique_refs = df.ref.unique()
    df["ref_id"] = df.ref.map(lambda ref: np.where(unique_refs == ref)[0])
    plt.xticks(
        range(len(unique_refs)),
        unique_refs,
        rotation=40,
        horizontalalignment='right'
    )
    plt.plot(
        df.ref_id,
        df["age in days"],
        'bo',
        label="commit age in days"
    )
    plt.plot(
        range(len(unique_refs)),
        df.groupby("ref")["age in days"].median(),
        'r^',
        label="median commit age in days"
    )
    plt.title(f"Inventory - unmerged commits in {repo_name}")
    plt.tight_layout()
    plt.legend()
    plt.show()


def commit_author_time_and_branch_ref(run, master_branch):
    get_refs = for_each_ref('refs/remotes/origin/**', format='%(refname:short) %(authordate:unix)')
    with run(get_refs) as program:
        for branch, t in columns(program.stdout):
            get_time = log(f"{master_branch}..{branch}", format='%at')
            with run(get_time) as inner_program:
                for author_time, in columns(inner_program.stdout):
                    yield int(author_time), branch


def get_branches(run):
    with run(for_each_ref(format='%(refname)')) as cmd:
        for line in cmd.stdout:
            yield line.strip()
