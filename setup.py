from setuptools import setup, find_packages

setup(
    name='git_metrics',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        "docopt >= 0.6.2",
        "GitPython >= 3.1.14",
        "matplotlib >= 3.3.4",
        "pandas >= 1.2.3",
        "pytest >= 6.2.2",
        "requests >= 2.25.1",
    ],
    entry_points={
        'console_scripts': [
            'calculate-four-metrics = git_metrics.calculate_four_metrics:main',
            'git-metrics = git_metrics.git_metrics:main',
        ],
    },
)
