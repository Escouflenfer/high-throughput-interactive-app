import pytest

# import importlib.metadata


__version__ = "0.5"


def test():
    """Run all package tests.

    Examples
    --------
    1. Run all tests.

    >>> import ubermagtable as ut
    ...
    >>> # ut.test()

    """
    return pytest.main(["-v", "--pyargs", "high_throughput_interactive_app", "-l"])
