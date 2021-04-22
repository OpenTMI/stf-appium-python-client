import logging
import os


class Logger:
    def __init__(self):
        self.logger = logging.getLogger('StfAppiumClient')
        self.setup_logger()

    @staticmethod
    def get_default_logger_format():
        return "%(asctime)-15s %(name)-8s %(levelname)s: %(message)s"

    def setup_logger(self):
        if self.logger.handlers:
            return
        self.logger.addHandler(logging.NullHandler())

        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(fmt=Logger.get_default_logger_format()))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        if bool(os.environ.get("STF_APPIUM_LOGGING", False)):
            self.logger.setLevel(logging.DEBUG)
