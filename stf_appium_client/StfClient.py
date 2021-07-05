from contextlib import contextmanager
import time
import random
import urllib
import json
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
        self.logger.debug(f"Fetch API spec from: {url}")
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
        self.logger.info('StfClient library initiated')

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
            'serial', 'manufacturer', 'model', 'platform', 'sdk', 'version',
            'status'
        ])
        self.logger.debug('stf: get devices..')
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
                                idle for this period. default value is provided
                                by the provider 'group timeout'
        :return: None
        """
        NotConnectedError.invariant(self._client, 'Not connected')
        serial = device.get('serial')
        self.logger.debug(f"{serial}: trying to  allocate")
        timeout = timeout_seconds * 1000
        req, resp = self._app.op['addUserDevice'](device=dict(serial=serial, timeout=timeout))
        response = self._client.request((req, resp))
        assert response.status == 200, 'Could not allocate device'
        self.logger.info(f'{serial}: Allocated (timeout: {timeout_seconds})')
        device['owner'] = "me"

        @atexit.register
        def _exit():
            nonlocal self, device
            try:
                if device.get('owner') == "me":
                    self.logger.warn(f"exit:Release device {device.get('serial')}")
                    self.release(device)
            except AssertionError as error:
                self.logger.error(f'releasing fails: {error}')

        return device

    def remote_connect(self, device: dict) -> str:
        """
        Create remote ADB connection to device
        :param device: dictionary device object
        :return: remote connection url
        """
        NotConnectedError.invariant(self._client, 'Not connected')
        serial = device.get('serial')
        self.logger.debug(f"{serial}: remoteConnecting")
        req, resp = self._app.op['remoteConnectUserDeviceBySerial'](serial=serial)
        # prefer json as response
        req.produce('application/json')
        response = self._client.request((req, resp))
        assert response.status == 200, 'Could not connect device by serial'
        remote_connect_url = response.data.get('remoteConnectUrl')
        assert isinstance(remote_connect_url, str), 'invalid remoteConnectUrl'
        self.logger.info(f"{serial}: remoteConnected ({remote_connect_url})")
        return remote_connect_url

    def remote_disconnect(self, device: dict):
        """
        Close remote ADB connection to device
        :param device: dictionary device object
        :return: remote connection url
        """
        NotConnectedError.invariant(self._client, 'Not connected')
        serial = device.get('serial')
        self.logger.debug(f"{serial}; remote disconnecting..")

        req, resp = self._app.op['remoteDisconnectUserDeviceBySerial'](serial=serial)
        # prefer json as response
        req.produce('application/json')
        response = self._client.request((req, resp))
        assert response.status == 200, 'Could not connect device by serial'
        self.logger.info(f"{serial}; remote disconnected")

    def release(self, device: dict) -> None:
        """
        Release device
        :param device: disctionary device object
        :return: None
        """
        NotConnectedError.invariant(self._client, 'Not connected')
        serial = device.get('serial')
        self.logger.debug(f'{serial}: releasing..')
        req, resp = self._app.op['deleteUserDeviceBySerial'](serial=serial)
        response = self._client.request((req, resp))
        assert response.status == 200, f'Releasing fails: {response.data.description}'
        device['owner'] = None
        self.logger.info(f'{serial}: released')

    def list_devices(self, requirements: dict, fields: str = "") -> list:
        """
        Get list of devices filtered by given requirements and optional extra fields
        :param requirements: filter dictionary
        :param fields: extra fields to include
        :return: list of objects that represent devices
        """
        req_keys = list(requirements.keys())
        req_keys.extend(['present', 'ready', 'using', 'owner'])
        req_keys.extend([
            'serial', 'manufacturer', 'model',
            'platform', 'sdk', 'version', 'note', 'group.name'
        ])
        req_keys.extend(fields.split(','))
        fields = uniq(req_keys)

        predicate = requirements.copy()

        predicate.update(
            dict(
                present=True,
                ready=True,
                using=False,
                owner=None,
                status=3)  # 3=Online 
        )

        self.logger.debug(
            f"Find devices with requirements: {json.dumps(requirements)}, using fields: {','.join(fields)}")

        devices = self.get_devices(fields=fields)

        return filter_(devices, predicate)

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
        suitable_devices = self.list_devices(requirements=requirements)
        DeviceNotFound.invariant(len(suitable_devices), 'no suitable devices found')
        if shuffle:
            random.shuffle(suitable_devices)

        self.logger.debug(f'Found {len(suitable_devices)} suitable devices, try to allocate one')

        def allocate_first():
            def try_allocate(device):
                try:
                    return self.allocate(device, timeout_seconds=timeout_seconds)
                except AssertionError as error:
                    self.logger.warning(f"{device.get('serial')}Allocation fails: {error}")
                    return None

            tasks = map_(suitable_devices, lambda item: wrap(item, try_allocate))
            return find(tasks, lambda allocFunc: allocFunc())

        result = allocate_first()
        if not result:
            raise DeviceNotFound()
        device = result.args[0]
        return device

    def find_wait_and_allocate(self,
                               requirements: dict,
                               wait_timeout=60,
                               timeout_seconds=DEFAULT_ALLOCATION_TIMEOUT_SECONDS,
                               shuffle: bool = True):
        """
        wait until suitable device is free and allocate it
        :param requirements: dict of requirements for DUT
        :param wait_timeout: wait timeout for suitable free device
        :param timeout_seconds: allocation timeout. See more from allocate -API.
        :param shuffle: allocate suitable device randomly.
        :return: device dictionary
        """
        device = None
        for i in range(wait_timeout):  # try to allocate for 1 minute..
            try:
                device = self.find_and_allocate(requirements=requirements,
                                                timeout_seconds=timeout_seconds,
                                                shuffle=shuffle)
                break
            except DeviceNotFound:
                # Wait a while
                time.sleep(1)
                pass
        DeviceNotFound.invariant(device, 'Suitable device not found')
        return device

    @contextmanager
    def allocation_context(self, requirements: dict,
                           wait_timeout=60,
                           timeout_seconds: int = DEFAULT_ALLOCATION_TIMEOUT_SECONDS,
                           shuffle: bool = True):
        """
        :param requirements:
        :param wait_timeout: how long time we try to allocate suitable device
        :param timeout_seconds: allocation timeout
        :param shuffle: allocate suitable device randomly
        :return:
        """
        self.logger.info(f"Trying to allocate device using requirements: {requirements}")
        device = self.find_wait_and_allocate(requirements=requirements,
                                             wait_timeout=wait_timeout,
                                             timeout_seconds=timeout_seconds,
                                             shuffle=shuffle)

        self.logger.info(f'device allocated: {device}')
        adb_adr = self.remote_connect(device)
        device['remote_adb_url'] = adb_adr
        self.remote_connect(device)
        yield device
        self.release(device)
