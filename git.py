from typing import List, Iterable


def for_each_ref(glob=None, format=None, sort=None) -> List[str]:
    return sum((
        ["git", "for-each-ref"],
        [] if format is None else [f"--format={format}"],
        [] if sort is None else [f"--sort={sort}"],
        [] if glob is None else [glob],
    ), [])


def log(selector=None, format=None, limit=None) -> List[str]:
    return sum((
        ["git", "log"],
        [] if limit is None else [f"-{limit}"],
        [] if format is None else [f"--format={format}"],
        [] if selector is None else [selector],
    ), [])


def show(objects: Iterable[str]=(), diff: bool=True, format: str=None) -> List[str]:
    return sum((
        ["git", "show"],
        [] if diff else [f"-s"],
        [] if format is None else [f"--format={format}"],
        list(objects),
    ), [])


def cherry(upstream=None, head=None) -> List[str]:
    return sum((
        ["git", "cherry"],
        [] if upstream is None else [upstream],
        [] if head is None else [head],
    ), [])
