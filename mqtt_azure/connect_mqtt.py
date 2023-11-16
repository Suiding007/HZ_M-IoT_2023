import paho.mqtt.client as mqtt
from azure.iot.device import IoTHubDeviceClient, Message
import sqlite3 as sql
import datetime as datetime
import json

#MQTT Raspberry
broker = '<IP-Adres>'
port = 8883
topic = "esp/bme280/data"
DeviceID = f'python-mqtt-{1}'

username = '<Name>'
password = '<Password}>'


#connection to the MQTT server
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(topic)
    else:
        print(f"Failed to connect, return code {rc}")


    ######################sending data from mqtt server to database##############################

def on_message(client, userdata, msg):
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    
    status = False

    print()
    print("################################################")
    test =json.loads(msg.payload.decode())
    temp = float(test["temperature"].rstrip('C'))
    hum = float(test["humidity"].rstrip('%'))
    pressure_str = test["pressure"]
    pres = int(''.join(filter(str.isdigit, pressure_str)))
    time_ras = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")   #https://www.programiz.com/python-programming/datetime/current-datetime

    print(DeviceID) 
    print("temprature:", temp)
    print("humidity:",hum)
    print("pressure:",pres)
    print("time:",time_ras)
    
    
    
    #####################################database#############################################
    con = sql.connect('fund.db')
    cur = con.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS data (
            DeviceID VARCHAR(255),
            temp FLOAT,
            hum FLOAT,
            pres NUMERIC,
            time_ras DATETIME,
            status BOOLEAN
            
        )''')
    #####################################database#############################################


    if status == False:
        cur.execute('''
        INSERT INTO data (DeviceID,temp, hum, pres, time_ras, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (DeviceID, temp, hum, pres, time_ras, status))

    con.commit()
    con.close()
    ######################sending data from mqtt server to database##############################


def connect_mqtt() -> mqtt.Client:
    client = mqtt.Client(DeviceID)
    client.username_pw_set(username, password)
    client.tls_set(ca_certs="/etc/mosquitto/certs/ca-crt.pem")
    client.tls_insecure_set(True)  
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)
    return client


def run():
    client = connect_mqtt()
    client.loop_forever()
    
       
if __name__ == '__main__':
    run()
