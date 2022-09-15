import itertools
import logging
from unittest.mock import PropertyMock

import pytest
from mock.mock import MagicMock

from stf_appium_client.AppiumServer import AppiumServer


class TestAppiumServer:

    @classmethod
    def setup_class(cls):
        logging.disable(logging.CRITICAL)

    @classmethod
    def teardown_class(cls):
        logging.disable(logging.NOTSET)

    @pytest.fixture
    def mock_webdriver(self, mocker) -> MagicMock:
        mocked = mocker.patch("stf_appium_client.AppiumServer.AppiumService", autospec=True)
        type(mocked.return_value).is_running = PropertyMock(side_effect=
                                                            itertools.chain([False], itertools.repeat(True))
                                                            )
        process_mock = MagicMock()
        type(process_mock.return_value).pid = PropertyMock(return_value=1)
        type(mocked.return_value)._process = PropertyMock(process_mock)
        return mocked

    def test_context(self, mock_webdriver):
        with AppiumServer() as appium:
            mock_webdriver.assert_called_once_with()
            assert isinstance(appium.port, int)
