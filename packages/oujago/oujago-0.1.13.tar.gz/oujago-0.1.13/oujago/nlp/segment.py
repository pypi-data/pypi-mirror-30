# -*- coding: utf-8 -*-


import os

import oujago

try:
    import jieba
except ImportError:
    jieba = None

try:
    import pyltp
except ImportError:
    pyltp = None

try:
    import thulac
except ImportError:
    thulac = None


try:
    import pynlpir
except ImportError:
    pynlpir = None


_mode = 'jieba'
_support_modes = ['jieba', 'ltp', 'thulac', 'nlpir']

_jieba_instance = None
_ltp_instance = None
_thulac_instance = None
_nlpir_instance = None


class BaseSegment(object):
    """Abstract Segmentation class.
    """
    def seg(self, sentence, **kwargs):
        raise NotImplementedError


class LTPSeg(BaseSegment):
    """HIT-SCIR Language Technology Platform (LTP) Segmentation.

    分词标注集
    -----------

    +------+----------+------------+
    | 标记 | 含义     | 举例       |
    +======+==========+============+
    | B    | 词首     | __中__国   |
    +------+----------+------------+
    | I    | 词中     | 哈__工__大 |
    +------+----------+------------+
    | E    | 词尾     | 科__学__   |
    +------+----------+------------+
    | S    | 单字成词 | 的         |
    +------+----------+------------+

    References
    ----------

    .. [1] http://ltp.readthedocs.io/zh_CN/latest/index.html
    """

    def __init__(self):
        if pyltp is None:
            raise oujago.utils.LTPInstallError()

        ltp_seg_path = os.path.join(oujago.utils.DATA_PATH, 'ltp/cws.model')
        if not os.path.exists(ltp_seg_path):
            raise oujago.utils.LTPFileError()

        self.segment = pyltp.Segmentor()
        self.segment.load(ltp_seg_path)

    def __del__(self):
        if hasattr(self, 'segment'):
            self.segment.release()

    def seg(self, sentence, **kwargs):
        return list(self.segment.segment(sentence))


class JiebaSeg(BaseSegment):
    """Jieba Chinese text segmentation.
    """

    def __init__(self):
        if jieba is None:
            raise oujago.utils.JiebaInstallError()

    def seg(self, sentence, **kwargs):
        """Segment method.

        Parameters
        ----------
        sentence : str
            The str(unicode) to be segmented.
        cut_all : bool
            Model type. True for full pattern, False for accurate pattern.
        HMM : bool
            Whether to use the Hidden Markov Model.

        Returns
        -------
        list
            Segmented words.
        """
        return jieba.lcut(sentence, **kwargs)


class ThulacSeg(BaseSegment):
    """thulac segmentation.
    """
    def __init__(self):
        if thulac is None:
            raise oujago.utils.ThulacInstallError()
        self.thu = thulac.thulac(seg_only=True)

    def seg(self, sentence, **kwargs):
        res = self.thu.cut(sentence, text=False)
        return [a[0] for a in res]


class NLPIRSeg(BaseSegment):
    """PyNLPIR segmentation."""
    def __init__(self):
        if pynlpir is None:
            raise oujago.utils.NLPIRInstallError()

        pynlpir.open()

    def seg(self, sentence, **kwargs):
        res = pynlpir.segment(sentence, pos_tagging=False)
        return res

    def __del__(self):
        pynlpir.close()


def set_seg_mode(mode):
    """Set the segmentation method.

    Parameters
    ----------
    mode : str
        The segmentation method. Must in ``_support_methods``.

    """
    global _mode

    assert mode.lower() in _support_modes, 'Only support {}'.format(_support_modes)
    _mode = mode.lower()


def get_seg_mode():
    """Get segmentation method.

    Returns
    -------
    str
        The global segmentation method.
    """
    return _mode


def seg(sentence, mode=None, **kwargs):
    """Cut, segmentation.

    Examples:

        >>> from oujago.nlp.segment import seg
        >>> sentence = "这是一个伸手不见五指的黑夜。我叫孙悟空，我爱北京，我爱Python和C++。"
        >>> seg(sentence)
        ['这是', '一个', '伸手不见五指', '的', '黑夜', '。', '我', '叫', '孙悟空', '，', '我', '爱',
        '北京', '，', '我', '爱', 'Python', '和', 'C++', '。']
        >>> seg(sentence, mode='ltp')
        ['这', '是', '一个', '伸手', '不', '见', '五', '指', '的', '黑夜', '。', '我', '叫', '孙悟空',
        '，', '我', '爱', '北京', '，', '我', '爱', 'Python', '和', 'C', '+', '+', '。']
        >>> seg(sentence, mode='jieba')
        ['这是', '一个', '伸手不见五指', '的', '黑夜', '。', '我', '叫', '孙悟空', '，', '我', '爱',
        '北京', '，', '我', '爱', 'Python', '和', 'C++', '。']
        >>> seg(sentence, mode='thulac')
        ['这', '是', '一个', '伸手不见五指', '的', '黑夜', '。', '我', '叫', '孙悟空', '，',
        '我', '爱', '北京', '，', '我', '爱', 'Python', '和', 'C', '+', '+', '。']
        >>> seg(sentence, mode='nlpir')
        ['这', '是', '一个', '伸手', '不见', '五指', '的', '黑夜', '。', '我', '叫', '孙悟空',
        '，', '我', '爱', '北京', '，', '我', '爱', 'Python', '和', 'C++', '。']


    Parameters
    ----------
    sentence : str
        To seg string.
    mode : str
        To specify the segment method, 'jieba', 'ltp', or 'moran'.

    Returns
    -------
    list
        Segmented list.

    """
    # check
    mode = _mode if mode is None else mode
    assert mode in _support_modes

    # jieba
    if mode == 'jieba':
        # init
        global _jieba_instance
        if _jieba_instance is None:
            _jieba_instance = JiebaSeg()

        # seg
        return _jieba_instance.seg(sentence, **kwargs)

    # LTP
    if mode == 'ltp':
        # init
        global _ltp_instance
        if _ltp_instance is None:
            _ltp_instance = LTPSeg()

        # seg
        return _ltp_instance.seg(sentence, **kwargs)

    if mode == 'thulac':
        # init
        global _thulac_instance
        if _thulac_instance is None:
            _thulac_instance = ThulacSeg()

        # seg
        return _thulac_instance.seg(sentence, **kwargs)

    if mode == 'nlpir':
        # init
        global _nlpir_instance
        if _nlpir_instance is None:
            _nlpir_instance = NLPIRSeg()

        # seg
        return _nlpir_instance.seg(sentence, **kwargs)

    raise ValueError("Unknown mode: {}".format(mode))
