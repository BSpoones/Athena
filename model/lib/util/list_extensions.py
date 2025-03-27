from collections import defaultdict
from typing import TypeVar, List, Callable, Dict, Iterator

T = TypeVar('T')  # Item type
K = TypeVar('K')  # Key type returned by key_func


def group_by(iterable: List[T], key_func: Callable[[T], K]) -> Dict[K, List[T]]:
    grouped = defaultdict(list)
    for item in iterable:
        key = key_func(item)
        grouped[key].append(item)
    return dict(grouped)


def chunked(values: List[T], size: int) -> Iterator[List[T]]:
    if not isinstance(size, int):
        raise TypeError("Chunk size must be an integer.")
    if size <= 0:
        raise ValueError("Chunk size must be a positive integer.")

    for i in range(0, len(values), size):
        yield values[i:i + size]

def parse_list_response(response_text: str) -> list[list[str] | None]:
    groups = response_text.strip().split("\n\n")
    result = []

    for group in groups:
        rewrites = [line.strip() for line in group.split("\n") if line.strip()]

        if any([x.lower() == "null" for x in rewrites]):
            result.append([])
        else:
            result.append(rewrites)

    return result