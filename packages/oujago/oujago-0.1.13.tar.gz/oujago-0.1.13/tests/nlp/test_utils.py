# -*- coding: utf-8 -*-


import pytest


def test_HanziConverter():
    from oujago.nlp.utils import HanziConverter

    assert HanziConverter.to_simplify('繁簡轉換器') == '繁简转换器'
    assert HanziConverter.to_tradition('繁简转换器') == '繁簡轉換器'

