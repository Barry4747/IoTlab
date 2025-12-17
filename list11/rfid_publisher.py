import time
import datetime
import json
import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import paho.mqtt.client as mqtt

buzzerPin = 23
led1 = 24

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "lab/rfid/access"

def on_connect(client, userdata, flags, rc):
    pass

client = mqtt.Client()
client.on_connect = on_connect
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
except:
    pass

def feedback_accepted():
    GPIO.output(buzzerPin, 0)
    for i in range(2):
        GPIO.output(led1, True)
        time.sleep(0.1)
        GPIO.output(led1, False)
        time.sleep(0.1)
    GPIO.output(buzzerPin, 1)

def rfid_loop():
    MIFAREReader = MFRC522()
    last_uid = None

    while True:
        (status_req, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        if status_req == MIFAREReader.MI_OK:
            (status_anti, uid) = MIFAREReader.MFRC522_Anticoll()

            if status_anti == MIFAREReader.MI_OK:
                uid_str = "-".join([str(x) for x in uid])

                if uid_str != last_uid:
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    payload = {
                        "card_id": uid_str,
                        "timestamp": current_time,
                        "reader_id": "Reader_Lab_1"
                    }
                    
                    client.publish(MQTT_TOPIC, json.dumps(payload))
                    feedback_accepted()
                    last_uid = uid_str
                
        else:
            last_uid = None

        time.sleep(0.1)

def main():
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(buzzerPin, GPIO.OUT)
        GPIO.setup(led1, GPIO.OUT)
        
        GPIO.output(buzzerPin, 1) 
        GPIO.output(led1, False)

        rfid_loop()
        
    except KeyboardInterrupt:
        client.loop_stop()
        client.disconnect()
        GPIO.cleanup()

if __name__ == "__main__":
    main()