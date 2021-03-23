import unittest
import logging
from shutil import which
from stf_appium_client.Appium import Appium


class TestAppium(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)

    def test_context(self):
        if not which("appium"):
            self.skipTest("Appium is missing!")
        with Appium() as appium:
            self.assertIsInstance(appium.port, int)
