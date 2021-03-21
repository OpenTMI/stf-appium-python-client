from easyprocess import EasyProcess
import atexit
from stf_appium_client.Logger import Logger
from stf_appium_client.tools import find_free_port


class AdbServer(Logger):
    def __init__(self, adb_server: str, port: int = 0):
        """ Connect to adb server and open proxy for given port"""
        super().__init__()
        self._adb_server = adb_server
        self._port = find_free_port() if port == 0 else port
        self.connected = False

    def __enter__(self):
        self.logger.info("adb connect: ${self._adb_server}")
        self.connect(self._adb_server)

        @atexit.register
        def exit():
            nonlocal self
            if self.connected:
                print("exit:Killing adb")
                self.kill()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Killing adb")
        if self.connected:
            self.kill()

    @property
    def port(self) -> int:
        return self._port

    def _execute(self, command: str, timeout: int = 2):
        """
        Internal execute function
        :param command: adb command to be execute
        :param timeout: command timeout
        :return: EasyProcess instance which contains stdout, stderr and return_code
        """
        port = f"-P {self.port} " if self.port else ""
        arg1 = f"adb {port} {command}"
        self.logger.debug(f"Arg: {arg1}")
        response = EasyProcess(arg1).call(timeout=timeout)
        self.logger.debug(response.stdout)
        return response

    def connect(self, host: str) -> None:
        """
        Create ADB server using given ADB host
        :param host: ADB host to be used for local adb server
        :return: None
        """
        try:
            cmd = f"connect {host}"
            response = self._execute(cmd, 10)
            stdout = response.stdout
            self.logger.debug(stdout)
            assert response.return_code == 0, f"{response.stderr}"
        except AssertionError as error:
            self.logger.error(error)
            assert False, f"{error}"
        else:
            self.logger.debug(f'adb server running on port: {self.port}')
            self.connected = True

    def kill(self) -> None:
        """
        Kill local adb server
        :return: None
        """
        assert self.connected, 'is not connected'
        try:
            self._execute('kill-server')
            self.connected = False
        except AssertionError as error:
            self.logger.error(error)
