## OpenSTF+Appium Client for test automation

[![Unit tests](https://github.com/OpenTMI/stf-appium-python-client/actions/workflows/test.yml/badge.svg)](https://github.com/OpenTMI/stf-appium-python-client/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/OpenTMI/stf-appium-python-client/badge.svg?branch=main&t=CQV17G)](https://coveralls.io/github/OpenTMI/stf-appium-python-client?branch=main)

Library provides basic functionality for test automation which allows allocating
phone from OpenSTF server, initialise adb connection to it and 
start appium server for it.

Basic idea is to run tests against remote openstf device farm with minimum
requirements.


### Flow
```
stf-appium-client      --find/allocate--> OpenSTF(device)
stf-appium-client      --remoteConnect--> OpenSTF(device)
stf-appium-client(ADB) <----------------> OpenSTF(ADB)
stf-appium-client(appium(ADB))
..appium tests..
```

### Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
* openstf server and access token 
* python >=3.7
* adb
* appium (`npm install appium`)
  Library expects that appium is located to PATH

### Installing

* `pip install stf-appium-client`
  
or for development purpose:

* `pip install -e .`

### Running the tests

`make test`

CI runs tests against following environments:

|   | ubuntu-latest | macos-latest | windows-latest |
| ------------- | ------------- | ------------- | ------------- |
| 3.7  | ✓  | ✓  | ✓  |
| 3.8  | ✓  | ✓  | ✓  |
| 3.9  | ✓  | ✓  | ✓  |

### Deployment

This pip package could be installed together with test framework
and utilise using CLI interface or via python interface. 
See more usage examples below.

### usage

#### Python Library

```
client = StfClient(host=environ.get('STF_HOST'))
client.connect(token=environ.get('STF_TOKEN'))

with client.allocation_context(
        requirements=dict(version='10')) as device:
    print('phone is now allocated and remote connected')
    with AdbServer(device['remote_adb_url']) as adb_port:
        print('adb server started with port: {adb_port}')
            with Appium() as appium:
                print("Phone is ready for test automation..")
                # appium is running and ready for usage
```

See examples from [examples](examples) -folder.

#### CLI

```shell script
stf --token 123456 --requirements "{\"version\": \"9\"}" "echo $DEV1_SERIAL"
```

Call robot framework
```shell script
stf --token 123456 --requirements "{\"version\": \"9\"}" "robot phone/suite" 
```


```shell script
$ stf --help
usage: stf [-h] --token TOKEN [--host HOST] [--requirements R]
           [command [command ...]]

STF client with appium.

Tool allocate phone, create adb and appium server and 
call user given command with generated env variables:
DEV1_ADB_PORT      ADB PORT that appium utilize.
DEV1_APPIUM_HOST   appium host where user given command can connect, e.g. robot framework
DEV1_SERIAL        device details..
DEV1_VERSION
DEV1_REQUIREMENTS  user given requirements
DEV1_INFO          phone details

positional arguments:
  command           Command to be execute during device allocation

optional arguments:
  -h, --help        show this help message and exit
  --token TOKEN     openstf access token
  --host HOST       openstf host
  --requirements R  requirements as json string
```

License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
