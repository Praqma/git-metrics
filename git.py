

def for_each_ref(glob=None, format=None, sort=None) -> [str]:
    return sum((
        ["git", "for-each-ref"],
        [] if format is None else [f"--format={format}"],
        [] if sort is None else [f"--sort={sort}"],
        [] if glob is None else [glob],
    ), [])


def log(selector=None, format=None) -> [str]:
    return sum((
        ["git", "log"],
        [] if format is None else [f"--format={format}"],
        [] if selector is None else [selector],
    ), [])


def cherry(upstream=None, head=None) -> [str]:
    return sum((
        ["git", "cherry"],
        [] if upstream is None else [upstream],
        [] if head is None else [head],
    ), [])
