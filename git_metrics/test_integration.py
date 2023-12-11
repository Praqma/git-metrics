import os
import subprocess
import tempfile

import pytest
from git import Repo

from .calculate_four_metrics import calculate_lead_time, calculate_deploy_interval, calculate_change_fail_rate, \
    calculate_MTTR


@pytest.fixture(scope="session")
def git_repo(repo_dir):
    r = Repo.init(repo_dir)
    yield r

@pytest.fixture(scope="session")
def repo_dir():
    repo_dir = tempfile.mkdtemp()
    return repo_dir


@pytest.fixture(scope="session")
def git_repo_DDDP(git_repo):
    create_and_commit_file(git_repo, "file_zero", "initial commit", "Thu Jan 24 10:17:00 2019 +0100")
    create_tag_with_date(git_repo, 'D-0.0.0', '0.0.0 deploy tag', "Thu Jan 24 10:18:00 2019 +0100")
    create_and_commit_file(git_repo, "file_one", "second commit", "Thu Jan 24 10:20:00 2019 +0100")
    create_tag_with_date(git_repo, 'D-0.0.1', '0.0.1 deploy tag', "Thu Jan 24 10:21:00 2019 +0100")
    create_and_commit_file(git_repo, "file_two", "third commit", "Thu Jan 24 10:22:00 2019 +0100")
    create_and_commit_file(git_repo, "file_three", "fourth commit", "Thu Jan 24 10:24:00 2019 +0100")
    create_tag_with_date(git_repo, 'D-0.0.2', '0.0.2 deploy tag', "Thu Jan 24 10:26:00 2019 +0100")
    create_tag_with_date(git_repo, "P-0.0.2", "0.0.2 patch tag", "Fri Jan 25 10:00:00 2019 +0100")
    yield git_repo


def create_and_commit_file(git_repo, file_name, message, commmiterdate):
    # This function just creates an empty file ...
    open(os.path.join(git_repo.working_dir, file_name), 'wb').close()
    git_repo.index.add([file_name])
    command = ['git', 'commit', '-m', message]
    _run_git_cmd(git_repo, command, {"GIT_AUTHOR_DATE": commmiterdate})


def create_tag_with_date(git_repo, tag, message, taggerdate):
    command = ['git', 'tag', '-m', message, tag]
    _run_git_cmd(git_repo, command, {"GIT_COMMITTER_DATE": taggerdate})

def _run_git_cmd(git_repo, command, environment):
    env_variables = {"GIT_COMMITTER_EMAIL": "test@example.com",
                    "GIT_COMMITTER_NAME": "Integration Test",
                    "GIT_AUTHOR_EMAIL": "test@example.com",
                    "GIT_AUTHOR_NAME": "Integration Test",
                    "EMAIL": "test@example.com"}
    env_variables.update(environment)
    subprocess.run(command, cwd=git_repo.working_dir,
        env=env_variables)


def test_lead_time_multiple_deploys(git_repo_DDDP):
    mean_lead_time = calculate_lead_time(git_repo_DDDP.working_dir, "D-*", 1548321540)
    # First commit is before earliest date.
    # Time from second commit to 0.0.1 release is 60 seconds.
    # Time from third commit to 0.0.2 release is 240 seconds.
    # Time from fourth commit to 0.0.2 release is 120 seconds.
    # Mean lead time is (60 + 240 + 120) / 3
    assert mean_lead_time == 140


def test_lead_time_single_deploy(git_repo_DDDP):
    mean_lead_time = calculate_lead_time(git_repo_DDDP.working_dir, "D-*", 1548321660)
    # First commit is before earliest date.
    # Second commit is before earliest date.
    # Time from third commit to 0.0.2 release is 240 seconds.
    # Time from fourth commit to 0.0.2 release is 120 seconds.
    # Mean lead time is (240 + 120) / 2
    assert mean_lead_time == 180


def test_calculate_deploy_interval(git_repo_DDDP):
    interval_end = 1548322020 # Thu, 24 Jan 2019 10:27:00 CET in epoch time
    interval_length = 600 # 10 minutes
    interval = calculate_deploy_interval(git_repo_DDDP.working_dir, "D-*", interval_end - interval_length, interval_end)
    # Three deployments within the interval so deployment interval is 600 seconds divided by three
    assert interval == 200


def test_calculate_change_fail_rate(git_repo_DDDP):
    fail_rate = calculate_change_fail_rate(git_repo_DDDP.working_dir, "D-*", "P-*", 0)
    # We have three deployments, one is a patch. Failure rate is one in three or ~33%.
    assert fail_rate == pytest.approx((1/3) * 100, 0.1)

def test_calculate_MTTR(git_repo_DDDP):
    MTTR = calculate_MTTR(git_repo_DDDP.working_dir, "D-*", "P-*", 0)
    assert MTTR == 5*60

def test_calculate_MTTR_no_matching_tags(git_repo_DDDP):
    MTTR = calculate_MTTR(git_repo_DDDP.working_dir, "FOO*", "BAR*", 0)
    assert MTTR == "N/A" # no deploys or patches

def test_calculate_change_fail_rate_no_matching_tags(git_repo_DDDP):
    fail_rate = calculate_change_fail_rate(git_repo_DDDP.working_dir, "FOO*", "BAR*", 0)
    assert fail_rate == "N/A" # no deploys or patches


def test_calculate_deploy_interval_no_matching_tags(git_repo_DDDP):
    interval_end = 1548322020 # Thu, 24 Jan 2019 10:27:00 CET in epoch time
    interval_length = 600 # 10 minutes
    interval = calculate_deploy_interval(git_repo_DDDP.working_dir, "FOO*", interval_end - interval_length, interval_end)
    assert interval == "N/A" # no deploys

def test_lead_time_multiple_deploys(git_repo_DDDP):
    mean_lead_time = calculate_lead_time(git_repo_DDDP.working_dir, "FOO*", 1548321540)
    assert mean_lead_time == "N/A"
