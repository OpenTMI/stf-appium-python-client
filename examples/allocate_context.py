from os import environ
from time import sleep

from stf_appium_client import StfClient

client = StfClient(host=environ.get('STF_HOST'))
client.connect(token=environ.get('STF_TOKEN'))

with client.allocation_context(
        requirements=dict(version='10')) as device:
    print(device)


