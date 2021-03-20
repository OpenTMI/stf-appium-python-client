from os import environ
from time import sleep

from stf_appium_client import StfClient

client = StfClient(host=environ.get('STF_HOST'))
client.connect(token=environ.get('STF_TOKEN'))
client.get_devices()
dev = client.find_and_allocate(dict(version='10'))
sleep(2)
client.remote_connect(dev)
sleep(2)
client.release(dev)
