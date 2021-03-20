from contextlib import contextmanager
from easyprocess import EasyProcess
import atexit
from stf_appium_client.Logger import Logger
from stf_appium_client.tools import find_free_port


@contextmanager
def adb(adb_adr: str):
    adb = AdbServer.use_random_port()
    print("adb connect")
    adb.connect(adb_adr)

    @atexit.register
    def exit():
        if adb.connected:
            print("exit:Killing adb")
            adb.kill()

    try:
        yield adb.port
    finally:
        print("Killing adb")
        adb.kill()


class AdbServer(Logger):
    def __init__(self, port=0):
        super().__init__('AdbClient')
        self._port = port
        self.connected = False

    @property
    def port(self) -> int:
        return self._port

    @staticmethod
    def use_random_port():
        """
        Use random free port and create AdbServer instance
        :return: instance of AdbServer
        :rtype: AdbServer
        """
        port = find_free_port()
        return AdbServer(port)

    def _execute(self, command: str, timeout: int = 2):
        """
        Internal execute function
        :param command: adb command to be execute
        :param timeout: command timeout
        :return: EasyProcess instance which contains stdout, stderr and return_code
        """
        port = f"-P {self._port} " if self._port else ""
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
            # assert response.return_code == 0, f"{response.stderr}"
        except AssertionError as error:
            self.logger.error(error)
            assert False, f"{error}"
        else:
            self.logger.debug('adb server running..')
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
