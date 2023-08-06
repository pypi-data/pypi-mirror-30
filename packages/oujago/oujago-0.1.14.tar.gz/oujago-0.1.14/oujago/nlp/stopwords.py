# -*- coding: utf-8 -*-


import os
from oujago.utils.common import is_list
from oujago.utils import DATA_PATH


class ChineseStopWords(object):
    """Chinese Stop Words.

    You can specify what kind of stop words you will use.

    Parameters
    ==========
    modes : str
        If ``all`` or ``ALL``, integrate all stopwords in ``_files/stopwords_zh`` directory.
        If ``hit`` or ``HIT``, use "hit_stopwords.txt".
        If ``baidu`` or ``Baidu``, use "baidu_stopwords.txt".
        If ``normal``, use "normal_stopwords.txt".

    """

    def __init__(self, modes='all'):
        _base_path = os.path.join(DATA_PATH, 'stopwords_zh')
        self._stopwords = set()
        self._path_dict = {'all': os.listdir(_base_path),
                           'hit': 'hit_stopwords.txt',
                           'HIT': 'hit_stopwords.txt',
                           'baidu': "baidu_stopwords.txt",
                           'Baidu': "baidu_stopwords.txt",
                           'normal': "normal_stopwords.txt"}

        if not is_list(modes):
            modes = (modes,)

        for mode in modes:
            if mode not in self._path_dict:
                raise ValueError("Unknown mode: {}. Please specify mode "
                                 "using following types: {}.".format(mode, list(self._path_dict.keys())))

            paths = self._path_dict[mode]
            if not is_list(paths):
                paths = (paths,)

            for path in paths:
                with open(os.path.join(_base_path, path), encoding='gbk') as fin:
                    stopwords = [word.strip() for word in fin.readlines()]
                    self._stopwords |= set(stopwords)

    def check(self, word):
        """Check whether ``word`` is a stop word.

        Parameters
        ----------
        word : str

        Returns
        -------
        boolean
            True or False
        """
        if word in self._stopwords:
            return True
        else:
            return False


