# Copyright 2018 ONES.AI

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import json
import os
import time
import traceback
import types
import unittest
from collections import defaultdict

try:
    from urllib.parse import parse_qs, urlparse, urlunparse
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urlparse import parse_qs, urlparse, urlunparse
    from urllib2 import urlopen, Request, HTTPError

__all__ = ['OnesTestRunner']

class OnesTestRunner(object):
    """ONES Pipeline test runner implementation which wraps another runner and sends test result to url.

    If runner is None, a TextTestRunner is created and used. 
    """
    def __init__(self, url=None, runner=None):
        self.url = os.getenv('ONES_PIPELINE_URL') if url is None else url
        self.runner = unittest.TextTestRunner() if runner is None else runner
        self._executions = defaultdict(dict)
        self._status = 'unknown'

    def run(self, test):
        if not self.url:
            self.runner.run(test)
            return

        self._override_run(test)
        
        start_time = self._current_seconds()
        self.runner.run(test)
        finish_time = self._current_seconds()

        for id, run in self._executions.items():
            run['id'] = id
            run['name'] = id
            run['language'] = 'python'
            run['framework'] = 'unittest'
        
        self._executions.values()
        data = {
            'action': 'stage',
            'stage': {
                'type': 'test',
                'name': 'test',
                'start_time': start_time,
                'finish_time': finish_time,
                'status': self._status,
            },
            'payload': {
                'test': {
                    'executions': list(self._executions.values())
                }
            }
        }
        self._request_ones_pipeline(self.url, data)

    def _override_run(self, test):
        origin = test.run
        def replacement(test_self, result):
            if result is None:
                result = unittest.TestResult()
            if not getattr(result, '_overridden_by_ones', False):
                self._override_start_test(result)
                self._override_stop_test(result)
                self._override_success_finisher(result, 'addSuccess', 'success')
                self._override_success_finisher(result, 'addUnexpectedSuccess', 'unexpected_success')
                self._override_failure_finisher(result, 'addFailure', 'failure')
                self._override_failure_finisher(result, 'addExpectedFailure', 'expected_failure')
                self._override_failure_finisher(result, 'addError', 'error')
                self._override_skip_finisher(result, 'addSkip', 'skip')
                setattr(result, '_overridden_by_ones', True)
            origin(result)
            self._status = 'success' if result.wasSuccessful() else 'failure'
        test.run = types.MethodType(replacement, test)

    def _override_start_test(self, result):
        origin = result.startTest
        def replacement(result_self, test):
            execution = self._executions[test.id()]
            execution['start_time'] = self._current_millis()
            execution['description'] = test.shortDescription()
            origin(test)
        result.startTest = types.MethodType(replacement, result)

    def _override_stop_test(self, result):
        origin = result.stopTest
        def replacement(result_self, test):
            origin(test)
            execution = self._executions[test.id()]
            execution['finish_time'] = self._current_millis()
        result.stopTest = types.MethodType(replacement, result)

    def _override_failure_finisher(self, result, finisher_name, label):
        origin = getattr(result, finisher_name, None)
        if origin is None:
            return
        def replacement(result_self, test, err):
            origin(test, err)
            execution = self._executions[test.id()]
            execution['result'] = label
            execution['message'] = self._build_error_message(err, test)
        setattr(result, finisher_name, types.MethodType(replacement, result))

    def _override_success_finisher(self, result, finisher_name, label):
        origin = getattr(result, finisher_name, None)
        if origin is None:
            return
        def replacement(result_self, test):
            origin(test)
            execution = self._executions[test.id()]
            execution['result'] = label
        setattr(result, finisher_name, types.MethodType(replacement, result))

    def _override_skip_finisher(self, result, finisher_name, label):
        origin = getattr(result, finisher_name, None)
        if origin is None:
            return
        def replacement(result_self, test, reason):
            origin(test, reason)
            execution = self._executions[test.id()]
            execution['result'] = label
            execution['message'] = reason
        setattr(result, finisher_name, types.MethodType(replacement, result))

    def _current_seconds(self):
        return int(round(time.time()))

    def _current_millis(self):
        return int(round(time.time() * 1000))

    def _build_error_message(self, err, test):
        exctype, value, tb = err
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next
        if exctype is test.failureException:
            length = self._count_relevant_tb_levels(tb)
            lines = traceback.format_exception(exctype, value, tb, length)
        else:
            lines = traceback.format_exception(exctype, value, tb)
        return ''.join(lines)

    def _is_relevant_tb_level(self, tb):
        return '__unittest' in tb.tb_frame.f_globals

    def _count_relevant_tb_levels(self, tb):
        length = 0
        while tb and not self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next
        return length

    def _request_ones_pipeline(self, pipeline_url, data):
        parts = urlparse(pipeline_url)
        query = parse_qs(parts.query)
        token = query.get('token', None)
        if not token:
            raise ValueError('invalid ones pipeline url: missing token')
        data['token'] = token[0]
        
        url = urlunparse((parts.scheme, parts.netloc, parts.path, '', '', ''))
        headers = {
            'Content-Type': 'application/json'
        }
        req = Request(url, json.dumps(data).encode('utf-8'), headers)
        resp = urlopen(req)
        return json.load(resp)
