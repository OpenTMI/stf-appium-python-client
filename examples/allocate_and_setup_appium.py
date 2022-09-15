from os import environ
from time import sleep
import logging

from stf_appium_client import StfClient, AdbServer, AppiumServer

client = StfClient(host=environ.get('STF_HOST'))
#client.logger.setLevel(logging.DEBUG)
client.connect(token=environ.get('STF_TOKEN'))

dev = client.find_and_allocate(dict())
uri = client.remote_connect(dev)
adb = AdbServer(uri)
adb.connect()
appium = AppiumServer()
uri = appium.start()
print(f'appium uri: {uri}')
sleep(10)

appium.stop()
adb.kill()
client.release(dev)
