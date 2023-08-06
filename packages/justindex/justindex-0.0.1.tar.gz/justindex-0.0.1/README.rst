.. This file is generated. DO NOT EDIT it.
.. code-block:: python

    >>> index((len(s), s) for s in 'a b'.split())
    defaultdict(<class 'list'>, {1: ['a', 'b']})
    >>> index((len(s), s) for s in ''.split())
    defaultdict(<class 'list'>, {})
    >>> sorted(index((len(s), s) for s in 'a b cc'.split()).items())
    [(1, ['a', 'b']), (2, ['cc'])]
    
