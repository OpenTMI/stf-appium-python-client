from os import environ
from time import sleep

from stf_appium_client import StfClient


client = StfClient(host=environ.get('STF_HOST'))
client.connect(token=environ.get('STF_TOKEN'))
devs = client.get_devices()
client.allocate(devs[0])
sleep(2)
client.remote_connect(devs[0])
sleep(2)
client.release(devs[0])
