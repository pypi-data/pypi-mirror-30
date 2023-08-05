# Copyright 2018 Joseph Wright <joseph@cloudboss.co>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Utility functions related to strings.
"""

import random
import re
import string

import six


if six.PY2:
    uppercase = string.uppercase
else:
    uppercase = string.ascii_uppercase


def random_string(length, charset):
    """
    Return a random string of the given length from the
    given character set.

    :param int length: The length of string to return
    :param str charset: A string of characters to choose from
    :returns: A random string
    :rtype: str
    """
    n = len(charset)
    return ''.join(charset[random.randrange(n)] for _ in range(length))


def random_alphanum(length):
    """
    Return a random string of ASCII letters and digits.

    :param int length: The length of string to return
    :returns: A random string
    :rtype: str
    """
    charset = string.ascii_letters + string.digits
    return random_string(length, charset)


def random_hex(length):
    """
    Return a random hex string.

    :param int length: The length of string to return
    :returns: A random string
    :rtype: str
    """
    charset = ''.join(set(string.hexdigits.lower()))
    return random_string(length, charset)


def snake_to_camel(stringue):
    """
    Convert a "snake case" string to a "camel case" string.

    :param str stringue: The string to convert
    :returns: A camel case string
    :rtype: str

    :Example:

    ::

      >>> snake_to_camel('snake_to_camel')
      'snakeToCamel'
    """
    return _thing_to_camel(stringue, '_')


def kebab_to_camel(stringue):
    """
    Convert a "kebab case" string to a "camel case" string.

    :param str stringue: The string to convert
    :returns: A camel case string
    :rtype: str

    :Example:

    ::

      >>> kebab_to_camel('kebab-to-camel')
      'kebabToCamel'
    """
    return _thing_to_camel(stringue, '-')


def snake_to_pascal(stringue):
    """
    Convert a "snake case" string to a "pascal case" string.

    :param str stringue: The string to convert
    :returns: A pascal case string
    :rtype: str

    :Example:

    ::

      >>> snake_to_pascal('snake_to_pascal')
      'SnakeToPascal'
    """
    return _thing_to_pascal(stringue, '_')


def kebab_to_pascal(stringue):
    """
    Convert a "kebab case" string to a "pascal case" string.

    :param str stringue: The string to convert
    :returns: A pascal case string
    :rtype: str

    :Example:

    ::

      >>> kebab_to_pascal('kebab-to-pascal')
      'KebabToPascal'
    """
    return _thing_to_pascal(stringue, '-')


def camel_to_snake(stringue):
    """
    Convert a "camel case" string to a "snake case" string.

    :param str stringue: The string to convert
    :returns: A snake case string
    :rtype: str

    :Example:

    ::

      >>> camel_to_snake('camelCaseString')
      'camel_case_string'
    """
    return _camel_to_thing(stringue, '_')


def camel_to_kebab(stringue):
    """
    Convert a "camel case" string to a "kebab case" string.

    :param str stringue: The string to convert
    :returns: A kebab case string
    :rtype: str

    :Example:

    ::

      >>> camel_to_kebab('camelCaseString')
      'camel-case-string'
    """
    return _camel_to_thing(stringue, '-')


def snake_to_camel_obj(obj):
    """
    Take a dictionary with string keys and recursively convert
    all keys from "snake case" to "camel case".

    The dictionary may contain lists as values, and any nested
    dictionaries within those lists will also be converted.

    :param object obj: The object to convert
    :returns: A new object with keys converted
    :rtype: object

    :Example:

    ::

      >>> obj = {
      ...     'dict_list': [
      ...         {'one_key': 123, 'two_key': 456},
      ...         {'three_key': 789, 'four_key': 456},
      ...     ],
      ...     'some_other_key': 'some_unconverted_value',
      ... }
      >>> snake_to_camel_obj(obj)
      {
          'dictList': [
              {'onekey': 123, 'twoKey': 456},
              {'fourKey': 456, 'threeKey': 789}
          ],
          'someOtherKey': 'some_unconverted_value'
      }
    """
    return format_obj_keys(obj, snake_to_camel)


def kebab_to_camel_obj(obj):
    """
    Take a dictionary with string keys and recursively convert
    all keys from "kebab case" to "camel case".

    The dictionary may contain lists as values, and any nested
    dictionaries within those lists will also be converted.

    :param object obj: The object to convert
    :returns: A new object with keys converted
    :rtype: object

    :Example:

    ::

      >>> obj = {
      ...     'dict-list': [
      ...         {'one-key': 123, 'two-key': 456},
      ...         {'three-key': 789, 'four-key': 456},
      ...     ],
      ...     'some-other-key': 'some-unconverted-value',
      ... }
      >>> kebab_to_camel_obj(obj)
      {
          'dictList': [
              {'oneKey': 123, 'twoKey': 456},
              {'fourKey': 456, 'threeKey': 789}
          ],
          'someOtherKey': 'some-unconverted-value'
      }
    """
    return format_obj_keys(obj, kebab_to_camel)


def snake_to_pascal_obj(obj):
    """
    Take a dictionary with string keys and recursively convert
    all keys from "snake case" to "pascal case".

    The dictionary may contain lists as values, and any nested
    dictionaries within those lists will also be converted.

    :param object obj: The object to convert
    :returns: A new object with keys converted
    :rtype: object

    :Example:

    ::

      >>> obj = {
      ...     'dict_list': [
      ...         {'one_key': 123, 'two_key': 456},
      ...         {'three_key': 789, 'four_key': 456},
      ...     ],
      ...     'some_other_key': 'some_value'
      ... }
      >>> snake_to_pascal_obj(obj)
      {
          'DictList': [
              {'OneKey': 123, 'TwoKey': 456},
              {'FourKey': 456, 'ThreeKey': 789}
          ],
          'SomeOtherKey': 'some_value'
      }
    """
    return format_obj_keys(obj, snake_to_pascal)


def kebab_to_pascal_obj(obj):
    """
    Take a dictionary with string keys and recursively convert
    all keys from "kebab case" to "pascal case".

    The dictionary may contain lists as values, and any nested
    dictionaries within those lists will also be converted.

    :param object obj: The object to convert
    :returns: A new object with keys converted
    :rtype: object

    :Example:

    ::

      >>> obj = {
      ...     'dict-list': [
      ...         {'one-key': 123, 'two-key': 456},
      ...         {'three-key': 789, 'four-key': 456},
      ...     ],
      ...     'some-other-key': 'some-unconverted-value',
      ... }
      >>> kebab_to_pascal_obj(obj)
      {
          'DictList': [
              {'OneKey': 123, 'TwoKey': 456},
              {'FourKey': 456, 'ThreeKey': 789}
          ],
          'SomeOtherKey': 'some-unconverted-value'
      }
    """
    return format_obj_keys(obj, kebab_to_pascal)


def camel_to_snake_obj(obj):
    """
    Take a dictionary with string keys and recursively convert
    all keys from "camel case" to "snake case".

    The dictionary may contain lists as values, and any nested
    dictionaries within those lists will also be converted.

    :param object obj: The object to convert
    :returns: A new object with keys converted
    :rtype: object

    :Example:

    ::

      >>> obj = {
      ...     'dictList': [
      ...         {'oneKey': 123, 'twoKey': 456},
      ...         {'threeKey': 789, 'fourKey': 456},
      ...     ],
      ...     'someOtherKey': 'someUnconvertedValue'
      ... }
      >>> camel_to_snake_obj(obj)
      {
          'dict_list': [
              {'one_key': 123, 'two_key': 456},
              {'four_key': 456, 'three_key': 789}
          ],
          'some_other_key': 'someUnconvertedValue'
      }
    """
    return format_obj_keys(obj, camel_to_snake)


def camel_to_kebab_obj(obj):
    """
    Take a dictionary with string keys and recursively convert
    all keys from "camel case" to "kebab case".

    The dictionary may contain lists as values, and any nested
    dictionaries within those lists will also be converted.

    :param object obj: The object to convert
    :returns: A new object with keys converted
    :rtype: object

    :Example:

    ::

      >>> obj = {
      ...     'dictList': [
      ...         {'oneKey': 123, 'twoKey': 456},
      ...         {'threeKey': 789, 'fourKey': 456},
      ...     ],
      ...     'someOtherKey': 'someUnconvertedValue'
      ... }
      >>> camel_to_kebab_obj(obj)
      {
          'dict-list': [
              {'one-key': 123, 'two-key': 456},
              {'four-key': 456, 'three-key': 789}
          ],
          'some-other-key': 'someUnconvertedValue'
      }
    """
    return format_obj_keys(obj, camel_to_kebab)


def format_obj_keys(obj, formatter):
    """
    Take a dictionary with string keys and recursively convert
    all keys from one form to another using the formatting function.

    The dictionary may contain lists as values, and any nested
    dictionaries within those lists will also be converted.

    :param object obj: The object to convert
    :param function formatter: The formatting function
      for keys, which takes and returns a string
    :returns: A new object with keys converted
    :rtype: object

    :Example:

    ::

      >>> obj = {
      ...     'dict-list': [
      ...         {'one-key': 123, 'two-key': 456},
      ...         {'threeKey': 789, 'four-key': 456},
      ...     ],
      ...     'some-other-key': 'some-unconverted-value'
      ... }
      >>> format_obj_keys(obj, lambda s: s.upper())
      {
          'DICT-LIST': [
              {'ONE-KEY': 123, 'TWO-KEY': 456},
              {'FOUR-KEY': 456, 'THREE-KEY': 789}
          ],
          'SOME-OTHER-KEY': 'some-unconverted-value'
      }
    """
    if type(obj) == list:
        return [format_obj_keys(o, formatter) for o in obj]
    elif type(obj) == dict:
        return {formatter(k): format_obj_keys(v, formatter)
                for k, v in obj.items()}
    else:
        return obj


def _camel_to_thing(stringue, delim):
    def case(s):
        return s.lower()

    def split(s):
        return re.split('([A-Z])', s)

    def joinexpr(s):
        return delim + s.lower() if s in uppercase else s.lower()
    return _thing_to_thing(stringue, case, split, joinexpr)


def _thing_to_camel(stringue, delim):
    def case(s):
        return s.lower()
    return _thing_to_camelish(stringue, delim, case)


def _thing_to_pascal(stringue, delim):
    def case(s):
        return s.capitalize()
    return _thing_to_camelish(stringue, delim, case)


def _thing_to_camelish(stringue, delim, case):
    def split(s):
        return s.split(delim)

    def joinexpr(s):
        return s[0].upper() + s[1:]
    return _thing_to_thing(stringue, case, split, joinexpr)


def _thing_to_thing(stringue, case, split, joinexpr):
    if len(stringue) in (0, 1):
        return case(stringue)
    parts = [p for p in split(stringue) if p]
    first = case(parts[0])
    rest = ''.join(joinexpr(part) for part in parts[1:])
    return first + rest
