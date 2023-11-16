from azure.iot.device import IoTHubDeviceClient, exceptions
import sqlite3 as sql
import time
import json

# Connection to Azure
iothub = "put your connection string here"

def connect_to_azure():
    device = IoTHubDeviceClient.create_from_connection_string(iothub)

    while True:
        try:
            device.connect()
            print("Connected to Azure IoT Hub")
            return device
        except exceptions.ConnectionFailedError as ex:
            print(f"Connection to Azure failed: {ex}")
            time.sleep(5)

def get_data():
    con = sql.connect('fund.db')
    cur = con.cursor()

    cur.execute('''
        SELECT DeviceID, temp, hum, pres, time_ras, status
        FROM data
        WHERE status = 0
        ORDER BY time_ras DESC
    ''')
    return cur.fetchall()

def send_data(device, rows):
    con = sql.connect('fund.db')

    try:
        for row in rows:
            print(row)
            time.sleep(5)
            DeviceID, temp, hum, pres, time_ras, status = row

            payload = {
                "DeviceID": DeviceID,
                "temp": temp,
                "hum": hum,
                "pres": pres,
                "time_ras": time_ras,
                "status": status
            }
            message = json.dumps(payload)

            try:
                device.send_message(message)
                print("Message sent successfully")
                cur = con.cursor()
                cur.execute('''
                    UPDATE data
                    SET status = 1
                    WHERE DeviceID = ? AND status = 0
                ''', (DeviceID,))
                con.commit()
                
            except exceptions.ConnectionDroppedError as ex:
                print(f"Connection to Azure dropped: {ex}")
                break  

            except Exception as e:
                print(f"An error occurred while sending message: {e}")

    finally:
        con.close()



def run():
    azure_device = connect_to_azure()
    should_fetch_data = True  

    while True:
        try:
            rows = get_data()

            if rows:
                send_data(azure_device, rows)
            else:
                print("No data to send")

            time.sleep(5)  

        except exceptions.ConnectionDroppedError as ex:
            print(f"Connection to Azure dropped: {ex}")
            should_fetch_data = False  
            azure_device = connect_to_azure()

        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(5)

        else:
            should_fetch_data = True  

if __name__ == '__main__':
    run()
