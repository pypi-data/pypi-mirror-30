.. This file is generated. DO NOT EDIT it.
.. code-block:: python

    # pip install multdict
    # >>> from multdict import multdict


    >>> idict = {'a': ['x'], 'b': 0}

    >>> assert multdict(idict, 0) == {}

    >>> assert multdict(idict, 1) is idict

    >>> odict = multdict(idict, 2)
    >>> assert idict == {'a': ['x'], 'b': 0}
    >>> assert odict == {'a0': ['x'], 'b0': 0, 'a1': ['x'], 'b1': 0}
    >>> assert odict['a0'] is odict['a1']
    
