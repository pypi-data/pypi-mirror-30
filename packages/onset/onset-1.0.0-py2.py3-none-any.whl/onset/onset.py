"""Set operations supported by the project."""


def union(s: set, t: set) -> None:
    """Return set `s` with elements added from `t`.
    >>> s, t = {1, 2, 3}, {1, 3, 5}
    >>> union(s, t); s
    {1, 2, 3, 5}"""
    s.update(t)


def difference(s: set, t: set) -> None:
    """Return set `s` after removing elements from `t`
    >>> s, t = {1, 2, 3}, {1, 3, 5}
    >>> difference(s, t); s
    {2}"""
    s.difference_update(t)


def intersection(s: set, t: set) -> None:
    """Return set `s` keeping only elements found in `t`.
    >>> s, t = {1, 2, 3}, {1, 3, 5}
    >>> intersection(s, t); s
    {1, 3}"""
    s.intersection_update(t)


def disjunction(s: set, t: set) -> None:
    """Return set `s` with elements from `s` or `t` but not both.
    >>> s, t = {1, 2, 3}, {1, 3, 5}
    >>> disjunction(s, t); s
    {2, 5}"""
    s.symmetric_difference_update(t)
