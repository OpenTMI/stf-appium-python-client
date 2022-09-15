#! python3
from subprocess import PIPE
import argparse
import json
import os
import sys
import subprocess
from stf_appium_client.StfClient import StfClient
from stf_appium_client.AdbServer import AdbServer
from stf_appium_client.AppiumServer import AppiumServer
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
                    'DEV1_MANUFACTURER\n'
                    'DEV1_MODEL\n'
                    'DEV1_MARKET_NAME\n'
                    'DEV1_REQUIREMENTS  user given requirements\n'
                    'DEV1_INFO          phone details\n'
                    '\nExample: stf --token 123 -- echo \$DEV1_SERIAL',
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
    parser.add_argument('--list',
                        action='store_true',
                        help='Only list devices as json')
    parser.add_argument('--timeout', metavar='t', type=int,
                        default=StfClient.DEFAULT_ALLOCATION_TIMEOUT_SECONDS,
                        help='allocation timeout')
    parser.add_argument('--wait_timeout', metavar='w', type=int,
                        default=60,
                        help='max wait time for suitable device allocation')
    parser.add_argument('--verbose', action="store_true",
                        help='appium logs to console. WARNING: this mix console prints')
    parser.add_argument('--appium-logs', metavar='file', type=str, default='',
                        help='appium logs to file')
    parser.add_argument('command', nargs='*',
                        help='Command to be execute during device allocation')

    args = parser.parse_args()
    try:
        requirement = parse_requirements(args.requirements)
    except ValueError as error:
        print(f"Invalid requirements: {error}")
        exit(1)

    if not os.environ.get('CI'):
        AdbServer.ok()

    returncode = RETCODE_FAILURE

    client = StfClient(host=args.host)
    client.connect(token=args.token)

    if args.list:
        print(client.list_devices(requirements=requirement))
        exit(0)

    with client.allocation_context(requirements=requirement,
                                   wait_timeout=args.wait_timeout,
                                   timeout_seconds=args.timeout) as device:
        try:
            with AdbServer(device['remote_adb_url']) as adb:
                adb.logger.info(f'adb server listening localhost:{adb.port}')
                try:
                    extra_args = dict(stdout=sys.stdout.fileno(), stderr=sys.stderr.fileno()) if args.verbose else {}
                    appium_args = []
                    if args.appium_logs:
                        appium_args.extend(['--log', args.appium_logs])
                    with AppiumServer(appium_args=appium_args, **extra_args) as appium:
                        appium.logger.info(f"appium server listening localhost:{appium.port}")

                        appium.logger.info(f'Device in use: {device.manufacturer}:{device.marketName}, model: {device.model}, sn: {device.serial}')

                        custom_env = {}
                        custom_env["DEV1_ADB_PORT"] = f"{adb.port}"
                        custom_env["DEV1_APPIUM_HOST"] = f'127.0.0.1:{appium.port}'
                        custom_env["DEV1_APPIUM_WD_HUB_URI"] = f'http://127.0.0.1:{appium.port}/wd/hub'
                        custom_env["DEV1_SERIAL"] = device.serial
                        custom_env["DEV1_VERSION"] = device.version
                        custom_env["DEV1_MODEL"] = device.model
                        custom_env["DEV1_MANUFACTURER"] = device.manufacturer
                        custom_env["DEV1_MARKET_NAME"] = device.marketName
                        custom_env["DEV1_REQUIREMENTS"] = f"{requirement}"
                        custom_env["DEV1_INFO"] = json.dumps(device)
                        appium.logger.info('Env variables:')
                        for key in custom_env.keys():
                            appium.logger.info(f'{key}={custom_env[key]}')

                        # merge available env variables
                        my_env = os.environ.copy()
                        my_env.update(custom_env)

                        command = " ".join(args.command)
                        appium.logger.info(f"call: {command}")
                        proc = subprocess.Popen(command,
                                                shell=True,
                                                stdout=sys.stdout, stderr=sys.stderr,
                                                cwd=os.curdir, env=my_env)
                        proc.communicate()
                        returncode = proc.returncode
                except Exception as error:
                    client.logger.error(error)
        except Exception as error:
            client.logger.error(error)
    exit(returncode)


if __name__ == "__main__":
    main()
