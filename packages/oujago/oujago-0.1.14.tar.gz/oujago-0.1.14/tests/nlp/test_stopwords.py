

import pytest


def test_chinese_stopwords():
    from oujago.nlp.stopwords import ChineseStopWords

    for mode in ('all', 'hit', 'HIT', 'baidu', 'Baidu', 'normal'):
        sw = ChineseStopWords(mode)

        for word in ('的', '并', '啊'):
            assert sw.check(word)

