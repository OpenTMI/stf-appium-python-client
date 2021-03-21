import sys
import unittest
import urllib
from unittest.mock import patch
from stf_appium_client.cli import main


class TestAdbServer(unittest.TestCase):

    def test_help(self):
        testargs = ["prog", "--help"]
        with self.assertRaises(SystemExit) as cm:
            with patch.object(sys, 'argv', testargs):
                main()
        self.assertEqual(cm.exception.code, 0)

    def test_host_invalid_requirements(self):
        testargs = ["prog", "--token", "123", "--host",
                    "http://test", "--requirements", "asdf"]
        with self.assertRaises(SystemExit) as cm:
            with patch.object(sys, 'argv', testargs):
                main()
        self.assertEqual(cm.exception.code, 1)

    def test_host_not_found(self):
        testargs = ["prog", "--token", "123", "--host", "http://test"]
        with self.assertRaises(urllib.error.URLError):
            with patch.object(sys, 'argv', testargs):
                main()
