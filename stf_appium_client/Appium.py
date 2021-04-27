import atexit
from appium.webdriver.appium_service import AppiumService
from stf_appium_client.tools import find_free_port
from stf_appium_client.Logger import Logger


class Appium(Logger):

    def __init__(self):
        """ Initialize Appium wrapper """
        super().__init__()
        self.port = find_free_port()
        self.service = AppiumService()

        @atexit.register
        def _exit():
            nonlocal self
            if self.service.is_running:
                self.logger.warn("exit:stop appium")
                self.stop()

    def get_wd_hub_uri(self) -> str:
        """ Get local appium uri """
        assert self.service.is_running, 'Appium is not running'
        return f'http://127.0.0.1:{self.port}/wd/hub'

    def start(self):
        assert not self.service.is_running, 'Appium already running'
        # https://appium.io/docs/en/writing-running-appium/server-args/
        args = ['-a', '127.0.0.1', '-p', f"{self.port}"]
        self.logger.info(f'Start Appium with args: {" ".join(args)}')
        self.service.start(args=args)
        assert self.service.is_running, 'Appium did not started :o'
        uri = self.get_wd_hub_uri()
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
