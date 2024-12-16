import socket
import json
import shutil
from contextlib import closing


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
    if requirements_str == "":
        return dict()
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

            def split(dest, subkey):
                if '.' in subkey:
                    keys = subkey.split('.')
                    key1 = keys[0]
                    rest = '.'.join(keys[1:])
                    dest[key1] = {}
                    split(dest[key1], rest)
                else:
                    dest[subkey] = value
            split(requirements, key)
        return requirements
