

def for_each_ref(glob=None, format=None):
    return sum((
        ["git", "for-each-ref"],
        [] if format is None else [f"--format={format}"],
        [] if glob is None else [glob],
    ), [])
