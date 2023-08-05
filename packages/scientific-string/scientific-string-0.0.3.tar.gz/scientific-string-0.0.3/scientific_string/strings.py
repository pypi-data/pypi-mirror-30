#!/usr/bin/env python3
"""
:mod:`strings` -- Toolkit for strings
=====================================

.. module strings
   :platform: Unix, Windows, Mac, Linux
   :synopsis: Analyze text and convert strings.
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

import re
from typing import *

# ========================================= What can be exported? =========================================
__all__ = ['strings_to_', 'strings_to_integers', 'strings_to_floats', 'string_to_double_precision_float',
           'string_to_general_float', 'match_one_string', 'match_one_pattern', 'is_string_like', 'all_string_like']


def strings_to_(strings: Iterable[str], f: Callable) -> Iterable[Any]:
    """
    Convert a list of strings to a list of certain form, specified by *f*.

    :param strings: a list of string
    :param f: a function that converts your string
    :return: type undefined, but specified by `to_type`

    .. doctest::

        >>> strings_to_(['0.333', '0.667', '0.250'], float)
        [0.333, 0.667, 0.25]
    """
    if not all_string_like(strings):
        raise TypeError('All have to be strings!')
    # ``type(strs)`` is the container of *strs*.
    return type(strings)(map(f, strings))


def strings_to_integers(strings: Iterable[str]) -> Iterable[int]:
    """
    Convert a list of strings to a list of integers.

    :param strings: a list of string
    :return: a list of converted integers

    .. doctest::

        >>> strings_to_integers(['1', '1.0', '-0.2'])
        [1, 1, 0]
    """
    return strings_to_(strings, lambda x: int(float(x)))


def strings_to_floats(strings: Iterable[str]) -> Iterable[float]:
    """
    Convert a list of strings to a list of floats.

    :param strings: a list of string
    :return: a list of converted floats

    .. doctest::

        >>> strings_to_floats(['1', '1.0', '-0.2'])
        [1.0, 1.0, -0.2]
    """
    return strings_to_(strings, float)


def string_to_double_precision_float(s: str) -> float:
    """
    Double precision float in Fortran file will have form 'x.ydz' or 'x.yDz', this cannot be convert directly to float
    by Python ``float`` function, so I wrote this function to help conversion. For example,

    :param s: a string denoting a double precision number
    :return: a Python floating point number

    .. doctest::

        >>> string_to_double_precision_float('1d-82')
        1e-82
        >>> string_to_double_precision_float('1.0D-82')
        1e-82
        >>> string_to_double_precision_float('0.8D234')
        8e+233
        >>> string_to_double_precision_float('.8d234')
        8e+233
    """
    first, second, exponential = re.match(
        "(-?\d*)\.?(-?\d*)d(-?\d+)", s, re.IGNORECASE).groups()
    return float(first + '.' + second + 'e' + exponential)


def string_to_general_float(s: str) -> float:
    """
    Convert a string to corresponding single or double precision scientific number.

    :param s: a string could be '0.1', '1e-5', '1.0D-5', or any other validated number
    :return: a float or raise an error

    .. doctest::

        >>> string_to_general_float('1.0D-5')
        1e-05
        >>> string_to_general_float('1Dx')
        Traceback (most recent call last):
            ...
        ValueError: The string '1Dx' does not corresponds to a double precision number!
        >>> string_to_general_float('.8d234')
        8e+233
        >>> string_to_general_float('0.1')
        0.1
    """
    if 'D' in s.upper():  # Possible double precision number
        try:
            return string_to_double_precision_float(s)
        except ValueError:
            raise ValueError(
                "The string '{0}' does not corresponds to a double precision number!".format(s))
    else:
        return float(s)


def match_one_string(pattern: str, s: str, *args):
    """
    Make sure you know only none or one string will be matched! If you are not sure, use `match_one_pattern` instead.

    :param pattern:
    :param s:
    :param args:
    :return:

    .. doctest::

        >>> p = "\d+"
        >>> s = "abc 123 def"
        >>> match_one_string(p, s, int)
        123
        >>> print(match_one_string(p, "abc"))
        Pattern "\d+" not found, or more than one found in string abc!
        None
        >>> print(match_one_string(p, "abc 123 def 456"))
        Pattern "\d+" not found, or more than one found in string abc 123 def 456!
        None
    """
    try:
        # `match` is either an empty list or a list of string.
        match, = re.findall(pattern, s)
        if len(args) == 0:  # If no wrapper argument is given, return directly the matched string
            return match
        elif len(args) == 1:  # If wrapper argument is given, i.e., not empty, then apply wrapper to the match
            wrapper, = args
            return wrapper(match)
        else:
            raise TypeError(
                'Multiple wrappers are given! Only one should be given!')
    except ValueError:
        print("Pattern \"{0}\" not found, or more than one found in string {1}!".format(
            pattern, s))


def match_one_pattern(pattern: str, s: str, *args: Optional[Callable], **flags):
    """
    Find a pattern in a certain string. If found and a wrapper is given, then return the wrapped matched-string; if no
    wrapper is given, return the pure matched string. If no match is found, return None.

    :param pattern: a pattern, can be a string or a regular expression
    :param s: a string
    :param args: at most 1 argument can be given
    :param flags: the same flags as ``re.findall``'s
    :return:

    .. doctest::

        >>> p = "\d+"
        >>> s = "abc 123 def 456"
        >>> match_one_pattern(p, s)
        ['123', '456']
        >>> match_one_pattern(p, s, int)
        [123, 456]
        >>> match_one_pattern(p, "abc 123 def")
        ['123']
        >>> print(match_one_pattern('s', 'abc'))
        Pattern "s" not found in string abc!
        None
        >>> match_one_pattern('s', 'Ssa', flags=re.IGNORECASE)
        ['S', 's']
    """
    match: Optional[List[str]] = re.findall(pattern, s,
                                            **flags)  # `match` is either an empty list or a list of strings.
    if match:
        if len(args) == 0:  # If no wrapper argument is given, return directly the matched string
            return match
        elif len(args) == 1:  # If wrapper argument is given, i.e., not empty, then apply wrapper to the match
            wrapper, = args
            return [wrapper(m) for m in match]
        else:
            raise TypeError(
                'Multiple wrappers are given! Only one should be given!')
    else:  # If no match is found
        print("Pattern \"{0}\" not found in string {1}!".format(pattern, s))
        return None


def is_string_like(obj: object) -> bool:
    """
    Check if the object is a string.

    :param obj: The object to check.
    :return: Whether *obj* is a string or not.

    .. doctest::

        >>> is_string_like('foo')
        True
        >>> is_string_like(1)
        False
    """
    return isinstance(obj, str)


def all_string_like(iterable: Iterable[object]) -> bool:
    """
    If any element of an iterable is not a string, return `True`.

    :param iterable: Can be a set, a tuple, a list, etc.
    :return: Whether any element of an iterable is not a string.

    .. doctest::

        >>> all_string_like(['a', 'b', 'c', 3])
        False
        >>> all_string_like(('a', 'b', 'c', 'd'))
        True
    """
    return all(is_string_like(_) for _ in iterable)
