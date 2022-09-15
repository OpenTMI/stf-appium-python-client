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

    @pytest.fixture
    def mock_webdriver(self, mocker) -> MagicMock:
        return mocker.patch("stf_appium_client.AppiumClient.WebDriver")

    def test_context(self, mock_webdriver):
        #if not which("appium"):
        #    pytest.skip("Appium is missing!")
        with AppiumClient() as appium:
            assert appium.driver
