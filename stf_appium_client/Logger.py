import logging


class Logger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        # Todo: improve logging module...
