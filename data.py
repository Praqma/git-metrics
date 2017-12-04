from itertools import tee, islice
from typing import Iterable, TypeVar, Tuple


def columns(iterable):
    for line in iterable:
        yield line.split()


T = TypeVar('T')


def zip_with_tail(to_zip: Iterable[T]) -> Iterable[Tuple[T, T]]:
    a, b = tee(to_zip)
    tail = islice(b, 1, None)
    return zip(a, tail)
