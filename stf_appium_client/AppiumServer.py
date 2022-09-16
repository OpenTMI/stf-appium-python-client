from typing import Any, List
import atexit
from appium.webdriver.appium_service import AppiumService
from appium.version import version
from stf_appium_client.tools import find_free_port
from stf_appium_client.Logger import Logger


class AppiumServer(Logger):

    def __init__(self, appium_args: List[str] = None, **kwargs: Any):
        """ Initialize Appium wrapper """
        super().__init__()
        self.port = find_free_port()
        self.service = AppiumService()
        self._extra_args = kwargs
        self._appium_args = appium_args or []

        @atexit.register
        def _exit():
            nonlocal self
            if self.service.is_running:
                self.logger.info("exit:stop appium")
                self.stop()

    def get_api_path(self) -> str:
        """ Get local appium uri """
        assert self.service.is_running, 'Appium is not running'
        if version.startswith("1."):
            return f'http://127.0.0.1:{self.port}/wd/hub'
        elif version.startswith("2."):
            return f'http://127.0.0.1:{self.port}'
        raise AssertionError('appium version not supported')

    def start(self):
        assert not self.service.is_running, 'Appium already running'
        # https://appium.io/docs/en/writing-running-appium/server-args/
        args = ['-a', '127.0.0.1', '-p', f"{self.port}"]
        args.extend(self._appium_args)
        self.logger.info(f'Start Appium with args: {" ".join(args)} {self._extra_args}')
        self.service.start(args=args, **self._extra_args)
        assert self.service.is_running, 'Appium did not started :o'
        uri = self.get_api_path()
        self.logger.info(f'Appium started: {uri} (pid: {self.service._process.pid})')
        return uri

    def stop(self):
        assert self.service.is_running, 'Appium is not running'
        self.logger.info(f"Close appium server (port: {self.port}, pid: {self.service._process.pid})")
        self.service.stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
