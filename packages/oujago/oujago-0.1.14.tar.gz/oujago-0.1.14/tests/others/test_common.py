

import pytest


def test_is_iterable():
    from oujago.utils.common import is_iterable

    for obj in ['abc', (1, 2, 3), [1, 2, 3], set([1, 2, 3]), {'a': 1}]:
        assert is_iterable(obj)

    for obj in [123, ]:
        assert not is_iterable(obj)


def test_hostname():
    from oujago.utils.common import hostname

    assert hostname()


def test_system():
    from oujago.utils.common import system

    assert system()

