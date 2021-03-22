import socket
import json
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
