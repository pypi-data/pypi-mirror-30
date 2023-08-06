# -*- coding: utf-8 -*-

"""
Named Entity Recognition

"""

import os

import oujago

try:
    import pyltp
except ImportError:
    pyltp = None

try:
    import pynlpir
except ImportError:
    pynlpir = None

_mode = 'ltp'
_support_modes = ['ltp']

_ltp_instance = None
_moran_instance = None


class BaseNER(object):
    """Abstract NOR class.
    """

    def recognize(self, sentence=None, words=None, postags=None, **kwargs):
        raise NotImplementedError


class LTPNER(BaseNER):
    """HIT-SCIR Language Technology Platform (LTP) NER Tagging.

    命名实体识别标注集
    -------------------

    NE识别模块的标注结果采用O-S-B-I-E标注形式，其含义为

    +------+----------------------+
    | 标记 | 含义                 |
    +======+======================+
    | O    | 这个词不是NE         |
    +------+----------------------+
    | S    | 这个词单独构成一个NE |
    +------+----------------------+
    | B    | 这个词为一个NE的开始 |
    +------+----------------------+
    | I    | 这个词为一个NE的中间 |
    +------+----------------------+
    | E    | 这个词位一个NE的结尾 |
    +------+----------------------+

    LTP中的NE 模块识别三种NE，分别如下：

    +------+--------+
    | 标记 | 含义   |
    +======+========+
    | Nh   | 人名   |
    +------+--------+
    | Ni   | 机构名 |
    +------+--------+
    | Ns   | 地名   |
    +------+--------+

    References
    ----------

    .. [1] http://ltp.readthedocs.io/zh_CN/latest/index.html
    """

    def __init__(self):
        ner_path = os.path.join(oujago.utils.DATA_PATH, 'ltp/ner.model')
        if not os.path.exists(ner_path):
            raise oujago.utils.LTPFileError()
        self.recognizer = pyltp.NamedEntityRecognizer()
        self.recognizer.load(ner_path)

    def __del__(self):
        if hasattr(self, 'recognizer'):
            self.recognizer.release()

    def recognize(self, sentence=None, **kwargs):
        """Recognize.

        Parameters
        ----------
        sentence : str

        kwargs:
            words : list, or None
                Segmented words.
            postags : list, or None
                POS tags.

        Returns
        -------
        list
            Tagged list.
        """
        if sentence is None:
            assert 'words' in sentence
            assert 'postags' in sentence
            words = sentence['words']
            postags = sentence['postags']
        else:
            words = oujago.nlp.seg(sentence, 'ltp')
            postags = oujago.nlp.pos(words, 'ltp')
        tags = self.recognizer.recognize(words, postags)
        return [(w, t) for w, t in zip(words, tags)]


def set_ner_mode(mode):
    """Set the NER Tagging method.

    Parameters
    ----------
    mode : str
        The tagging method. Must in ``_support_methods``.

    """
    global _mode

    assert mode.lower() in _support_modes, 'Only support {}'.format(_support_modes)
    _mode = mode.lower()


def get_ner_mode():
    """Get NER Tagging method.

    Returns
    -------
    str
        The global tagging method.
    """
    return _mode


def ner(sentence=None, mode=None, **kwargs):
    """Named Entity Recognition.

    Examples:

        >>> from oujago.nlp import ner
        >>> ner("阿姆斯特朗是乘哪个飞船成功登月的", mode='ltp')
        [('阿姆斯特朗', 'S-Nh'), ('是', 'O'), ('乘', 'O'), ('哪个', 'O'),
        ('飞船', 'O'), ('成功', 'O'), ('登月', 'O'), ('的', 'O')]

    Parameters
    ----------
    sentence : str, or None
        Sentence.
    mode : str,
        NER mode.

    words : list, or None
        Segmented words.
    postags : list, or None
        POS tags.

    Return
    ------
    list
        Tagged list
    """

    # check
    mode = _mode if mode is None else mode
    assert mode in _support_modes

    # LTP
    if mode == 'ltp':
        # init
        global _ltp_instance
        if _ltp_instance is None:
            _ltp_instance = LTPNER()

        # NER
        return _ltp_instance.recognize(sentence, **kwargs)


    raise ValueError("Unknown mode: {}".format(mode))
