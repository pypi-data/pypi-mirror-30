# -*- coding:utf-8 -*-

from datetime import datetime


def now():
    """Get the format time of NOW.

    For example:

        >>> from oujago.utils.time import now
        >>> now()
        "2017-04-26-16-44-56"

    Returns
    -------
    str
    """
    return datetime.now().strftime('%Y-%m-%d-%H-%M-%S')


def today():
    """Get the format time of TODAY.

    For example:

        >>> from oujago.utils.time import today
        >>> today()
        "2017-04-26"

    Returns
    -------
    str
    """
    return datetime.now().strftime('%Y-%m-%d')


def time_format(total_time):
    """Change the total time into the normal time format.

    For examples:

        >>> from oujago.utils.time import time_format
        >>> time_format(36)
        "36 s"
        >>> time_format(90)
        "1 min 30 s "
        >>> time_format(5420)
        "1 h 30 min 20 s"
        >>> time_format(20.5)
        "20 s 500 ms"

    Parameters
    ----------
    total_time : float or str
        The total seconds of the time. 

    Returns
    -------
    str
        The format string about time.
    """
    if total_time < 0:
        raise ValueError
    if total_time == 0:
        return ""
    if total_time < 1:
        return "{} ms".format(int(total_time * 1000))
    if total_time < 60:
        sec_integer = int(total_time)
        sec_decimal = total_time - sec_integer
        return ("{} s {}".format(sec_integer, time_format(sec_decimal))).strip()
    if total_time < 3600:
        min_integer = int(total_time / 60)
        sec_decimal = total_time - min_integer * 60
        return ("{} min {}".format(min_integer, time_format(sec_decimal))).strip()
    if total_time < 86400:
        hour_integer = int(total_time / 60 / 60)
        sec_decimal = total_time - hour_integer * 60 * 60
        return ("{} h {}".format(hour_integer, time_format(sec_decimal))).strip()
    if total_time >= 86400:
        day_integer = int(total_time / 60 / 60 / 24)
        sec_decimal = total_time - day_integer * 60 * 60 * 24
        return ("{} d {}".format(day_integer, time_format(sec_decimal))).strip()
    raise ValueError
