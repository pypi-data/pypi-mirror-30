.. This file is generated. DO NOT EDIT it.
.. code-block:: python

    >>> idict = {'a': ['a'], 'b': ['b']}
    >>> odict = multdict(idict, 2)
    >>> assert odict == {'a0': ['a'], 'b0': ['b'], 'a1': ['a'], 'b1': ['b']}
    >>> assert odict['a0'] is odict['a1']

    >>> assert multdict(idict, 1) == idict
    
