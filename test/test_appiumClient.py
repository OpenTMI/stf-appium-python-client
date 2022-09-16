import logging
from shutil import which

from mock import patch, MagicMock
import pytest
from appium.webdriver.webdriver import WebDriver

from stf_appium_client.AppiumClient import AppiumClient


class TestAppiumClient:

    @classmethod
    def setup_class(cls):
        logging.disable(logging.CRITICAL)

    @classmethod
    def teardown_class(cls):
        logging.disable(logging.NOTSET)

    @patch("stf_appium_client.AppiumClient.WebDriver")
    def test_context(self, mock_webdriver):
        with AppiumClient(test=1) as driver:
            mock_webdriver.assert_called_once_with(command_executor='http://localhost:4723', test=1)
