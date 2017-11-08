

def columns(iterable):
    for line in iterable:
        yield line.split()
