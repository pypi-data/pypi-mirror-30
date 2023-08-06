# -*- coding: utf-8 -*-

"""
Semantic Role Labeling

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


class BaseSRL(object):
    """Abstract SRL class.
    """

    def label(self, sentence=None, words=None, postags=None, netags=None, srcs=None, **kwargs):
        raise NotImplementedError


class LTPSRL(BaseSRL):
    """HIT-SCIR Language Technology Platform (LTP) SRL.

    语义角色类型
    ------------

    +--------------+------------------------------------------------+
    | 语义角色类型 | 说明                                           |
    +==============+================================================+
    | ADV          | adverbial, default tag ( 附加的，默认标记 )    |
    +--------------+------------------------------------------------+
    | BNE          | beneﬁciary ( 受益人 )                          |
    +--------------+------------------------------------------------+
    | CND          | condition ( 条件 )                             |
    +--------------+------------------------------------------------+
    | DIR          | direction ( 方向 )                             |
    +--------------+------------------------------------------------+
    | DGR          | degree ( 程度 )                                |
    +--------------+------------------------------------------------+
    | EXT          | extent ( 扩展 )                                |
    +--------------+------------------------------------------------+
    | FRQ          | frequency ( 频率 )                             |
    +--------------+------------------------------------------------+
    | LOC          | locative ( 地点 )                              |
    +--------------+------------------------------------------------+
    | MNR          | manner ( 方式 )                                |
    +--------------+------------------------------------------------+
    | PRP          | purpose or reason ( 目的或原因 )               |
    +--------------+------------------------------------------------+
    | TMP          | temporal ( 时间 )                              |
    +--------------+------------------------------------------------+
    | TPC          | topic ( 主题 )                                 |
    +--------------+------------------------------------------------+
    | CRD          | coordinated arguments ( 并列参数 )             |
    +--------------+------------------------------------------------+
    | PRD          | predicate ( 谓语动词 )                         |
    +--------------+------------------------------------------------+
    | PSR          | possessor ( 持有者 )                           |
    +--------------+------------------------------------------------+
    | PSE          | possessee ( 被持有 )                           |
    +--------------+------------------------------------------------+


    References
    ----------

    .. [1] http://ltp.readthedocs.io/zh_CN/latest/index.html

    """

    def __init__(self):
        if pyltp is None:
            raise oujago.utils.LTPInstallError()

        srl_path = os.path.join(oujago.utils.DATA_PATH, 'srl')
        if not os.path.exists(srl_path):
            raise oujago.utils.LTPFileError()
        self.labeller = pyltp.SementicRoleLabeller()
        self.labeller.load(srl_path)

    def __del__(self):
        self.labeller.release()

    def label(self, sentence=None, words=None, postags=None, netags=None, srcs=None, **kwargs):
        if sentence is None:
            assert words and postags and netags and srcs
        else:
            assert sentence is not None
            words = oujago.nlp.seg(sentence)
            postags = oujago.nlp.pos(words)
            netags = oujago.nlp.ner(words)
            srcs = oujago.nlp.deparse(words)
        return list(self.labeller.label(words, postags, netags, srcs))


def srlabel(sentence=None, words=None, postags=None, netags=None, srcs=None, mode=_mode, **kwargs):
    # LTP
    if mode == 'ltp':
        # init
        global _ltp_instance
        if _ltp_instance is None:
            _ltp_instance = LTPSRL()

        # NER
        return _ltp_instance.label(sentence, words, postags, netags, srcs, **kwargs)

    raise ValueError("Unknown mode: {}".format(mode))
