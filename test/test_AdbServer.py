import logging
import sys
from shutil import which
from time import sleep
from unittest.mock import MagicMock, patch

import pytest
from easyprocess import EasyProcess

from stf_appium_client.AdbServer import AdbServer


class TestAdbServer:

    @classmethod
    def setup_class(cls):
        logging.disable(logging.CRITICAL)

    @classmethod
    def teardown_classr(cls):
        logging.disable(logging.NOTSET)

    def test_context_e2e(self):
        if not which("adb"):
            pytest.skip("adb is missing!")
        with AdbServer('localhost') as adb:
            assert isinstance(adb.port, int)

    @patch('shutil.which')
    @patch('stf_appium_client.AdbServer.EasyProcess')
    def test_context(self, mock_easy_process, mock_which):
        mock_easy_process.return_value.call.return_value.stdout = ''
        mock_easy_process.return_value.call.return_value.return_code = 0
        with AdbServer('localhost') as adb:
            assert isinstance(adb.port, int)

    @patch('stf_appium_client.AdbServer.EasyProcess')
    def test_execute_success(self, mock_easy_process):
        mock_easy_process.return_value.call.return_value.stdout = '123'
        mock_easy_process.return_value.call.return_value.return_code = 0
        adb_server = AdbServer('locvalhost', port=1000)
        resp = adb_server.execute('hello', 10)
        assert resp.return_code == 0
        assert resp.stdout == '123'
        mock_easy_process.assert_called_once()
        mock_easy_process.return_value.call.assert_called_once_with(timeout=10)

    @patch('stf_appium_client.AdbServer.EasyProcess')
    def test_execute_fail(self, mock_easy_process):
        mock_easy_process.return_value.call.return_value.stderr = 'abc'
        mock_easy_process.return_value.call.return_value.stdout = '123'
        mock_easy_process.return_value.call.return_value.return_code = 1
        adb_server = AdbServer('locvalhost', port=1000)
        resp = adb_server.execute('hello', 10)
        assert resp.return_code == 1
        assert resp.stdout == '123'
        assert resp.stderr == 'abc'
        mock_easy_process.assert_called_once()
        mock_easy_process.return_value.call.assert_called_once_with(timeout=10)

    @patch('stf_appium_client.AdbServer.EasyProcess')
    def test_execute_timeout(self, mock_easy_process):

        def call(timeout):
            python = sys.executable
            return EasyProcess([python, "-c", 'import time\ntime.sleep(10)']).call(timeout=timeout)
        mock_easy_process.return_value.call.side_effect = call
        adb_server = AdbServer('localhost', port=1000)
        resp = adb_server.execute('hello', timeout=0.1)
        assert resp.timeout_happened
        mock_easy_process.assert_called_once()
