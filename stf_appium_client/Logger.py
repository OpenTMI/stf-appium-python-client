import logging
import os


class Logger:
    def __init__(self):
        self.logger = logging.getLogger('StfAppiumClient')
        self.setup_logger()

    def setup_logger(self):
        self.logger.addHandler(logging.NullHandler())
        if bool(os.environ.get("STF_APPIUM_LOGGING", False)):
            self.set_debug_logger()

    def set_debug_logger(self):
        FORMAT = "%(asctime)-15s %(name)-8s %(levelname)s: %(message)s"
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(fmt=FORMAT))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
