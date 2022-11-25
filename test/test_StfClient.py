import unittest
import logging
import types
from unittest.mock import patch, MagicMock

from stf_client.exceptions import ForbiddenException

from stf_appium_client.StfClient import StfClient
from stf_appium_client.exceptions import *




class TestStfClientBasics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)

    def test_construct(self):
        client = StfClient('http://localhost')
        self.assertIsInstance(client, StfClient)
        with self.assertRaises(NotConnectedError):
            client.allocate({})
        with self.assertRaises(NotConnectedError):
            client.release({})
        with self.assertRaises(NotConnectedError):
            client.find_and_allocate({})
        # Check that all API's exists
        self.assertIsInstance(client.allocate, types.MethodType)
        self.assertIsInstance(client.release, types.MethodType)
        self.assertIsInstance(client.remote_connect, types.MethodType)
        self.assertIsInstance(client.remote_disconnect, types.MethodType)
        self.assertIsInstance(client.get_devices, types.MethodType)
        self.assertIsInstance(client.find_wait_and_allocate, types.MethodType)
        self.assertIsInstance(client.find_and_allocate, types.MethodType)
        self.assertIsInstance(client.allocation_context, types.MethodType)
        self.assertIsInstance(client.list_devices, types.MethodType)

    @patch('stf_appium_client.StfClient.Configuration')
    @patch('stf_appium_client.StfClient.ApiClient')
    def test(self, mock_client, mock_conf):
        client = StfClient('localhost')
        mock_conf.assert_called_once()
        client.connect('mytoken')
        mock_client.assert_called_once()


class TestStfClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)

    def setUp(self):
        patcher_conf = patch('stf_appium_client.StfClient.Configuration')
        patcher_client = patch('stf_appium_client.StfClient.ApiClient')
        patcher_userapi = patch('stf_appium_client.StfClient.UserApi')
        patcher_devicesapi = patch('stf_appium_client.StfClient.DevicesApi')
        self.addCleanup(patcher_conf.stop)
        self.addCleanup(patcher_client.stop)
        self.addCleanup(patcher_userapi.stop)
        self.addCleanup(patcher_devicesapi.stop)

        self.Configuration = patcher_conf.start()
        self.ApiClient = patcher_client.start()
        self.UserApi = patcher_userapi.start()
        self.DevicesApi = patcher_devicesapi.start()

        class MockResp:
            remote_connect_url = '123'
        self.UserApi.return_value.remote_connect_user_device_by_serial = MagicMock(return_value=MockResp())

        self.client = StfClient('localhost')
        self.client.connect('token')

    def test_get_devices(self):
        class MockResp:
            devices = []
        self.DevicesApi.return_value.get_devices = MagicMock(return_value=MockResp())
        devices = self.client.get_devices()
        self.assertEqual(devices, [])

    def test_allocate_release(self):
        mock_add_device = MagicMock()
        mock_delete_device = MagicMock()
        self.UserApi.return_value.add_user_device_v2 = mock_add_device
        self.UserApi.return_value.delete_user_device_by_serial = mock_delete_device

        resource = self.client.allocate({"serial": '123'})
        self.assertEqual(resource['serial'], '123')
        self.client.release({"serial": '123'})

        # validate under the hoods
        mock_add_device.assert_called_once()

    def test_find_and_allocate_but_device_not_found(self):
        class MockResp:
            devices = []
        self.DevicesApi.return_value.get_devices = MagicMock(return_value=MockResp())
        with self.assertRaises(DeviceNotFound):
            self.client.find_and_allocate({})

    def test_list_devices(self):
        available = {'serial': 123, 'present': True, 'ready': True, 'using': False, 'owner': None, 'status': 3}
        self.client.get_devices = MagicMock(return_value=[available])
        response = self.client.list_devices(requirements={})
        self.assertEqual(response, [available])

    def test_list_devices_offline(self):
        available = {'serial': 123, 'present': True, 'ready': True, 'using': False, 'owner': None, 'status': 1}
        self.client.get_devices = MagicMock(return_value=[available])
        response = self.client.list_devices(requirements={})
        self.assertEqual(response, [])

    def test_find_and_allocate_success(self):
        available = {'serial': '123', 'present': True, 'ready': True, 'using': False, 'owner': None, 'status': 3}
        self.client.get_devices = MagicMock(return_value=[available])
        self.client.allocate = MagicMock()

        device = self.client.find_and_allocate({})
        self.assertEqual(device, available)

        # validate under the hoods
        self.client.get_devices.assert_called_once()
        self.client.allocate.assert_called_once_with(available, timeout_seconds=900)

    @patch('random.shuffle', side_effect=MagicMock())
    def test_find_and_allocate_second_success(self, mock_choise):
        invalid = {'serial': '12', 'present': False, 'ready': True, 'using': False, 'owner': None, 'status': 3}
        available = {'serial': '123', 'present': True, 'ready': True, 'using': False, 'owner': None, 'status': 3}
        self.client.get_devices = MagicMock(return_value=[invalid, available, available])

        def dummy_alloc(dev, timeout_seconds):
            return dev

        self.client.allocate = MagicMock(side_effect=[ForbiddenException, dummy_alloc])

        device = self.client.find_and_allocate({})
        available['owner'] = 'me'
        self.assertEqual(device, available)
        self.client.release(device)

        # validate under the hoods
        self.client.get_devices.assert_called_once()

    def test_find_and_allocate_no_suitable(self):
        dev1 = {'serial': '12', 'present': True, 'ready': True, 'using': True, 'owner': None, 'status': 3}
        dev2 = {'serial': '123', 'present': True, 'ready': True, 'using': True, 'owner': None, 'status': 3}
        self.client.get_devices = MagicMock(return_value=[dev1, dev2])
        self.client.allocate = MagicMock()

        with self.assertRaises(DeviceNotFound):
            self.client.find_and_allocate({})

    def test_remote_connect(self):

        self.UserApi.return_value.add_user_device_v2 = MagicMock()

        self.UserApi.return_value.delete_user_device_by_serial = MagicMock()
        resource = self.client.allocate({"serial": '123'})
        remoteConnectUrl = self.client.remote_connect(resource)
        self.client.release(resource)
        self.assertEqual(remoteConnectUrl, '123')
        self.UserApi.return_value.add_user_device_v2.assert_called_once_with('123', timeout=900000)
        self.UserApi.return_value.remote_connect_user_device_by_serial.assert_called_once_with('123')

    def test_remote_disconnect(self, ):
        url = '123'
        class MockResp:
            remote_connect_url=url
        self.UserApi.return_value.remote_connect_user_device_by_serial = MagicMock(return_value=MockResp())

        self.UserApi.return_value.remote_disconnect_user_device_by_serial = MagicMock()

        device = {"serial": 123}
        resource = self.client.allocate(device)
        self.client.remote_connect(resource)
        self.client.remote_disconnect(resource)
        self.client.release(resource)
        self.UserApi.return_value.remote_disconnect_user_device_by_serial.assert_called_once_with(123)

    def test_release(self):
        resource = self.client.allocate({"serial": '123'})
        self.assertEqual(resource['serial'], '123')
        self.client.release(resource)
        self.UserApi.return_value.add_user_device_v2.assert_called_once_with('123', timeout=900000)
        self.UserApi.return_value.delete_user_device_by_serial.assert_called_once_with('123')

    def test_allocation_context_first_success(self):
        dev1 = {'serial': '123', 'present': True, 'ready': True, 'using': False, 'owner': None, 'status': 3}
        self.client.get_devices = MagicMock(return_value=[dev1])
        url = '123'

        with self.client.allocation_context({"serial": '123'}) as device:
            self.assertEqual(device['serial'], '123')
            self.assertEqual(device['remote_adb_url'], url)

    @patch('time.sleep', side_effect=MagicMock())
    def test_allocation_context_wait_success(self, mock_sleep):
        dev1 = {'serial': '123', 'present': True, 'ready': True, 'using': False, 'owner': None, 'status': 3}
        self.client.get_devices = MagicMock(side_effect=[[], [dev1]])
        url = '123'

        with self.client.allocation_context({"serial": '123'}) as device:
            self.assertEqual(device['serial'], '123')
            self.assertEqual(device['remote_adb_url'], url)


