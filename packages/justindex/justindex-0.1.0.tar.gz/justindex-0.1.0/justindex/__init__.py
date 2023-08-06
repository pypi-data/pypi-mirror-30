from collections import defaultdict


def index(iterable):
    """
    # pip install justindex
    # >>> from justindex import index

    >>> index((len(s), s) for s in 'a b'.split())
    defaultdict(<class 'list'>, {1: ['a', 'b']})
    >>> index((len(s), s) for s in ''.split())
    defaultdict(<class 'list'>, {})
    >>> sorted(index((len(s), s) for s in 'a b cc'.split()).items())
    [(1, ['a', 'b']), (2, ['cc'])]
    """
    output = defaultdict(list)
    for key, value in iterable:
        output[key].append(value)
    return output
