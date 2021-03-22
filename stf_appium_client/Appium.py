from appium.webdriver.appium_service import AppiumService
from stf_appium_client.tools import find_free_port
from stf_appium_client.Logger import Logger


class Appium(Logger):

    def __init__(self):
        self.port = find_free_port()
        self.service = AppiumService()
        super().__init__()

    def start(self):
        assert not self.service.is_running, 'Appium already running'
        # https://appium.io/docs/en/writing-running-appium/server-args/
        args = ['-a', '127.0.0.1', '-p', f"{self.port}"]
        self.logger.info(f'Start Appium with args: {" ".join(args)}')
        self.service.start(args=args)

    def exit(self):
        assert self.service.is_running, 'Appium is not running'
        self.logger.info("Close appium server")
        self.service.stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit()
