import time
from umqttrobust import MQTTClient
import ubinascii
import machine
import network
import esp
import BME280
import ujson
from machine import Pin, I2C

while True:
    try:
        if not station.isconnected():
            # Wi-Fi connection lost, attempt to reconnect
            connect_wifi()
            print('Reconnected to Wi-Fi')

        if (time.time() - last_message) > message_interval:
            temp = bme.temperature
            hum = bme.humidity
            pres = bme.pressure
            
            print("temprature:", temp)
            print("humidity:",hum)
            print("pressure:",pres)
            print()

            data = {
                "temperature": temp,
                "humidity": hum,
                "pressure": pres
            }

            json_data = ujson.dumps(data)
            client = MQTTClient(client_id, mqtt_server, port=mqtt_port, user='bodhi-raspberrypi', password='Raspberrypi', ssl=ca_cert)
            client.connect()
            client.publish(topic_pub, json_data)
            client.disconnect()

            last_message = time.time()
    except OSError as e:
        pass


