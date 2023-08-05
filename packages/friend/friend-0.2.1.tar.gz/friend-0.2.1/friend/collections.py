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


def select_dict(coll, key, value):
    """
    Given an iterable of dictionaries, return the dictionaries
    where the values at a given key match the given value.
    If the value is an iterable of objects, the function will
    consider any to be a match.

    This is especially useful when calling REST APIs which
    return arrays of JSON objects. When such a response is
    converted to a Python list of dictionaries, it may be
    easily filtered using this function.

    :param iter coll: An iterable containing dictionaries
    :param obj key: A key to search in each dictionary
    :param value: A value or iterable of values to match
    :type value: obj or iter
    :returns: A list of dictionaries matching the query
    :rtype: list

    :Example:

    ::

      >>> dicts = [
      ...    {'hi': 'bye'},
      ...    {10: 2, 30: 4},
      ...    {'hi': 'hello', 'bye': 'goodbye'},
      ... ]
      >>> select_dict(dicts, 'hi', 'bye')
      [{'hi': 'bye'}]
      >>> select_dict(dicts, 'hi', ('bye', 'hello'))
      [{'hi': 'bye'}, {'hi': 'hello', 'bye': 'goodbye'}]
    """
    if getattr(value, '__iter__', None):
        iterable = value
    else:
        iterable = [value]
    return [v for v in coll if key in v and v[key] in iterable]
