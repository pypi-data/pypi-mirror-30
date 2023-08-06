# -*- coding: utf-8 -*-


import os

import oujago

try:
    import pyltp
except ImportError:
    pyltp = None

try:
    import jieba.posseg as jieba
except ImportError:
    jieba = None

try:
    import thulac
except ImportError:
    thulac = None

try:
    import pynlpir
except ImportError:
    pynlpir = None

_mode = 'nlpir'
_support_modes = ['jieba', 'ltp', 'thulac', 'nlpir']

_jieba_instance = None
_ltp_instance = None
_thulac_instance = None
_nlpir_instance = None


class BasePOS(object):
    """Abstract Part-of_speech Tagging class.
    """

    def pos(self, input, return_tokens=False, **kwargs):
        raise NotImplementedError


class LTPPOS(BasePOS):
    """HIT-SCIR Language Technology Platform (LTP) POS Tagging.

    词性标注集
    ---------

    LTP 使用的是863词性标注集，其各个词性含义如下表。

    +-----+---------------------+------------+-----+-------------------+------------+
    | Tag | Description         | Example    | Tag | Description       | Example    |
    +=====+=====================+============+=====+===================+============+
    | a   | adjective           | 美丽       | ni  | organization name | 保险公司   |
    +-----+---------------------+------------+-----+-------------------+------------+
    | b   | other noun-modifier | 大型, 西式 | nl  | location noun     | 城郊       |
    +-----+---------------------+------------+-----+-------------------+------------+
    | c   | conjunction         | 和, 虽然   | ns  | geographical name | 北京       |
    +-----+---------------------+------------+-----+-------------------+------------+
    | d   | adverb              | 很         | nt  | temporal noun     | 近日, 明代 |
    +-----+---------------------+------------+-----+-------------------+------------+
    | e   | exclamation         | 哎         | nz  | other proper noun | 诺贝尔奖   |
    +-----+---------------------+------------+-----+-------------------+------------+
    | g   | morpheme            | 茨, 甥     | o   | onomatopoeia      | 哗啦       |
    +-----+---------------------+------------+-----+-------------------+------------+
    | h   | prefix              | 阿, 伪     | p   | preposition       | 在, 把     |
    +-----+---------------------+------------+-----+-------------------+------------+
    | i   | idiom               | 百花齐放   | q   | quantity          | 个         |
    +-----+---------------------+------------+-----+-------------------+------------+
    | j   | abbreviation        | 公检法     | r   | pronoun           | 我们       |
    +-----+---------------------+------------+-----+-------------------+------------+
    | k   | suffix              | 界, 率     | u   | auxiliary         | 的, 地     |
    +-----+---------------------+------------+-----+-------------------+------------+
    | m   | number              | 一, 第一   | v   | verb              | 跑, 学习   |
    +-----+---------------------+------------+-----+-------------------+------------+
    | n   | general noun        | 苹果       | wp  | punctuation       | ，。！     |
    +-----+---------------------+------------+-----+-------------------+------------+
    | nd  | direction noun      | 右侧       | ws  | foreign words     | CPU        |
    +-----+---------------------+------------+-----+-------------------+------------+
    | nh  | person name         | 杜甫, 汤姆 | x   | non-lexeme        | 萄, 翱     |
    +-----+---------------------+------------+-----+-------------------+------------+
    |     |                     |            | z   | descriptive words | 瑟瑟，匆匆 |
    +-----+---------------------+------------+-----+-------------------+------------+

    References
    ----------

    .. [1] http://ltp.readthedocs.io/zh_CN/latest/index.html
    """

    def __init__(self):
        if pyltp is None:
            raise oujago.utils.LTPInstallError()

        pos_model_path = os.path.join(oujago.utils.DATA_PATH, 'ltp/pos.model')
        if not os.path.exists(pos_model_path):
            raise oujago.utils.LTPFileError()
        self.tagger = pyltp.Postagger()
        self.tagger.load(pos_model_path)

    def __del__(self):
        if hasattr(self, 'tagger'):
            self.tagger.release()

    def pos(self, input, return_tokens=False, **kwargs):
        """LTP POS Tagging.

        Parameters
        ----------
        input : str, or list
            If ``str``, call LTP seg, then, perform LTP pos tag.
        return_tokens : bool
            Return segmented tokens with POS tags.

        Returns
        -------
        list
            POS tagged list.
        """

        # prepare data
        if oujago.utils.type_(input) == 'str':
            input = oujago.nlp.seg(input, mode='ltp')

        # POS tag
        tags = list(self.tagger.postag(input))

        # return
        if return_tokens:
            return list(zip(input, tags))
        else:
            return tags


class JiebaPOS(BasePOS):
    def __init__(self):
        if jieba is None:
            raise oujago.utils.JiebaInstallError()

    def pos(self, input, return_tokens=False, **kwargs):
        """Jieba POS Tagging.

        Parameters
        ----------
        input : str, or list
            If ``str``, call LTP seg, then, perform LTP pos tag.
        return_tokens : bool
            Return segmented tokens with POS tags.
        HMM : bool
            Whether to use the Hidden Markov Model.

        """

        # data
        if oujago.utils.is_list(input):
            input = ''.join(input)

        # pos tags
        paris = jieba.lcut(input, **kwargs)

        # returns
        if return_tokens:
            return [(p.word, p.flag) for p in paris]
        else:
            return [p.flag for p in paris]


class ThulacPOS(BasePOS):
    def __init__(self):
        if thulac is None:
            raise oujago.utils.ThulacInstallError()
        self.thu = thulac.thulac()

    def pos(self, input, return_tokens=False, **kwargs):
        # data
        if oujago.utils.is_list(input):
            input = ''.join(input)

        # get results
        results = self.thu.cut(input, text=False)

        if return_tokens:
            return [tuple(a) for a in results]
        else:
            return [a[1] for a in results]


class NLPIRPOS(BasePOS):
    def __init__(self):
        if pynlpir is None:
            raise oujago.utils.NLPIRInstallError()

        pynlpir.open()

    def pos(self, input, return_tokens=False, **kwargs):
        # data
        if oujago.utils.is_list(input):
            input = ''.join(input)

        # get results
        results = pynlpir.segment(input, pos_tagging=True)

        if return_tokens:
            return results
        else:
            return [a[1] for a in results]


def set_pos_mode(mode):
    """Set the Part-of-Speech Tagging method.

    Parameters
    ----------
    mode : str
        The tagging method. Must in ``_support_methods``.

    """
    global _mode

    assert mode.lower() in _support_modes, 'Only support {}'.format(_support_modes)
    _mode = mode.lower()


def get_pos_mode():
    """Get Part-of-Speech Tagging method.

    Returns
    -------
    str
        The global tagging method.
    """
    return _mode


def pos(input, mode=None, return_tokens=False, **kwargs):
    """Part-of-Speech Tagging.

    Examples:

        >>> from oujago.nlp.postag import pos
        >>> sentence = '我不喜欢日本和服'
        >>> pos(sentence, 'jieba')
        ['r', 'd', 'v', 'ns', 'nz']
        >>> pos(sentence, 'ltp')
        ['r', 'd', 'v', 'ns', 'n']
        >>> pos(sentence, 'thulac')
        ['r', 'd', 'v', 'ns', 'n']
        >>> pos(sentence, 'thulac', True)
        [('我', 'r'), ('不', 'd'), ('喜欢', 'v'), ('日本', 'ns'), ('和服', 'n')]
        >>> pos(sentence, 'nlpir')
        ['pronoun', 'adverb', 'verb', 'noun', 'noun']
        >>> pos(sentence, 'nlpir', return_tokens=True)
        [('我', 'pronoun'), ('不', 'adverb'), ('喜欢', 'verb'), ('日本', 'noun'), ('和服', 'noun')]
        >>> from oujago.nlp.postag import set_pos_mode
        >>> set_pos_mode('nlpir')
        >>> sentence = '我不喜欢日本和服'
        >>> pos(sentence)
        ['r', 'd', 'v', 'ns', 'n']

    Parameters
    ----------
    input : str, or list
        To pos string.
    mode : str
        To specify the segment method, 'jieba', 'ltp', or 'moran'.
    return_tokens : bool
        Return segmented tokens with POS tags.

    Returns
    -------
    list
        Tagged list.

    """
    # check
    mode = _mode if mode is None else mode
    assert mode in _support_modes

    # jieba
    if mode == 'jieba':
        # init
        global _jieba_instance
        if _jieba_instance is None:
            _jieba_instance = JiebaPOS()

        # seg
        return _jieba_instance.pos(input, return_tokens, **kwargs)

    # LTP
    if mode == 'ltp':
        # init
        global _ltp_instance
        if _ltp_instance is None:
            _ltp_instance = LTPPOS()

        # seg
        return _ltp_instance.pos(input, return_tokens, **kwargs)

    # thulac
    if mode == 'thulac':
        # init
        global _thulac_instance
        if _thulac_instance is None:
            _thulac_instance = ThulacPOS()

        # seg
        return _thulac_instance.pos(input, return_tokens, **kwargs)

    if mode == 'nlpir':
        global _nlpir_instance
        if _nlpir_instance is None:
            _nlpir_instance = NLPIRPOS()

        return _nlpir_instance.pos(input, return_tokens, **kwargs)

    raise ValueError("Unknown mode: {}".format(mode))
