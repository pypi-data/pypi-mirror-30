# -*- coding:utf-8 -*-

import numpy as np
from numpy.testing import assert_allclose

import pytest
from oujago.utils.data import pad_sequences


def test_pad_sequences():
    a = [[1], [1, 2], [1, 2, 3]]

    # test padding
    b = pad_sequences(a, maxlen=3, padding='pre')
    assert_allclose(b, [[0, 0, 1], [0, 1, 2], [1, 2, 3]])
    b = pad_sequences(a, maxlen=3, padding='post')
    assert_allclose(b, [[1, 0, 0], [1, 2, 0], [1, 2, 3]])

    # test truncating
    b = pad_sequences(a, maxlen=2, truncating='pre')
    assert_allclose(b, [[0, 1], [1, 2], [2, 3]])
    b = pad_sequences(a, maxlen=2, truncating='post')
    assert_allclose(b, [[0, 1], [1, 2], [1, 2]])

    # test value
    b = pad_sequences(a, maxlen=3, value=1)
    assert_allclose(b, [[1, 1, 1], [1, 1, 2], [1, 2, 3]])


def test_pad_sequences_vector():
    a = [[[1, 1]],
         [[2, 1], [2, 2]],
         [[3, 1], [3, 2], [3, 3]]]

    # test padding
    b = pad_sequences(a, maxlen=3, padding='pre')
    assert_allclose(b, [[[0, 0], [0, 0], [1, 1]],
                        [[0, 0], [2, 1], [2, 2]],
                        [[3, 1], [3, 2], [3, 3]]])
    b = pad_sequences(a, maxlen=3, padding='post')
    assert_allclose(b, [[[1, 1], [0, 0], [0, 0]],
                        [[2, 1], [2, 2], [0, 0]],
                        [[3, 1], [3, 2], [3, 3]]])

    # test truncating
    b = pad_sequences(a, maxlen=2, truncating='pre')
    assert_allclose(b, [[[0, 0], [1, 1]],
                        [[2, 1], [2, 2]],
                        [[3, 2], [3, 3]]])

    b = pad_sequences(a, maxlen=2, truncating='post')
    assert_allclose(b, [[[0, 0], [1, 1]],
                        [[2, 1], [2, 2]],
                        [[3, 1], [3, 2]]])

    # test value
    b = pad_sequences(a, maxlen=3, value=1)
    assert_allclose(b, [[[1, 1], [1, 1], [1, 1]],
                        [[1, 1], [2, 1], [2, 2]],
                        [[3, 1], [3, 2], [3, 3]]])

