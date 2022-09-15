import logging
from shutil import which

import pytest

from stf_appium_client.AdbServer import AdbServer


class TestAdbServer:

    @classmethod
    def setup_class(cls):
        logging.disable(logging.CRITICAL)

    @classmethod
    def teardown_classr(cls):
        logging.disable(logging.NOTSET)

    def test_context(self):
        if not which("adb"):
            pytest.skip("adb is missing!")
        with AdbServer('localhost') as adb:
            assert isinstance(adb.port, int)
