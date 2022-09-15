import logging

import pytest
from mock.mock import MagicMock, PropertyMock

from stf_appium_client.AdbServer import AdbServer


class TestAdbServer:

    @classmethod
    def setup_class(cls):
        logging.disable(logging.CRITICAL)

    @classmethod
    def teardown_classr(cls):
        logging.disable(logging.NOTSET)

    @pytest.fixture
    def mock_easyprocess(self, mocker) -> MagicMock:
        mocked = mocker.patch("stf_appium_client.AdbServer.EasyProcess", autospec=True)

        call_mock = MagicMock()
        type(call_mock).stderr = PropertyMock(return_value='err')
        type(call_mock).stdout = PropertyMock(return_value='out')
        type(call_mock).return_code = PropertyMock(return_value=0)

        #type(mocked).call = call_mock
        mocked.call = call_mock

        return mocked

    #def test_context(self, mock_easyprocess):
    #    with AdbServer('localhost') as adb:
    #        assert isinstance(adb.port, int)
