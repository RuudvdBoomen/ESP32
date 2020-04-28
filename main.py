# Temperature imports
from machine import Pin, I2C
from time import sleep
import BME280
from umqttsimple import MQTTClient
from ntptime import settime

from boot import *

# ESP32 - Pin assignment
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=10000)

def sub_cb(topic, msg):
  print((topic, msg))
  if topic == b'home/summerhouse/lights':
    print(b'message')

def connect_and_subscribe():
  global client_id, MQTT_SERVER, topic_sub
  client = MQTTClient(client_id, MQTT_SERVER, user=MQTT_USER, password=MQTT_PASSWORD)
  client.set_callback(sub_cb)
  client.connect()
  # client.subscribe(topic_sub)
  print('Connected to %s MQTT broker' % MQTT_SERVER)
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

# Convert the a tuple: (2020, 4, 25, 5, 15, 17, 56, 97) to a string: "2012-04-25 15:17:00"
def get_date_string():
  rtc = machine.RTC()
  year = rtc.datetime()[0]
  month = rtc.datetime()[1] if rtc.datetime()[1] > 9 else "0%s" % rtc.datetime()[1]
  day = rtc.datetime()[2] if rtc.datetime()[2] > 9 else "0%s" % rtc.datetime()[2]
  #  Add 2 to hour since it uses UTC and in the Netherlands we have UTC+2 as timezone.
  hour = (rtc.datetime()[4]+2) if (rtc.datetime()[4]+2) > 9 else "0%s" % (rtc.datetime()[4]+2)
  minute = rtc.datetime()[5] if rtc.datetime()[5] > 9 else "0%s" % rtc.datetime()[5]

  return "%s-%s-%s %s:%s:00" % (year, month, day, hour, minute)

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    client.check_msg()
    if (time.time() - last_message) > message_interval:
      bme = BME280.BME280(i2c=i2c)
      temp = bme.temperature
      hum = bme.humidity
      pres = bme.pressure
      settime()
      date = get_date_string()
      print("Date: %s, Temp: %s, Hum %s, Pres %s" % (date, temp, hum, pres))
      msg = b'{ "temperature": %s, "humidity": %s, "pressure": %s, "measured": "%s"}' % (temp, hum, pres, date) 
      client.publish(topic_pub, msg, retain=True)
      last_message = time.time()
  except OSError as e:
    restart_and_reconnect()




