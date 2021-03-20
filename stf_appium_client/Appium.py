from appium.webdriver.appium_service import AppiumService
from stf_appium_client.tools import find_free_port


class Appium:
    def __init__(self):
        self.port = find_free_port()
        self.service = AppiumService()

    def __enter__(self):
        # https://appium.io/docs/en/writing-running-appium/server-args/
        args = ['-a', '127.0.0.1', '-p', f"{self.port}"]
        print(f'Using appium server with args: {" ".join(args)}')
        self.service.start(args=args)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Close appium server")
        self.service.stop()
