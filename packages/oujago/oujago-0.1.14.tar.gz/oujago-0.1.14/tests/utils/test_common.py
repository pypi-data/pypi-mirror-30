

import pytest


def test_is_iterable():
    from oujago.utils.common import is_iterable

    for obj in ['abc', (1, 2, 3), [1, 2, 3], set([1, 2, 3]), {'a': 1}]:
        assert is_iterable(obj)

    for obj in [123, ]:
        assert not is_iterable(obj)


def test_is_list():
    from oujago.utils import is_list

    for obj in [(1, 2, 3), [1, 2, 3]]:
        assert is_list(obj)

    for obj in [123, 'abc', {1, 2, 3}, {'1': 1, '2': 2}]:
        assert not is_list(obj)


def test_type_():
    from oujago.utils import type_

    for obj in ['1', 1]:
        assert type_(obj) == obj.__class__.__name__


def test_hostname():
    from oujago.utils.common import hostname

    assert hostname()


def test_system():
    from oujago.utils.common import system

    assert system()


def test_yield_item():
    from oujago.utils.common import yield_item
    import numpy as np

    assert np.allclose(list(yield_item([1, [2, 3]])),
                       [1, 2, 3])
    assert np.allclose(list(yield_item([1, 2, 3])),
                       [1, 2, 3])
    assert np.allclose(list(yield_item([1, [2], [3, [4, [5, [6, 7]]]]])),
                       [1, 2, 3, 4, 5, 6, 7])


def test_ParamCls():
    from oujago.utils import ParamCls

    class A(ParamCls):
        var_a='variable_a'
        var_b='variable_b'

        def func_a(self):
            pass

        def func_b(self):
            pass

        @property
        def var_c(self):
            return ''

    a = A()

    assert set(a.get_functions()) == {'func_a', 'func_b', 'get_functions', 'get_variables'}
    assert a.get_variables() == {'var_a':'variable_a', 'var_b':'variable_b', 'var_c': ''}



