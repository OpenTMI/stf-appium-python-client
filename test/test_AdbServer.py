import unittest
from shutil import which
from stf_appium_client.AdbServer import AdbServer


class TestAdbServer(unittest.TestCase):

    def test_context(self):
        if not which("adb"):
            self.skipTest("adb is missing!")
        with AdbServer('localhost') as adb:
            self.assertIsInstance(adb.port, int)
