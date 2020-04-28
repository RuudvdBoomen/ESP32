import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network

from credentials import *

import esp
esp.osdebug(None)
import gc
gc.collect()

client_id = ubinascii.hexlify(machine.unique_id())
# topic_sub = b'home/summerhouse/lights'
topic_pub = b'home/summerhouse/temperature'

last_message = 0
message_interval = 15
counter = 0

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(WIFI_SSID, WIFI_PASSWORD)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())





