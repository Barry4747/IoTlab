import paho.mqtt.client as mqtt
import json
import time

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "lab/rfid/access"
LOG_FILE = "rfid_log.txt"

def save_to_file(data):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{data['timestamp']}] ID: {data['card_id']}\n")
    except IOError:
        pass

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode("utf-8")
        data = json.loads(payload_str)
        print(f"{data['card_id']} {data['timestamp']}")
        save_to_file(data)
    except:
        pass

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()
except:
    pass