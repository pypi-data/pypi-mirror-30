def multdict(idict, num):
    """
    >>> idict = {'a': ['x'], 'b': 0}

    >>> assert multdict(idict, 0) == {}

    >>> assert multdict(idict, 1) is idict

    >>> odict = multdict(idict, 2)
    >>> assert idict == {'a': ['x'], 'b': 0}
    >>> assert odict == {'a0': ['x'], 'b0': 0, 'a1': ['x'], 'b1': 0}
    >>> assert odict['a0'] is odict['a1']
    """
    assert num >= 0
    if num == 1:
        return idict

    odict = {}
    for i in range(num):
        for ikey, value in idict.items():
            okey = ikey + str(i)
            assert okey not in odict
            odict[okey] = value
    return odict
