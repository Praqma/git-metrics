"""Calculate the four devops metrics
    * Deployment lead time
    * Deployment interval
    * Change failure rate
    * Mean time to recover

Usage:
    calculate_four_metrics.py lead-time [--deploy-tag-pattern=<fn_match>] [--start-date=<timestamp>] <path_to_git_repo>
    calculate_four_metrics.py deploy-interval [--deploy-tag-pattern=<fn_match>] [--start-date=<timestamp>] <path_to_git_repo>
    calculate_four_metrics.py change-fail-rate [--deploy-tag-pattern=<fn_match>] [--patch-tag-pattern=<fn_match>] [--start-date=<timestamp>] <path_to_git_repo>
    calculate_four_metrics.py recovery-time [--deploy-tag-pattern=<fn_match>] [--patch-tag-pattern=<fn_match>] [--start-date=<timestamp>] <path_to_git_repo>
    calculate_four_metrics.py metrics-all [--deploy-tag-pattern=<fn_match>] [--patch-tag-pattern=<fn_match>] [--start-date=<timestamp>] <path_to_git_repo>
    calculate_four_metrics.py (-h | --help)

    Options:
        --master-branch=<branch>    example: origin/gh-pages
"""
import csv
import sys
from fnmatch import fnmatch
import os
import statistics
import time
from functools import partial

import docopt

from git_metrics_release_lead_time import commit_author_time_tag_author_time_and_from_to_tag_name, \
    fetch_tags_and_author_dates, fetch_tags_and_commit_dates
from process import mk_run
from recovery_time import Deployment, find_is_patch, find_outages


def main():
    flags = docopt.docopt(__doc__)
    now = int(time.time())
    if flags['<path_to_git_repo>']:
        path_to_git_repo = flags['<path_to_git_repo>']
        repo_name = os.path.basename(os.path.abspath(path_to_git_repo))
        start_date = int(flags["--start-date"] or 0)
        deploy_pattern = flags['--deploy-tag-pattern'] or '*'
        patch_pattern = flags['--patch-tag-pattern'] or '*'
        if flags["lead-time"]:
            mean_seconds = calculate_lead_time(path_to_git_repo, deploy_pattern, start_date)
            print(f"Avarage lead time: {mean_seconds:.0f} seconds")
            print(f"Avarage lead time: {(mean_seconds / 3600):.0f} hours")
            print(f"Avarage lead time: {(mean_seconds / 86400):.0f} days")
        if flags["deploy-interval"]:
            interval_seconds = calculate_deploy_interval(path_to_git_repo, deploy_pattern, start_date, now)
            print(f"Deploy interval: {interval_seconds:.0f} seconds")
            print(f"Deploy interval: {(interval_seconds / 3600):.0f} hours")
            print(f"Deploy interval: {(interval_seconds / 86400):.0f} days")
        if flags["change-fail-rate"]:
            change_fail_rate = calculate_change_fail_rate(path_to_git_repo, deploy_pattern, patch_pattern, start_date)
            print(f"Change failure rate: {change_fail_rate:.1f}%")
        if flags["recovery-time"]:
            MTTR = calculate_MTTR(path_to_git_repo, deploy_pattern, patch_pattern, start_date)
            print(f"Recovery time: {MTTR} seconds")
            print(f"Recovery time: {(MTTR / 3600):.0f} hours")
            print(f"Recovery time: {(MTTR / 86400):.0f} days")
        if flags["metrics-all"]:
            lead_time = calculate_lead_time(path_to_git_repo, deploy_pattern, start_date)
            interval = calculate_deploy_interval(path_to_git_repo, deploy_pattern, start_date, now)
            change_fail_rate = calculate_change_fail_rate(path_to_git_repo, deploy_pattern, patch_pattern, start_date)
            MTTR = calculate_MTTR(path_to_git_repo, deploy_pattern, patch_pattern, start_date)
            data = [lead_time, interval, change_fail_rate, MTTR, repo_name]
            write_four_metrics_csv_file(map(lambda d: str(d), data))


def calculate_MTTR(path_to_git_repo, deploy_pattern, patch_pattern, start_date):
    run = mk_run(path_to_git_repo)
    deploy_tags_author_date = fetch_tags_and_author_dates(
        run,
        partial(fnmatch, pat=deploy_pattern),
        start_date,
    )
    deploy_tags_commit_date = dict(fetch_tags_and_commit_dates(
        run,
        partial(fnmatch, pat=deploy_pattern),
        start_date,
    ))
    patch_tags_with_commit_date = list(fetch_tags_and_commit_dates(
        run,
        partial(fnmatch, pat=patch_pattern),
        start_date,
    ))
    deployments = []
    for deployment in deploy_tags_author_date:
        is_patch = find_is_patch(deployment[0], deploy_tags_commit_date, patch_tags_with_commit_date)
        deployments.append(Deployment(is_patch, deployment[1]))
    outages = find_outages(deployments)
    downtime = (end.time - start.time for start, end in outages)
    return statistics.mean(downtime)


def calculate_change_fail_rate(path_to_git_repo, deploy_pattern, patch_pattern, start_date):
    run = mk_run(path_to_git_repo)
    deploy_tags = fetch_tags_and_author_dates(
        run,
        partial(fnmatch, pat=deploy_pattern),
        start_date,
    )
    patch_tags = fetch_tags_and_author_dates(
        run,
        partial(fnmatch, pat=patch_pattern),
        start_date,
    )
    change_fail_rate = len(list(patch_tags)) / len(list(deploy_tags)) * 100
    return change_fail_rate


def calculate_deploy_interval(path_to_git_repo, pattern, start_date, now):
    run = mk_run(path_to_git_repo)
    gen = fetch_tags_and_author_dates(
        run,
        partial(fnmatch, pat=pattern),
        start_date,
    )
    deployment_data = set(tat for tag, tat in gen)
    interval_seconds = (now - start_date) / len(deployment_data)
    return interval_seconds


def calculate_lead_time(path_to_git_repo, pattern, start_date):
    run = mk_run(path_to_git_repo)
    gen = commit_author_time_tag_author_time_and_from_to_tag_name(
        run,
        partial(fnmatch, pat=pattern),
        start_date,
    )
    lead_time_data = ((tat - cat) for cat, tat, old_tag, tag in gen)
    mean_seconds = statistics.mean(lead_time_data)
    return mean_seconds


def write_four_metrics_csv_file(data):
    writer = csv.writer(sys.stdout, delimiter=',', lineterminator='\n')
    writer.writerow(("deploy lead time", "deploy interval", "change fail rate", "mean time to recover", "repo name"))
    writer.writerow(data)


if __name__ == "__main__":
    main()
