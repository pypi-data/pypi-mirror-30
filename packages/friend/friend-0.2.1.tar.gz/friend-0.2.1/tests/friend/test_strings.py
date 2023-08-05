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
import random
import string
import unittest

from friend import strings


class StringsTests(unittest.TestCase):
    def test_random_string(self):
        charset = string.ascii_letters
        for _ in range(100):
            length = random.randint(25, 100)
            v1 = strings.random_string(length, charset)
            v2 = strings.random_string(length, charset)
            self.assertNotEqual(v1, v2)
            self.assertEqual(len(v1), length)

    def test_snake_to_camel(self):
        expectations = (
            ('', ''),
            ('0', '0'),
            ('100', '100'),
            ('A', 'a'),
            ('a', 'a'),
            ('a_b_c', 'aBC'),
            ('a_and_b_and_c', 'aAndBAndC'),
            ('z_z', 'zZ'),
            ('c_0', 'c0'),
            ('_c_0', 'c0'),
            ('camel_case_stringue', 'camelCaseStringue'),
        )
        for snake, camel in expectations:
            self.assertEqual(strings.snake_to_camel(snake), camel)

    def test_kebab_to_camel(self):
        expectations = (
            ('', ''),
            ('0', '0'),
            ('100', '100'),
            ('A', 'a'),
            ('a', 'a'),
            ('a-b-c', 'aBC'),
            ('a-and-b-and-c', 'aAndBAndC'),
            ('z-z', 'zZ'),
            ('c-0', 'c0'),
            ('-c-0', 'c0'),
            ('camel-case-stringue', 'camelCaseStringue'),
        )
        for kebab, camel in expectations:
            self.assertEqual(strings.kebab_to_camel(kebab), camel)

    def test_snake_to_pascal(self):
        expectations = (
            ('', ''),
            ('0', '0'),
            ('100', '100'),
            ('A', 'A'),
            ('a', 'A'),
            ('a_b_c', 'ABC'),
            ('a_and_b_and_c', 'AAndBAndC'),
            ('z_z', 'ZZ'),
            ('c_0', 'C0'),
            ('_c_0', 'C0'),
            ('pascal_case_stringue', 'PascalCaseStringue'),
        )
        for snake, pascal in expectations:
            self.assertEqual(strings.snake_to_pascal(snake), pascal)

    def test_kebab_to_pascal(self):
        expectations = (
            ('', ''),
            ('0', '0'),
            ('100', '100'),
            ('A', 'A'),
            ('a', 'A'),
            ('a-b-c', 'ABC'),
            ('a-and-b-and-c', 'AAndBAndC'),
            ('z-z', 'ZZ'),
            ('c-0', 'C0'),
            ('-c-0', 'C0'),
            ('pascal-case-stringue', 'PascalCaseStringue'),
        )
        for kebab, pascal in expectations:
            self.assertEqual(strings.kebab_to_pascal(kebab), pascal)

    def test_camel_to_snake(self):
        expectations = (
            ('', ''),
            ('0', '0'),
            ('100', '100'),
            ('A', 'a'),
            ('AAA', 'a_a_a'),
            ('a', 'a'),
            ('aAndBAndC', 'a_and_b_and_c'),
            ('zZ', 'z_z'),
            ('c0', 'c0'),
            ('snakeCaseStringue', 'snake_case_stringue'),
        )
        for camel, snake in expectations:
            self.assertEqual(strings.camel_to_snake(camel), snake)

    def test_camel_to_kebab(self):
        expectations = (
            ('', ''),
            ('0', '0'),
            ('100', '100'),
            ('A', 'a'),
            ('AAA', 'a-a-a'),
            ('a', 'a'),
            ('aAndBAndC', 'a-and-b-and-c'),
            ('zZ', 'z-z'),
            ('c0', 'c0'),
            ('kebabCaseStringue', 'kebab-case-stringue'),
        )
        for camel, kebab in expectations:
            self.assertEqual(strings.camel_to_kebab(camel), kebab)

    def test_snake_to_camel_obj(self):
        random_value = strings.random_alphanum(25)
        expectations = (
            (
                {}, {},
            ),
            (
                {'0': []}, {'0': []},
            ),
            (
                {'camel_case': random_value},
                {'camelCase': random_value}
            ),
            (
                {'a': [{'a_a': random_value}, {'b_b': random_value}]},
                {'a': [{'aA': random_value}, {'bB': random_value}]},
            ),
        )
        for snake_obj, camel_obj in expectations:
            copy = snake_obj.copy()
            converted = strings.snake_to_camel_obj(snake_obj)
            self.assertEqual(converted, camel_obj)
            self.assertEqual(snake_obj, copy)

    def test_kebab_to_camel_obj(self):
        random_value = strings.random_alphanum(25)
        expectations = (
            (
                {}, {},
            ),
            (
                {'0': []}, {'0': []},
            ),
            (
                {'camel-case': random_value},
                {'camelCase': random_value}
            ),
            (
                {'a': [{'a-a': random_value}, {'b-b': random_value}]},
                {'a': [{'aA': random_value}, {'bB': random_value}]},
            ),
        )
        for kebab_obj, camel_obj in expectations:
            copy = kebab_obj.copy()
            converted = strings.kebab_to_camel_obj(kebab_obj)
            self.assertEqual(converted, camel_obj)
            self.assertEqual(kebab_obj, copy)

    def test_snake_to_pascal_obj(self):
        random_value = strings.random_alphanum(25)
        expectations = (
            (
                {}, {},
            ),
            (
                {'0': []}, {'0': []},
            ),
            (
                {'pascal_case': random_value},
                {'PascalCase': random_value}
            ),
            (
                {'a': [{'a_a': random_value}, {'b_b': random_value}]},
                {'A': [{'AA': random_value}, {'BB': random_value}]},
            ),
        )
        for snake_obj, pascal_obj in expectations:
            copy = snake_obj.copy()
            converted = strings.snake_to_pascal_obj(snake_obj)
            self.assertEqual(converted, pascal_obj)
            self.assertEqual(snake_obj, copy)

    def test_kebab_to_pascal_obj(self):
        random_value = strings.random_alphanum(25)
        expectations = (
            (
                {}, {},
            ),
            (
                {'0': []}, {'0': []},
            ),
            (
                {'pascal-case': random_value},
                {'PascalCase': random_value}
            ),
            (
                {'a': [{'a-a': random_value}, {'b-b': random_value}]},
                {'A': [{'AA': random_value}, {'BB': random_value}]},
            ),
        )
        for kebab_obj, pascal_obj in expectations:
            copy = kebab_obj.copy()
            converted = strings.kebab_to_pascal_obj(kebab_obj)
            self.assertEqual(converted, pascal_obj)
            self.assertEqual(kebab_obj, copy)

    def test_camel_to_snake_obj(self):
        random_value = strings.random_alphanum(25)
        expectations = (
            (
                {}, {},
            ),
            (
                {'0': []}, {'0': []},
            ),
            (
                {'snakeCase': random_value},
                {'snake_case': random_value}
            ),
            (
                {'a': [{'aA': random_value}, {'bB': random_value}]},
                {'a': [{'a_a': random_value}, {'b_b': random_value}]},
            ),
        )
        for camel_obj, snake_obj in expectations:
            copy = camel_obj.copy()
            converted = strings.camel_to_snake_obj(camel_obj)
            self.assertEqual(converted, snake_obj)
            self.assertEqual(camel_obj, copy)

    def test_camel_to_kebab_obj(self):
        random_value = strings.random_alphanum(25)
        expectations = (
            (
                {}, {},
            ),
            (
                {'0': []}, {'0': []},
            ),
            (
                {'kebabCase': random_value},
                {'kebab-case': random_value}
            ),
            (
                {'a': [{'aA': random_value}, {'bB': random_value}]},
                {'a': [{'a-a': random_value}, {'b-b': random_value}]},
            ),
        )
        for camel_obj, kebab_obj in expectations:
            copy = camel_obj.copy()
            converted = strings.camel_to_kebab_obj(camel_obj)
            self.assertEqual(converted, kebab_obj)
            self.assertEqual(camel_obj, copy)

    def test_format_obj_keys(self):
        random_value = strings.random_alphanum(25)

        def formatter(s):
            return '-' + s.upper() + '-'

        expectations = (
            (
                {}, {},
            ),
            (
                {'0': []}, {'-0-': []},
            ),
            (
                {'sdjfljdsf': random_value},
                {'-SDJFLJDSF-': random_value}
            ),
            (
                {'a': [{'aA': random_value}, {'bB': random_value}]},
                {'-A-': [{'-AA-': random_value}, {'-BB-': random_value}]},
            ),
        )
        for obj, formatted_obj in expectations:
            copy = obj.copy()
            converted = strings.format_obj_keys(obj, formatter)
            self.assertEqual(converted, formatted_obj)
            self.assertEqual(obj, copy)
