# -*- coding: utf-8 -*-

"""
To Support NLP (Natural Language Processing) commonly used algorithms.
"""

# import .py files
from . import dependence
from . import fjconvert
from . import nertag
from . import postag
from . import segment
from . import sentence_split
from . import srl
from . import stopwords
# dependence.py
from .dependence import deparse
# import hanziconverter.py
from .fjconvert import FJConvert
# nertag.py
from .nertag import get_ner_mode
from .nertag import ner
from .nertag import set_ner_mode
# from postag.py
from .postag import get_pos_mode
from .postag import pos
from .postag import set_pos_mode
# import segment.py
from .segment import get_seg_mode
from .segment import seg
from .segment import set_seg_mode
# sentence_split.py
from .sentence_split import sen_split
# srl.py
from .srl import srlabel
# import stopwords.py
from .stopwords import ChineseStopWords
