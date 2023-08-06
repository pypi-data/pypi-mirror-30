def multdict(idict, num):
    """
    >>> idict = {'a': ['a'], 'b': ['b']}
    >>> odict = multdict(idict, 2)
    >>> assert odict == {'a0': ['a'], 'b0': ['b'], 'a1': ['a'], 'b1': ['b']}
    >>> assert odict['a0'] is odict['a1']

    >>> assert multdict(idict, 1) == idict
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
