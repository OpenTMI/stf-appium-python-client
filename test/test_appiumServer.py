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
        instance = mocked.return_value
        instance.start = MagicMock()
        process_mock = MagicMock()
        process_instance_mock = process_mock.return_value
        type(process_instance_mock).pid = PropertyMock(return_value=1)
        type(instance)._process = PropertyMock(process_mock)

        return mocked

    def test_context(self, mock_webdriver):
        with AppiumServer(appium_args=['asd'], extra=1) as appium:
            appium.service.start.assert_called_once_with(
                args=['-a', '127.0.0.1', '-p', str(appium.port), 'asd'],
                extra=1)
            assert isinstance(appium.port, int)
