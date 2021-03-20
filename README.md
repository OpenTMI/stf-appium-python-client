## OpenSTF client with appium capability for test automation

### Installation

Requirements:
* python >=3.7


### Usage

```shell script
python stf.py --token 123456 --requirements "{\"version\": \"9\"}" "echo $DEV1_SERIAL"
```

Call robot framework
```shell script
python stf.py --token 123456 --requirements "{\"version\": \"9\"}" "robot phone/suite" 
```

### dynamic environment variables for <command>

| variable          | note | example |
|-------------------|------|---------|
| `DEV1_ADB_PORT`     | local adb port | `123` |
| `DEV1_APPIUM_HOST`  | appium host address | `127.0.0.1:8100` |
| `DEV1_SERIAL`       | device serial number  | `B2NGAA8831600525`  |
| `DEV1_REQUIREMENTS` | device requirements as json string  | `{'version': '10'}` |
| `DEV1_INFO`         | device info as json string |  `{'manufacturer': 'HMD GLOBAL', 'version': '10', 'ready': True, 'platform': 'Android', 'owner': 'me', 'using': False, 'present': True, 'sdk': '29', 'model': ' 7 plus', 'serial': 'B2NGAA8831600525'}`  |

### Help

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
