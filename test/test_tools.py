import json
from unittest.mock import patch, MagicMock
import pytest
from stf_appium_client.tools import find_free_port, parse_requirements, lock
from pid import PidFileAlreadyLockedError


class TestTools:

    def assertEqual(self, value1, value2):
        assert value1 == value2

    def test_port(self):
        for i in range(10):
            port = find_free_port()
            assert isinstance(port, int)

    def test_parse_requirements(self):
        self.assertEqual(parse_requirements("test=1"), {"test": "1"})
        self.assertEqual(parse_requirements(""), {})
        self.assertEqual(parse_requirements({}), {})

        req = {"test": {"a": "1"}}
        self.assertEqual(parse_requirements(json.dumps(req)), req)
        self.assertEqual(parse_requirements("test.a=1"), req)
        self.assertEqual(parse_requirements("test.a=1"), req)
        self.assertEqual(parse_requirements("test.a.b=1"), {"test": {"a": {"b": "1"}}})

        with pytest.raises(ValueError):
            self.assertEqual(parse_requirements("key="), {})
        with pytest.raises(ValueError):
            self.assertEqual(parse_requirements("="), {})

    @patch('stf_appium_client.tools.PidFile')
    def test_lock(self, mock_pidfile):
        with lock():
            self.assertEqual(mock_pidfile.return_value.create.call_count, 1)
            self.assertEqual(mock_pidfile.return_value.close.call_count, 0)
        self.assertEqual(mock_pidfile.return_value.close.call_count, 1)

    @patch('stf_appium_client.tools.PidFile')
    def test_lock_is_released(self, mock_pidfile):
        try:
            with lock():
                raise RuntimeError()
        except RuntimeError:
            self.assertEqual(mock_pidfile.return_value.close.call_count, 1)

    @patch('stf_appium_client.tools.PidFile')
    def test_lock_in_use(self, mock_pidfile):
        mock_pidfile.return_value.create.side_effect = [PidFileAlreadyLockedError()]
        with pytest.raises(AssertionError):
            with lock():
                pass
