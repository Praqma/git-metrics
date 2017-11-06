

def columns(iterable):
    for line in iterable:
        yield line.split()


def decode(iterable):
    for line in iterable:
        yield line.decode('utf-8')
