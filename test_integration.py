import os
import subprocess
import tempfile

import pytest
from git import Repo

from calculate_four_metrics import calculate_lead_time


@pytest.fixture
def git_repo(repo_dir):
    r = Repo.init(repo_dir)
    yield r

@pytest.fixture
def repo_dir():
    repo_dir = tempfile.mkdtemp()
    return repo_dir


@pytest.fixture
def git_repo_DDDP(git_repo):
    create_and_commit_file(git_repo, "file_zero", "initial commit", "Thu Jan 24 10:18:00 2019 +0100")
    create_tag_with_date(git_repo, 'D-0.0.0', '0.0.0 deploy tag', "Thu Jan 24 10:19:00 2019 +0100")
    create_and_commit_file(git_repo, "file_one", "second commit", "Thu Jan 24 10:20:00 2019 +0100")
    create_tag_with_date(git_repo, 'D-0.0.1', '0.0.1 deploy tag', "Thu Jan 24 10:21:00 2019 +0100")
    create_and_commit_file(git_repo, "file_two", "third commit", "Thu Jan 24 10:22:00 2019 +0100")
    create_tag_with_date(git_repo, 'D-0.0.2', '0.0.2 deploy tag', "Thu Jan 24 10:26:00 2019 +0100")
    git_repo.create_tag("P-0.0.2", message="0.0.2 patch tag")
    print(subprocess.run(['git', 'tag'], cwd=git_repo.working_dir))
    print(subprocess.run(['git', 'log'], cwd=git_repo.working_dir))
    yield git_repo


def create_and_commit_file(git_repo, file_name, message, commmiterdate):
    # This function just creates an empty file ...
    open(os.path.join(git_repo.working_dir, file_name), 'wb').close()
    git_repo.index.add([file_name])
    command = ['git', 'commit', '-m', message]
    result = subprocess.run(command, cwd=git_repo.working_dir, env={"GIT_AUTHOR_DATE": commmiterdate})
    print(result)


def create_tag_with_date(git_repo, tag, message, taggerdate):
    command = ['git', 'tag', '-m', message, tag]
    result = subprocess.run(command, cwd=git_repo.working_dir, env={"GIT_COMMITTER_DATE": taggerdate})
    print(result)


def test_lead_time(git_repo_DDDP):
    mean_lead_time = calculate_lead_time(git_repo_DDDP.working_dir, "D-*", 0)
    # First commit is ignored.
    # Time from second commit to 0.0.1 release is 60 seconds.
    # Time from third commit to 0.0.2 release is 240 seconds.
    # Mean lead time is (60 + 240) / 2
    assert mean_lead_time == 150