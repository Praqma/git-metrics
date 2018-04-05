# Git Metrics

This project helps analyse a git repo that has beforehand been cloned to a local directory.

There are two types of data we currently support gathering of and plotting, Open branches and Release lead time.

## Open branches

Open branches gathers information about the age of all commits in a branch that are not yet merged into the master branch. This can help visualize how much value is not yet integrated into the project, or the potential merge cost of all code that is not yet shared between developers.

## Release Lead Time

Release lead time is at best a estimate and can be tricky if not impossible to get from your repository, git metrics tries its best.

Using tags that looks like release tags, you can help it with a "fn match" pattern. It tries to bin commits into a release that was, most likely, the first release including that change.

This data can be plotted and show things like how old the oldest change was for each release.

## Installation

Using python 3

To install dependencies:
	`pip install -r requirements.txt`

for more help run:
	`python git_metrics.py --help`
