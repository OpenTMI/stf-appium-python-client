import unittest
from dataclasses import dataclass
from unittest.mock import patch, MagicMock, PropertyMock
from pydash import get
from stf_appium_client.StfClient import StfClient
from stf_appium_client.exceptions import *


@dataclass
class Response:
    status: int
    data: dict

    @property
    def success(self):
        return self.status == 200


class TestStfClientBasics(unittest.TestCase):

    def test_construct(self):
        client = StfClient('http://localhost')
        self.assertIsInstance(client, StfClient)
        self.assertEqual(client.swagger_uri, 'http://localhost/api/v1/swagger.json')
        with self.assertRaises(NotConnectedError):
            client.allocate({})
        with self.assertRaises(NotConnectedError):
            client.release({})
        with self.assertRaises(NotConnectedError):
            client.find_and_allocate({})

    @patch('stf_appium_client.StfClient.swagger_uri', new_callable=PropertyMock)
    def test(self, mock_swagger_uri):
        mock_swagger_uri.return_value = './test/swagger.json'
        client = StfClient('localhost')
        client.connect('mytoken')
        mock_swagger_uri.assert_called_once()


class TestStfClient(unittest.TestCase):

    def setUp(self):
        patcher = patch('stf_appium_client.StfClient.swagger_uri', new_callable=PropertyMock)
        self.mock_swagger_uri = patcher.start()
        self.addCleanup(patcher.stop)

        self.client = StfClient('localhost')
        type(self.client).swagger_uri = PropertyMock(return_value='./test/swagger.json')
        self.client.connect('token')

    def test_get_devices(self):
        @dataclass
        class Data:
            devices = []
        self.client._client.request = MagicMock(return_value=Response(status=200, data=Data()))
        devices = self.client.get_devices()
        self.assertEqual(devices, [])

    def test_allocate(self):
        self.client._client.request = MagicMock(return_value=Response(status=200, data={}))

        resource = self.client.allocate({"serial": 123})
        self.assertEqual(resource['serial'], 123)

        # validate under the hoods
        self.client._client.request.assert_called_once()
        call = self.client._client.request.call_args_list[0]
        req, resp = call[0][0]
        self.assertEqual(req.path, '/user/devices')
        self.assertEqual(req.method, 'post')

    def test_find_and_allocate_but_device_not_found(self):
        self.client.get_devices = MagicMock(return_value=[])
        self.client._client.request = MagicMock(return_value=Response(status=200, data={}))

        with self.assertRaises(DeviceNotFound):
            self.client.find_and_allocate({})

    def test_find_and_allocate_success(self):
        available = {'serial': 123, 'present': True, 'ready': True, 'using': False, 'owner': None}
        self.client.get_devices = MagicMock(return_value=[available])
        self.client._client.request = MagicMock(return_value=Response(status=200, data={}))

        device = self.client.find_and_allocate({})
        self.assertEqual(device, available)

        # validate under the hoods
        self.client.get_devices.assert_called_once()
        self.client._client.request.assert_called_once()
        call = self.client._client.request.call_args_list[0]
        req, resp = call[0][0]
        self.assertEqual(req.path, '/user/devices')
        self.assertEqual(req.method, 'post')

    @patch('random.shuffle', side_effect=MagicMock())
    def test_find_and_allocate_second_success(self, mock_choise):
        invalid = {'serial': '12', 'present': True, 'ready': True, 'using': False, 'owner': None}
        available = {'serial': '123', 'present': True, 'ready': True, 'using': False, 'owner': None}
        self.client.get_devices = MagicMock(return_value=[invalid, available])

        self.client._client.request = MagicMock(side_effect=[
            Response(status=300, data={}),
            Response(status=200, data={})
        ])

        device = self.client.find_and_allocate({})
        available['owner'] = 'me'
        self.assertEqual(device, available)

        # validate under the hoods
        self.client.get_devices.assert_called_once()

    def test_find_and_allocate_no_suitable(self):
        dev1 = {'serial': '12', 'present': True, 'ready': True, 'using': False, 'owner': None}
        dev2 = {'serial': '123', 'present': True, 'ready': True, 'using': False, 'owner': None}
        self.client.get_devices = MagicMock(return_value=[dev1, dev2])

        self.client._client.request = MagicMock(side_effect=[
            Response(status=300, data={}),
            Response(status=300, data={})
        ])

        with self.assertRaises(DeviceNotFound) as error:
            self.client.find_and_allocate({})

    def test_remote_connect(self):
        url = '123'
        self.client._client.request = MagicMock(return_value=Response(status=200, data={'remoteConnectUrl': url}))

        resource = self.client.allocate({"serial": 123})
        remoteConnectUrl = self.client.remote_connect(resource)
        self.assertEqual(remoteConnectUrl, url)

    def test_remote_disconnect(self):
        url = '123'
        self.client._client.request = MagicMock(return_value=Response(status=200, data={'remoteConnectUrl': url}))

        resource = self.client.allocate({"serial": 123})
        self.client.remote_connect(resource)
        self.client._client.request.reset_mock()
        self.client.remote_disconnect(resource)
        self.client._client.request.assert_called_once()

    def test_release(self):
        self.client._client.request = MagicMock(return_value=Response(status=200, data={}))

        resource = self.client.allocate({"serial": 123})
        self.assertEqual(resource['serial'], 123)
        self.client._client.request.reset_mock()

        self.client.release(resource)
        self.client._client.request.assert_called_once()

    def test_allocation_context_first_success(self):
        dev1 = {'serial': '123', 'present': True, 'ready': True, 'using': False, 'owner': None}
        self.client.get_devices = MagicMock(return_value=[dev1])
        url = '123'
        self.client._client.request = MagicMock(return_value=Response(status=200, data={'remoteConnectUrl': url}))

        with self.client.allocation_context({"serial": '123'}) as device:
            self.assertEqual(device['serial'], '123')
            self.assertEqual(device['remote_adb_url'], url)

    @patch('time.sleep', side_effect=MagicMock())
    def test_allocation_context_wait_success(self, mock_sleep):
        dev1 = {'serial': '123', 'present': True, 'ready': True, 'using': False, 'owner': None}
        self.client.get_devices = MagicMock(side_effect=[[], [dev1]])
        url = '123'
        self.client._client.request = MagicMock(return_value=Response(status=200, data={'remoteConnectUrl': url}))

        with self.client.allocation_context({"serial": '123'}) as device:
            self.assertEqual(device['serial'], '123')
            self.assertEqual(device['remote_adb_url'], url)


