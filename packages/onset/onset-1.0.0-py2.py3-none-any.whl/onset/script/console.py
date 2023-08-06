#!/usr/bin/env python3
"""Run a sequence of set operations on files (use '-' for stdin).

Example: onset - U a.txt Diff b.txt disjunction c.txt INTER d.txt

Operations supported:
    - Union: u / union
    - Difference: d / diff / difference
    - Disjunction: j / disj / disjunction
    - Intersection: i / inter / intersection

NOTE: All set operations are case-insensitive."""

from onset import onset as S
from functools import reduce
import typing as T
import funcy as F
import argparse
import sys


USAGE = 'onset INIT STEP+ ; STEP = (OP FILE)'

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, usage=USAGE)
parser.add_argument('init', help=argparse.SUPPRESS)
parser.add_argument('steps', nargs='+', help=argparse.SUPPRESS)


def from_oper(oper: str) -> T.Callable[[set, set], None]:
    """Return a set function from a string."""
    oper = oper.lower()

    if oper in {'u', 'union'}:
        return S.union
    elif oper in {'d', 'diff', 'difference'}:
        return S.difference
    elif oper in {'j', 'disj', 'disjunction'}:
        return S.disjunction
    elif oper in {'i', 'inter', 'intersection'}:
        return S.intersection
    else:
        raise ValueError(f"Unknown set operation: {oper}")


def from_file(path: str) -> set:
    """Return a set of lines from a file path."""
    return {ln.rstrip() for ln in open(path) if ln}


def from_step(state: set, step) -> set:
    """Run an operation step on the current state."""
    oper, file = step
    t = from_file(file)
    f = from_oper(oper)

    f(state, t)

    return state


def main(args=None):
    opts = parser.parse_args(args)

    assert len(opts.steps) % 2 == 0, "All operations must be paired with a file."

    init = from_file(opts.init)
    steps = F.partition(2, opts.steps)
    out = reduce(from_step, steps, init)

    sys.stdout.write('\n'.join(out))


if __name__ == '__main__':
    main()
