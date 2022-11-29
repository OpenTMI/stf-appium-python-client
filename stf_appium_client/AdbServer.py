import os
from easyprocess import EasyProcess
import atexit
from stf_appium_client.Logger import Logger
from stf_appium_client.tools import find_free_port, assert_tool_exists


class AdbServer(Logger):
    def __init__(self, adb_server: str = None, port: int = None):
        """
        Connect to adb server and open proxy for given port
        :param adb_server: adb server to be connected
        :param port: adb listen port in  localhost. None=default, 0=first free one
        """
        super().__init__()
        assert adb_server, 'adb_server is not given'
        self.adb_server = adb_server
        if port is None:
            port = 5037  # default adb port
        self._port = find_free_port() if not port else port
        self.connected = False

        @atexit.register
        def _exit():
            nonlocal self
            if self.connected:
                self.logger.info("exit:Killing adb")
                self.kill()

    @staticmethod
    def ok():
        assert_tool_exists('adb')

    @property
    def adb_server(self) -> str:
        """ Get remote adb server address """
        return self._adb_server

    @adb_server.setter
    def adb_server(self, adb_server: str):
        """ Set remote adb server address """
        self._adb_server = adb_server

    def __enter__(self):
        """ Context entrypoint"""
        self.logger.info(f"adb connect: {self._adb_server}")
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Context exit point """
        self.logger.info(f"Killing adb {self.port}")
        if self.connected:
            self.kill()

    @property
    def port(self) -> int:
        """ Get local adb server port """
        return self._port

    def execute(self, command: str, timeout: int = 2) -> EasyProcess:
        """
        Internal execute function
        :param command: adb command to be executed
        :param timeout: command timeout
        :return: EasyProcess instance which contains stdout, stderr, return_code, timeout_happened
        """
        port = f"-P {self.port} " if self.port else ""
        cmd = f"adb {port} {command}"
        self.logger.debug(f"adb: {cmd}")
        my_env = os.environ.copy()
        if "ADB_VENDOR_KEYS" not in my_env:
            my_env["ADB_VENDOR_KEYS"] = "~/.android"
        response = EasyProcess(cmd, env=my_env).call(timeout=timeout)
        self.logger.debug(f'adb retcode: {response.return_code}, '
                          f'stdout: {response.stdout}, '
                          f'stderr: {response.stderr}')
        return response

    def connect(self) -> None:
        """
        Create ADB server using given ADB host
        :param host: ADB host to be used for local adb server
        :return: None
        """
        assert not self.connected, 'adb is already running'
        self.logger.debug(f'adb({self._adb_server}): connecting')
        try:
            cmd = f"connect {self._adb_server}"
            response = self.execute(cmd, 10)
            stdout = response.stdout
            self.logger.debug(stdout)
            assert response.return_code == 0, f"{response.stderr}"
        except AssertionError as error:
            self.logger.error(error)
            raise

        self.logger.info(f'adb({self.port}): connected to {self._adb_server}')
        self.connected = True

    def kill(self) -> None:
        """ Kill local adb server """
        assert self.connected, 'adb is not started'
        try:
            self.logger.debug(f'adb({self.port}): killing service')
            self.execute('kill-server')
            self.connected = False
        except AssertionError as error:
            self.logger.error(f'adb kill failed: {error}')
            raise
        self.logger.info(f'adb({self.port}): service killed successfully')
