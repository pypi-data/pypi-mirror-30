# -*- coding: utf-8 -*-

import os


def join(*args, **kwargs):
    """Join two (or more) paths.
    
    Parameters
    ----------
    args : 
        paths.
    
    kwargs : 
        abs : If True, Return the absolute version of a path.
    
    Returns
    -------
        
        joined path.
    
    """
    path = os.path.join(*args)
    if kwargs['abs']:
        path = os.path.abspath(path)
    return path


def mkdirs(path):
    """Create a directory.
    
    If dir_fd is not None, it should be a file descriptor open to a directory,
      and path should be relative; path will then be relative to that directory.
    dir_fd may not be implemented on your platform.
      If it is unavailable, using it will raise a NotImplementedError.
    
    The mode argument is ignored on Windows.
    
    Parameters
    ----------
    path : str
    
    Returns
    -------
    boolean
        True or False
    """
    path = join(os.getcwd(), path)
    if not os.path.exists(path):
        os.mkdir(path)
        return True
    else:
        return False


def write_xls():
    pass


