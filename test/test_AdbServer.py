import unittest
import logging
from shutil import which
from stf_appium_client.AdbServer import AdbServer


class TestAdbServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)

    def test_context(self):
        if not which("adb"):
            self.skipTest("adb is missing!")
        with AdbServer('localhost') as adb:
            self.assertIsInstance(adb.port, int)
