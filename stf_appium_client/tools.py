import socket
import json
import shutil
from contextlib import closing
import subprocess
from threading import Thread, Event
import sys
import os
import signal


def find_free_port() -> int:
    """
    Find first unused SOCKET port that can be used for adb server
    :return:
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('localhost', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def assert_tool_exists(tool):
    assert shutil.which(tool), f'Not found: {tool}'


def parse_requirements(requirements_str: str) -> dict:
    """
    Parse requirements
    :param requirements_str:
    :return: dict
    """
    if isinstance(requirements_str, dict):
        return requirements_str
    assert isinstance(requirements_str, str), 'Invalid requirements type'
    try:
        return json.loads(requirements_str)
    except json.decoder.JSONDecodeError:
        parts = requirements_str.split('&')
        if len(parts) == 0:
            raise ValueError('no requirements given')
        requirements = dict()
        for part in parts:
            key, value = part.split('=')
            if not (key and value):
                raise ValueError('value or key missing')
            requirements[key] = value
        return requirements


class GracefulProcess(Thread):
    def __init__(self, command, env={}):
        super().__init__()
        signal.signal(signal.SIGINT, self._sigint)

        self.handle = subprocess.Popen(command,
                                shell=True, bufsize=0,
                                stdout=sys.stdout, stderr=sys.stderr,
                                cwd=os.curdir, env=env)
        self.start()
        self._kill = Event()

    @property
    def returncode(self):
        return self.handle.returncode

    def _sigint(self, signum, frame):
        print('sigint:Graceful kill subprocess')
        self.handle.send_signal(signal.SIGINT)
        self._kill.set()

    def communicate(self):
        while self.handle.poll() is None:
            if self._kill.is_set():
                print('sigint:allow 7 seconds to teardown nicely')
                try:
                    self.handle.wait(7.0)
                    break
                except subprocess.TimeoutExpired:
                    print('sigint:killing not so gently')
                    self.handle.send_signal(signal.SIGTERM)
                try:
                    self.handle.wait(2.0)
                    break
                except subprocess.TimeoutExpired:
                    print('sigint:even sigterm didnt help, lets kill it.')
                    self.handle.send_signal(signal.SIGKILL)
                try:
                    self.handle.wait(2)
                except subprocess.TimeoutExpired:
                    print('sigint:ohno..')
                    break

#p = GracefulProcess('scratch_2.sh')
#p.communicate()
