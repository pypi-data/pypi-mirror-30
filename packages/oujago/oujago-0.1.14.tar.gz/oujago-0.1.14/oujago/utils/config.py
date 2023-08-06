# -*- coding: utf-8 -*-

import json
import os
import sys


def set_config(configuration):
    """Configuration setting.

    Parameters
    ----------
    configuration : dict
        Global configuration.
    """
    with open(_config_path, 'w') as f:
        f.write(json.dumps(configuration, indent=4))


# Step 1: define global data path
DATA_PATH = None

# Step 2: define oujago base directory
_oujago_base_dir = os.path.expanduser('~')
if not os.access(_oujago_base_dir, os.W_OK):
    _oujago_base_dir = '/tmp'

_oujago_dir = os.path.join(_oujago_base_dir, '.oujago')
if not os.path.exists(_oujago_dir):
    os.makedirs(_oujago_dir)

# Step 3: define oujago configuration directory
_config_path = os.path.expanduser(os.path.join(_oujago_dir, 'oujago.json'))
if os.path.exists(_config_path):
    _config = json.load(open(_config_path))
else:
    _config = {
        'data_path': None
    }
    set_config(_config)

# Step 4: Initialize global data path
if 'OUJAGO' in os.environ:
    DATA_PATH = os.environ.get('OUJAGO')
elif _config['data_path'] is not None:
    DATA_PATH = _config['data_path']
else:
    sys.stderr.write("WARNING: Can't find DATA_PATH.\n"
                     "1, You can add 'OUJAGO' variable to PATH environment by 'export OUJAGO=<DATA_PATH>'.\n"
                     "2, Or, you can use 'oujago.utils.set_data_path(<DATA_PATH>)' to set global model path.\n")


def get_config():
    """
    Publicly accessible method for configuration.

    Returns
    -------
    dict
        Global configuration.
    """
    return _config


def set_data_path(data_path):
    """Global `DATA_PATH` setting.

    Parameters
    ----------
    data_path : str
        Oujago needed model path.
    """
    global _config
    global DATA_PATH
    if os.path.exists(data_path):
        DATA_PATH = data_path

        _config['data_path'] = DATA_PATH
        set_config(_config)
    else:
        sys.stderr.write("WARNING: not a valid path, '{}' does not exist.".format(data_path))


def get_data_path():
    """Publicly accessible method for `DATA_PATH`.

    Returns
    -------
    str
        Global `DATA_PATH`.
    """
    global DATA_PATH
    return DATA_PATH

