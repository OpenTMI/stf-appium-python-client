import atexit
from typing import Any

from appium.webdriver.webdriver import WebDriver
from stf_appium_client.Logger import Logger


class AppiumClient(Logger):
    """"
    Appium client object
    """
    def __init__(self, command_executor='http://localhost:4723', **kwargs: Any):
        """ Initialize Appium wrapper """
        super().__init__()
        self._command_executor = command_executor
        self._kwargs = kwargs
        self._driver = None

        @atexit.register
        def _exit():
            nonlocal self
            if self._driver:
                self.logger.info("exit:stop appium-driver")
                self.stop()

    @property
    def driver(self):
        assert self._driver, 'Appium driver not running'
        return self._driver

    def start(self):
        assert not self._driver, 'Appium driver already running'
        self._driver = WebDriver(command_executor=self._command_executor, **self._kwargs)

    def stop(self):
        assert self._driver, 'Appium driver is not running'
        self.logger.info(f"Close appium driver")
        self._driver.quit()
        self._driver = None

    def __enter__(self):
        self.start()
        return self._driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
