import time
from umqttrobust import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
import BME280
from machine import Pin, I2C

esp.osdebug(None)
import gc
gc.collect()

# Define Wi-Fi and MQTT configuration
ssid = '<name>'
password = '<password>'
mqtt_server = '<IP-Adres>'
mqtt_port = 8883
ca_cert = "ca_cert.pem"  

# Define MQTT topic
topic_pub = b'esp/bme280/data'

client_id = ubinascii.hexlify(machine.unique_id())

last_message = 0
message_interval = 5

station = network.WLAN(network.STA_IF)

def connect_wifi():
    station.active(True)
    station.connect(ssid, password)
    while not station.isconnected():
        pass

# Initialize the BME280 sensor
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=10000)
bme = BME280.BME280(i2c=i2c)

# Attempt to establish Wi-Fi connection
connect_wifi()

