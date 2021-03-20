class StfAppiumClientError(Exception):
    @classmethod
    def invariant(cls, true, message):
        if not true:
            raise cls(message)


class DeviceNotFound(StfAppiumClientError):
    pass


class NotConnectedError(StfAppiumClientError):
    pass
