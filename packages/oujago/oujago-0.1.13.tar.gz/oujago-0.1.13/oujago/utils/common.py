# -*- coding:utf-8 -*-


from sys import version


def is_iterable(obj):
    """Check weather this ``object`` is an iterable.
    
    There are two kinds of implementations. The other is using ``collections.Iterable``. [1]_
    
    .. code-blocks:: python
    
        import collections
        
        def is_iterable(obj):
            if isinstance(obj, collections.Iterable):
                return True
            else:
                return False
    
    Checking for :meth:`__iter__` works on sequence types, but it would fail on 
    e.g. strings in `Python 2`. The :meth:`iter` built-in checks for the :meth:`__iter__` 
    method or in the case of strings the :meth:`__getitem__` method. In `Python 2`, to check 
    if an object is "list like" and not "string like" then the key is the attributes 
    :meth:`__getitem__` and :meth:`__iter__`. [2]_
    
    >>> hasattr([1,2,3,4], '__iter__')
    >>> True
    >>> hasattr((1,2,3,4), '__iter__')
    >>> True
    >>> hasattr(u"hello", '__iter__')
    >>> False
    >>> hasattr(u"hello", '__getitem__')
    >>> True
    
    Parameters
    ----------
    obj : object
       
    Returns
    -------
    boolean
        True or False.
        
    References
    ----------
    
    .. [1] http://stackoverflow.com/questions/19919314/how-to-check-isinstance-of-iterable-in-python
    .. [2] http://stackoverflow.com/questions/1952464/in-python-how-do-i-determine-if-an-object-is-iterable
    
    """

    # python 3
    if hasattr(obj, '__iter__'):
        return True

    # python 2
    if hasattr(obj, '__getitem__'):
        return True

    return False


def is_list(obj):
    """Check weather this ``object`` is a list or tuple.
    
    Parameters
    ----------
    obj : object
        
    Returns
    -------
    boolean
        True of False
    """
    if type_(obj) in ['list', 'tuple']:
        return True
    else:
        return False


def type_(obj):
    """Get the type of given object.
    
    Parameters
    ----------
    obj : Any object.
    
    Returns
    -------
    str
    """

    return obj.__class__.__name__


def hostname():
    """Get the computer system host name.
    
    There are two methods. First is, use ``socket`` and its ``gethostname()`` functionality. 
    This will get the hostname of the computer where the Python interpreter is running:

    >>> import socket
    >>> print(socket.gethostname())
    
    Another is use ``platform``.
    
    >>> import platform
    >>> platform.node()
    
    Returns
    -------
    str 
        name of host.
    
    """
    import platform
    return platform.node()


def system():
    """Returns the system/OS name, e.g. 'Linux', 'Windows' or 'Java'.

    An empty string is returned if the value cannot be determined.
    
    Returns
    -------
    str 
        the system name.
    """
    import platform
    return platform.system()


def is_py3():
    """Judge python version.

    Returns:
    bool
        Python 3 is `True`, else `False`.
    """
    return int(version[0]) == 3


def is_py2():
    """Judge python version.

    Returns:
    bool
        Python 2 is `True`, else `False`.
    """
    return int(version[0]) == 2


def u(s, encoding='utf-8', errors='strict'):
    """Ensure s is properly unicode.

    Parameters
    ----------
    s : str
        To process strings.
    encoding : str
        Encoding type.
    errors : str
        Error type.

    References
    ----------
    ..[1] https://github.com/proycon/pynlpl/blob/master/pynlpl/common.py

    """
    # wrapper for python 2.6/2.7,
    if version < '3':
        # ensure the object is unicode
        if isinstance(s, unicode):
            return s
        else:
            return unicode(s, encoding, errors=errors)
    else:
        # will work on byte arrays
        if isinstance(s, str):
            return s
        else:
            return str(s, encoding, errors=errors)


def b(s):
    """ensure s is bytestring

    Parameters
    ----------
    s : str
        To process strings.

    References
    ----------
    ..[1] https://github.com/proycon/pynlpl/blob/master/pynlpl/common.py
    """
    if version < '3':
        # ensure the object is unicode
        if isinstance(s, str):
            return s
        else:
            return s.encode('utf-8')
    else:
        # will work on byte arrays
        if isinstance(s, bytes):
            return s
        else:
            return s.encode('utf-8')
