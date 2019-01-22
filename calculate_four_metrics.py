"""Calculate the four devops metrics
    * Deployment lead time
    * Deployment interval
    * Change failure rate
    * Mean time to recover

Usage:
    calculate_four_metrics.py lead-time [--deploy-tag-pattern=<fn_match>] [--start-date=<timestamp>] <path_to_git_repo>
    calculate_four_metrics.py deploy-interval [--deploy-tag-pattern=<fn_match>] [--start-date=<timestamp>] <path_to_git_repo>
    calculate_four_metrics.py (-h | --help)

    Options:
        --master-branch=<branch>    example: origin/gh-pages
"""
from fnmatch import fnmatch
import os
import statistics
import time
from functools import partial

import docopt

from git_metrics_release_lead_time import commit_author_time_tag_author_time_and_from_to_tag_name, fetch_tags_and_dates
from process import mk_run


def main():
    flags = docopt.docopt(__doc__)
    now = int(time.time())
    if flags['<path_to_git_repo>']:
        path_to_git_repo = flags['<path_to_git_repo>']
        repo_name = os.path.basename(os.path.abspath(path_to_git_repo))
        run = mk_run(path_to_git_repo)
        if flags["lead-time"]:
            start_date = int(flags["--start-date"] or 0)
            pattern = flags['--deploy-tag-pattern'] or '*'
            gen = commit_author_time_tag_author_time_and_from_to_tag_name(
                run,
                partial(fnmatch, pat=pattern),
                start_date,
            )
            lead_time_data = ((tat-cat) for cat, tat, old_tag, tag in gen)
            mean_seconds = statistics.mean(lead_time_data)
            print(f"Avarage lead time: {mean_seconds:.0f} seconds")
            print(f"Avarage lead time: {(mean_seconds / 3600):.0f} hours")
            print(f"Avarage lead time: {(mean_seconds / 86400):.0f} days")
        if flags["deploy-interval"]:
            start_date = int(flags["--start-date"] or 0)
            pattern = flags['--deploy-tag-pattern'] or '*'
            gen = fetch_tags_and_dates(
                run,
                partial(fnmatch, pat=pattern),
                start_date,
            )
            deployment_data = set(tat for tag, tat in gen)
            interval_seconds = (now - start_date) / len(deployment_data)
            print(f"Release interval: {interval_seconds:.0f} seconds")
            print(f"Release interval: {(interval_seconds / 3600):.0f} hours")
            print(f"Release interval: {(interval_seconds / 86400):.0f} days")


if __name__ == "__main__":
    main()
