from paho.mqtt import client as mqtt_client
from influxdb import InfluxDBClient
from pymongo import MongoClient
import pymongo
import random
import json

broker_mqtt = "localhost"
port_mqtt = 1883
topic_mqtt = "selfbalancing"
client_id_mqtt = f'python-mqtt-{random.randint(0, 1000)}'

server_influx = "localhost"
port_influx = 8086
database_influx = "selfbalancing"
client_influx = InfluxDBClient(host=server_influx, port=port_influx, database=database_influx)

client_mongodb = MongoClient('localhost', 27017)
database_mongodb = client_mongodb["selfbalancing"]
collection_mongodb = database_mongodb["selfbalancing"]

def connect_mqtt():
    def on_connect(client_mqtt, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Connection failed!")
    client_mqtt = mqtt_client.Client(client_id_mqtt)
    client_mqtt.on_connect = on_connect
    client_mqtt.connect(broker_mqtt, port_mqtt)
    return client_mqtt

def subscribe(client_mqtt: mqtt_client):
    def on_message(client_mqtt, userdata, msg):
        value = str(msg.payload, 'utf-8')
        json_body = [
            {
            "measurement": "selfbalancing",
            "tags": {},
            "fields": {
                "value": value
                }
            }
        ]
        client_influx.write_points(json_body)
        print("inserted data on influxdb")
        value = json.loads(value)
        json_mongo = {
            "gyroy":value["measure"]["gyroy"],
            "kalangley":value["measure"]["kalangley"],
            "pitch":value["measure"]["pitch"],
            "res":value["measure"]["res"],
            "kd":value["measure"]["kd"],
            "ki":value["measure"]["ki"],
            "kp":value["measure"]["kp"],
            }
        insert_mongodb = collection_mongodb.insert_one(json_mongo)
        print("inserted data on mongodb")
    client_mqtt.subscribe(topic_mqtt)
    client_mqtt.on_message = on_message

def run():
    client_mqtt = connect_mqtt()
    subscribe(client_mqtt)
    client_mqtt.loop_forever()

if __name__ == "__main__":
    #client_influx.create_database(database_influx)
    run()