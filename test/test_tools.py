import unittest
from stf_appium_client.tools import find_free_port


class TestTools(unittest.TestCase):

    def test_port(self):
        for i in range(10):
            port = find_free_port()
            self.assertTrue(isinstance(port, int))
