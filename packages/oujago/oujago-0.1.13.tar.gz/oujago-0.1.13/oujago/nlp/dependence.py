# -*- coding: utf-8 -*-

"""
Dependency Parsing
"""


import os
import oujago

try:
    import pyltp
except ImportError:
    pyltp = None


_mode = 'ltp'
_support_modes = ['ltp']

_ltp_instance = None


class BaseDP(object):
    """Abstract DP class.
    """
    def parse(self, sentence=None, words=None, postags=None, **kwargs):
        raise NotImplementedError


class LTPDP(BaseDP):
    """HIT-SCIR Language Technology Platform (LTP) DP Parsing.

    依存句法关系
    -------------

    +------------+-----+----------------------------+----------------------------+
    | 关系类型   | Tag | Description                | Example                    |
    +============+=====+============================+============================+
    | 主谓关系   | SBV | subject-verb               | 我送她一束花 (我 <-- 送)   |
    +------------+-----+----------------------------+----------------------------+
    | 动宾关系   | VOB | 直接宾语，verb-object      | 我送她一束花 (送 --> 花)   |
    +------------+-----+----------------------------+----------------------------+
    | 间宾关系   | IOB | 间接宾语，indirect-object  | 我送她一束花 (送 --> 她)   |
    +------------+-----+----------------------------+----------------------------+
    | 前置宾语   | FOB | 前置宾语，fronting-object  | 他什么书都读 (书 <-- 读)   |
    +------------+-----+----------------------------+----------------------------+
    | 兼语       | DBL | double                     | 他请我吃饭 (请 --> 我)     |
    +------------+-----+----------------------------+----------------------------+
    | 定中关系   | ATT | attribute                  | 红苹果 (红 <-- 苹果)       |
    +------------+-----+----------------------------+----------------------------+
    | 状中结构   | ADV | adverbial                  | 非常美丽 (非常 <-- 美丽)   |
    +------------+-----+----------------------------+----------------------------+
    | 动补结构   | CMP | complement                 | 做完了作业 (做 --> 完)     |
    +------------+-----+----------------------------+----------------------------+
    | 并列关系   | COO | coordinate                 | 大山和大海 (大山 --> 大海) |
    +------------+-----+----------------------------+----------------------------+
    | 介宾关系   | POB | preposition-object         | 在贸易区内 (在 --> 内)     |
    +------------+-----+----------------------------+----------------------------+
    | 左附加关系 | LAD | left adjunct               | 大山和大海 (和 <-- 大海)   |
    +------------+-----+----------------------------+----------------------------+
    | 右附加关系 | RAD | right adjunct              | 孩子们 (孩子 --> 们)       |
    +------------+-----+----------------------------+----------------------------+
    | 独立结构   | IS  | independent structure      | 两个单句在结构上彼此独立   |
    +------------+-----+----------------------------+----------------------------+
    | 核心关系   | HED | head                       | 指整个句子的核心           |
    +------------+-----+----------------------------+----------------------------+


    References
    ----------

    .. [1] http://ltp.readthedocs.io/zh_CN/latest/index.html

    """
    def __init__(self):
        if pyltp is None:
            raise oujago.utils.LTPInstallError()

        ner_path = os.path.join(oujago.utils.DATA_PATH, 'ltp/parser.model')
        if not os.path.exists(ner_path):
            raise oujago.utils.LTPFileError()
        self.parser = pyltp.NamedEntityRecognizer()
        self.parser.load(ner_path)

    def __del__(self):
        self.parser.release()

    def parse(self, sentence=None, words=None, postags=None, **kwargs):
        if sentence is None:
            assert words and postags
        else:
            assert sentence is not None
            words = oujago.nlp.seg(sentence)
            postags = oujago.nlp.pos(words)
        arcs = self.parser.parse(words, postags)
        return list(arcs)


def deparse(sentence=None, words=None, postags=None, mode=_mode, **kwargs):

    # LTP
    if mode == 'ltp':
        # init
        global _ltp_instance
        if _ltp_instance is None:
            _ltp_instance = LTPDP()

        # NER
        return _ltp_instance.parse(sentence, words, postags, **kwargs)

    raise ValueError("Unknown mode: {}".format(mode))

