


def test_ipython():
    """
    This test will never touch the "do something broken"
    if run with pytest
    """

    try:
        __IPYTHON__  # is True when run with ipython, else undefined
        use_ipython = True
    except:
        use_ipython = False

    if use_ipython:
        1/0
        # do something broken
