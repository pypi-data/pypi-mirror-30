# -*- coding: utf-8 -*-

"""
Named Entity Recognition

"""


import re

try:
    from pyltp import SentenceSplitter
except ImportError:
    SentenceSplitter = None

from oujago.utils import LTPInstallError


_mode = 'raw'
_support_modes = ['ltp', 'raw']


def sen_split(text, mode=_mode, **kwargs):
    """Sentence Split.

    Parameters
    ----------
    text : str
        To split text.
    mode : str
        Sentence split mode. Must in ``_support_modes``.

    Returns
    -------
    list
        A list of sentences.
    """

    if mode == 'raw':
        return re.compile(".+?[。!?！？；\n]+").findall(text)

    # LTP
    if mode == 'ltp':
        if SentenceSplitter is None:
            raise LTPInstallError()
        return list(SentenceSplitter.split(text))

    raise ValueError("Unknown mode: {}".format(mode))


