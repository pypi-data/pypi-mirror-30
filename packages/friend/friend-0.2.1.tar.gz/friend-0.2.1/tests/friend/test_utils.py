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
import unittest

import mock

from friend import strings
from friend import utils


class UtilsTests(unittest.TestCase):
    def test_retry_ex_no_failures(self):
        state = [0]
        ret = strings.random_alphanum(20)

        def wont_fail():
            if state[0] is None:
                state[0] += 1
                raise RuntimeError('Uh oh!')
            return ret

        self.assertEqual(utils.retry_ex(wont_fail), ret)
        self.assertEqual(state[0], 0)

    def test_retry_ex_single_retry(self):
        state = [0]
        ret = strings.random_alphanum(20)

        def will_recover_once():
            if state[0] == 0:
                state[0] += 1
                raise RuntimeError('Uh oh!')
            return ret

        self.assertEqual(utils.retry_ex(will_recover_once), ret)
        self.assertEqual(state[0], 1)

    def test_retry_ex_multiple_retries(self):
        state = [0]
        ret = strings.random_alphanum(20)
        count = random.randint(1, 6)

        def will_recover_count_times():
            if state[0] < count:
                state[0] += 1
                raise RuntimeError('Uh oh!')
            return ret

        self.assertEqual(
            utils.retry_ex(will_recover_count_times, times=count), ret
        )
        self.assertEqual(state[0], count)

    def test_retry_bool_no_failures(self):
        state = [0]

        def wont_fail():
            if state[0] is None:
                state[0] += 1
                return False
            return True

        self.assertEqual(utils.retry_bool(wont_fail), True)
        self.assertEqual(state[0], 0)

    def test_retry_bool_single_retry(self):
        state = [0]

        def will_recover_once():
            if state[0] == 0:
                state[0] += 1
                return False
            return True

        self.assertEqual(utils.retry_bool(will_recover_once), True)
        self.assertEqual(state[0], 1)

    def test_retry_bool_multiple_retries(self):
        state = [0]
        count = random.randint(1, 6)

        def will_recover_count_times():
            if state[0] < count:
                state[0] += 1
                return False
            return True

        self.assertEqual(
            utils.retry_bool(will_recover_count_times, times=count), True
        )
        self.assertEqual(state[0], count)

    def test_retry_ex_no_recover(self):
        state = [0]
        count = 5
        message = strings.random_alphanum(20)

        def wont_recover():
            if state[0] < count:
                state[0] += 1
                raise RuntimeError(message)
            return 'wont_return_this'

        with self.assertRaises(RuntimeError) as r:
            utils.retry_ex(wont_recover, times=count-1)
        self.assertEqual(str(r.exception), message)
        self.assertEqual(state[0], count)

    def test_retry_bool_no_recover(self):
        state = [0]
        count = 5

        def wont_recover():
            if state[0] < count:
                state[0] += 1
                return False
            return True

        self.assertEqual(
            utils.retry_bool(wont_recover, times=count-1), False
        )
        self.assertEqual(state[0], count)

    def test_retryable_recover(self):
        state = [0]

        @utils.retryable()
        def will_recover():
            if state[0] == 0:
                state[0] += 1
                raise RuntimeError('Uh oh!')
            return 100

        self.assertEqual(will_recover(), 100)
        self.assertEqual(state[0], 1)

    def test_retryable_recover_times(self):
        retry_times = 5
        state = [0]

        @utils.retryable(times=retry_times)
        def will_recover():
            if state[0] < retry_times:
                state[0] += 1
                raise RuntimeError('Uh oh!')
            return 100

        self.assertEqual(will_recover(), 100)
        self.assertEqual(state[0], retry_times)

    def test_retryable_no_recover(self):
        retry_times = 3
        state = [0]

        @utils.retryable()
        def wont_recover():
            state[0] += 1
            raise RuntimeError('Uh oh!')

        with self.assertRaises(RuntimeError):
            wont_recover()
        self.assertEqual(state[0], retry_times+1)

    def test_ensure_environment(self):
        expectations = (
            (
                [],
                {'A': 'B', 'C': 'D'},
                [],
                None,
            ),
            (
                [],
                {},
                [],
                None
            ),
            (
                ['A'],
                {'A': 'B', 'C': 'D'},
                [],
                None,
            ),
            (
                ['A', 'C'],
                {'A': 'B', 'C': 'D'},
                [],
                None,
            ),
            (
                ['E'],
                {'A': 'B', 'C': 'D'},
                ['E'],
                utils.IncompleteEnvironment,
            ),
            (
                ['A', 'B'],
                {},
                ['A', 'B'],
                utils.IncompleteEnvironment,
            ),
            (
                ['A', 'C'],
                {'A': 'B'},
                ['C'],
                utils.IncompleteEnvironment,
            ),
        )
        for required, env, missing, error in expectations:
            with mock.patch('os.environ', env):
                if not error:
                    out_env = utils.ensure_environment(required)
                    self.assertEqual(out_env, env)
                else:
                    with self.assertRaises(error) as r:
                        utils.ensure_environment(required)
                    variables = ', '.join(missing)
                    message = 'Environment variables not set: {}'.format(
                        variables)
                    self.assertEqual(str(r.exception), message)
                    self.assertEqual(r.exception.variables, missing)
