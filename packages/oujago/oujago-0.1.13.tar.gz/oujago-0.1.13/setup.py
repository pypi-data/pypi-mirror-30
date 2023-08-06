# -*- encoding: utf-8 -*-

import io
import os
import re

from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

try:
    # obtain version string from __init__.py
    with open(os.path.join(here, 'oujago', '__init__.py'), 'r') as f:
        init_py = f.read()
    version = re.search('__version__ = "(.*)"', init_py).groups()[0]
except Exception:
    version = ''

try:
    # obtain long description from README and CHANGES
    with io.open(os.path.join(here, 'README.rst'), 'r', encoding='utf-8') as f:
        README = f.read()
    with io.open(os.path.join(here, 'CHANGES.rst'), 'r', encoding='utf-8') as f:
        CHANGES = f.read()
except IOError:
    README = CHANGES = ''

setup(name='oujago',
      version=version,
      description='Coding Makes Life Easier',
      long_description="\n\n".join([README, CHANGES]),
      author='Chao-Ming Wang',
      packages=find_packages(),
      author_email='oujago@gmail.com',
      url='https://github.com/oujago/oujago',
      install_requires=[
          'numpy',
      ],
)
