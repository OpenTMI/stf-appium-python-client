from contextlib import contextmanager
import time
import random
import urllib
from pyswagger import App, Security
from pyswagger.contrib.client.requests import Client
from pydash import filter_, map_, wrap, find, uniq
import atexit
from stf_appium_client.Logger import Logger
from stf_appium_client.exceptions import DeviceNotFound, NotConnectedError


class StfClient(Logger):
    DEFAULT_ALLOCATION_TIMEOUT_SECONDS = 900

    def __init__(self, host: str):
        """
        OpenSTF Client consructor
        :param host: Server address of OpenSTF
        """
        super().__init__()
        self._client = None
        self._app = None
        self._host = host

    @property
    def swagger_uri(self) -> str:
        """ Get swagger.json URI """
        return f"{self._host}/api/v1/swagger.json"

    def connect(self, token: str) -> None:
        """
        Establish connection for OpenSTF server
        :param token: stf access token
        :return: None
        """
        url = self.swagger_uri
        self.logger.debug(f"Get to {url}")
        # load Swagger resource file into App object
        try:
            self._app = App._create_(url)  # pylint: disable-line
        except (FileNotFoundError, urllib.error.URLError) as error:
            self.logger.error(error)
            raise
        auth = Security(self._app)
        auth.update_with('accessTokenAuth', f"Bearer {token}")  # token
        # init swagger client
        self._client = Client(auth)
        self.logger.info('Client library initiated')

    def get_devices(self, fields: list = []) -> list:
        """
        Get list of devices dictionary
        :param fields: fields to be request for each device
        :return: list of device dictionaries
        :rtype: [dict]
        """
        NotConnectedError.invariant(self._client, 'Not connected')
        fields.extend([
            'present', 'ready', 'using', 'owner', 'marketName',
            'serial', 'manufacturer', 'model', 'platform', 'sdk', 'version'
        ])
        self.logger.debug('getDevices')
        req, resp = self._app.op['getDevices'](fields=','.join(fields))
        # prefer json as response
        req.produce('application/json')
        response = self._client.request((req, resp))
        assert response.status == 200, 'Could not fetch device list'
        devices = response.data.devices
        assert isinstance(devices, list), 'invalid response'
        self.logger.debug(f'Got devices: {devices}')
        return devices

    def allocate(self, device: dict, timeout_seconds: int = DEFAULT_ALLOCATION_TIMEOUT_SECONDS) -> dict:
        """
        Allocate device based on serial number
        :param device: dictionary device object
        :param timeout_seconds: Means the device will be automatically
                                removed from the user control if it is kept
                                idle for this period (in milliseconds);
                                default value is provided by the provider 'group timeout'
        :return: None
        """
        NotConnectedError.invariant(self._client, 'Not connected')
        serial = device.get('serial')
        self.logger.debug(f"allocate: ${serial}")
        timeout = timeout_seconds * 1000
        req, resp = self._app.op['addUserDevice'](device=dict(serial=serial, timeout=timeout))
        response = self._client.request((req, resp))
        assert response.status == 200, 'Could not allocate device'
        self.logger.info(f'{device.get("serial")}: Allocated (timeout: {timeout_seconds})')
        return device

    def remote_connect(self, device: dict) -> str:
        """
        Create remote ADB connection to device
        :param device: dictionary device object
        :return: remote connection url
        """
        NotConnectedError.invariant(self._client, 'Not connected')
        serial = device.get('serial')
        self.logger.debug(f"remoteConnect: ${serial}")

        req, resp = self._app.op['remoteConnectUserDeviceBySerial'](serial=serial)
        # prefer json as response
        req.produce('application/json')
        response = self._client.request((req, resp))
        assert response.status == 200, 'Could not connect device by serial'
        remoteConnectUrl = response.data.get('remoteConnectUrl')
        assert isinstance(remoteConnectUrl, str), 'invalid remoteConnectUrl'
        return remoteConnectUrl

    def remote_disconnect(self, device: dict):
        """
        Close remote ADB connection to device
        :param device: dictionary device object
        :return: remote connection url
        """
        NotConnectedError.invariant(self._client, 'Not connected')
        serial = device.get('serial')
        self.logger.debug(f"remoteConnect: ${serial}")

        req, resp = self._app.op['remoteDisconnectUserDeviceBySerial'](serial=serial)
        # prefer json as response
        req.produce('application/json')
        response = self._client.request((req, resp))
        assert response.status == 200, 'Could not connect device by serial'

    def release(self, device: dict) -> None:
        """
        Release device
        :param device: disctionary device object
        :return: None
        """
        NotConnectedError.invariant(self._client, 'Not connected')
        serial = device.get('serial')
        self.logger.debug(f"`releasing: ${serial}")
        req, resp = self._app.op['deleteUserDeviceBySerial'](serial=serial)
        response = self._client.request((req, resp))
        assert response.status == 200, 'Could not disconnect to device'
        device['owner'] = None
        self.logger.info(f'{device.get("serial")}: released')

    def find_and_allocate(self, requirements: dict,
                          timeout_seconds: int = DEFAULT_ALLOCATION_TIMEOUT_SECONDS,
                          shuffle: bool = True) -> dict:
        """
        Find device based on requirements and allocate first
        :param requirements: dictionary about requirements, e.g. `dict(platform='android')`
        :param timeout_seconds: allocation timeout when idle, see more from allocation api.
        :param shuffle: randomize allocation
        :return: device dictionary
        """
        NotConnectedError.invariant(self._client, 'Not connected')
        req_keys = list(requirements.keys())
        req_keys.extend(['present', 'ready', 'using', 'owner'])
        req_keys.extend([
            'serial', 'manufacturer', 'model',
            'platform', 'sdk', 'version'
        ])
        fields = uniq(req_keys)

        predicate = requirements.copy()
        predicate.update(
            dict(
                present=True,
                ready=True,
                using=False,
                owner=None)
        )

        self.logger.debug(f"Get fields: {','.join(fields)}")

        devices = self.get_devices(fields=fields)

        suitable_devices = filter_(devices, predicate)
        DeviceNotFound.invariant(len(suitable_devices), 'no suitable devices found')
        if shuffle:
            random.shuffle(suitable_devices)

        def allocate_first():
            def try_allocate(device):
                try:
                    return self.allocate(device, timeout_seconds=timeout_seconds)
                except AssertionError:
                    return None

            tasks = map_(suitable_devices, lambda item: wrap(item, try_allocate))
            return find(tasks, lambda allocFunc: allocFunc())

        result = allocate_first()
        if not result:
            raise DeviceNotFound()
        device = result.args[0]
        device['owner'] = "me"
        return device

    @contextmanager
    def allocation_context(self, requirements: dict,
                           allocation_timeout=60,
                           timeout_seconds=DEFAULT_ALLOCATION_TIMEOUT_SECONDS):
        """
        :param requirements:
        :param allocation_timeout: how long time we try to allocate suitable device
        :param timeout_seconds: allocation timeout
        :return:
        """
        self.logger.info(f"Trying to allocate device using requirements: {requirements}")
        for i in range(allocation_timeout):  # try to allocate for 1 minute..
            try:
                device = self.find_and_allocate(requirements=requirements,
                                                timeout_seconds=timeout_seconds)
                break
            except DeviceNotFound:
                # Wait a while
                time.sleep(1)
                pass

        @atexit.register
        def exit():
            nonlocal self, device
            if device.get('owner') is not None:
                self.logger.warn(f"exit:Release device {device.get('serial')}")
                self.release(device)

        self.logger.info(f'device allocated: {device}')
        adb_adr = self.remote_connect(device)
        device['remote_adb_url'] = adb_adr
        yield device
        self.logger.info(f"Release device {device.get('serial')}")
        self.remote_connect(device)
        self.release(device)
