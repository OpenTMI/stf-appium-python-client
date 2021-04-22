#! python3

import argparse
import json
import os
import sys
import subprocess
from stf_appium_client.StfClient import StfClient
from stf_appium_client.AdbServer import AdbServer
from stf_appium_client.Appium import Appium
from stf_appium_client.tools import parse_requirements

MIN_PYTHON = (3, 7)
assert sys.version_info >= MIN_PYTHON, f"requires Python {'.'.join([str(n) for n in MIN_PYTHON])} or newer"
RETCODE_FAILURE = 1


def main():
    parser = argparse.ArgumentParser(
        description='STF client with appium.'
                    'Tool allocate phone, create adb and appium server and \n'
                    'call user given command with generated env variables:\n'
                    'DEV1_ADB_PORT      ADB PORT that appium utilize.\n'
                    'DEV1_APPIUM_HOST   appium host where user given command can connect, e.g. robot framework\n'
                    'DEV1_SERIAL        device details..\n'
                    'DEV1_VERSION\n'
                    'DEV1_MODEL\n'
                    'DEV1_MARKET_NAME\n'
                    'DEV1_REQUIREMENTS  user given requirements\n'
                    'DEV1_INFO          phone details\n',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--token',
                        required=True,
                        help='openstf access token')
    parser.add_argument('--host',
                        default='http://localhost:7100',
                        help='openstf host')
    parser.add_argument('--requirements', metavar='R', type=str,
                        default="{}",
                        help='requirements as json string')
    parser.add_argument('command', nargs='*',
                        help='Command to be execute during device allocation')

    args = parser.parse_args()
    try:
        requirement = parse_requirements(args.requirements)
    except ValueError as error:
        print(f"Invalid requirements: {error}")
        exit(1)

    AdbServer.ok()

    returncode = RETCODE_FAILURE

    client = StfClient(host=args.host)
    client.connect(token=args.token)
    with client.allocation_context(requirements=requirement) as device:

        with AdbServer(device['remote_adb_url']) as adb:
            print(f'adb server listening localhost:{adb.port}')
            with Appium() as appium:
                print(f"appium server listening localhost:{appium.port}")

                print(f'Device in use: {device.manufacturer}:{device.marketName}, model: {device.model}, sn: {device.serial}')
                my_env = os.environ.copy()
                my_env["DEV1_ADB_PORT"] = f"{adb.port}"
                my_env["DEV1_APPIUM_HOST"] = f'127.0.0.1:{appium.port}'
                my_env["DEV1_SERIAL"] = device.serial
                my_env["DEV1_VERSION"] = device.version
                my_env["DEV1_MODEL"] = device.model
                my_env["DEV1_MANUFACTURER"] = device.manufacturer
                my_env["DEV1_MARKET_NAME"] = device.marketName
                my_env["DEV1_REQUIREMENTS"] = f"{requirement}"
                my_env["DEV1_INFO"] = json.dumps(device)

                command = " ".join(args.command)
                print(f"call: {command}")
                proc = subprocess.Popen(command,
                                        shell=True,
                                        stdout=sys.stdout, stderr=sys.stderr,
                                        cwd=os.curdir, env=my_env)
                proc.communicate()
                returncode = proc.returncode
    exit(returncode)


if __name__ == "__main__":
    main()
