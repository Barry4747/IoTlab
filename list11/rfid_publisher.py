import time
import datetime
import json
import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import paho.mqtt.client as mqtt

BUZZER_PIN = 23
LED_PIN = 24

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "lab/rfid/access"
READER_ID = "Reader_Lab_1"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT Broker: {MQTT_BROKER}")
    else:
        print(f"Failed to connect, return code {rc}")

client = mqtt.Client()
client.on_connect = on_connect

def feedback_accepted():
    GPIO.output(BUZZER_PIN, 0) 
    
    for _ in range(2):
        GPIO.output(LED_PIN, True) 
        time.sleep(0.1)
        GPIO.output(LED_PIN, False) 
        time.sleep(0.1)
        
    GPIO.output(BUZZER_PIN, 1)

def rfid_loop():
    MIFAREReader = MFRC522()
    last_uid = None
    
    no_card_counter = 0
    MISS_THRESHOLD = 5 

    print("RFID Reader Ready...")

    while True:
        (status_req, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        if status_req == MIFAREReader.MI_OK:
            no_card_counter = 0
            
            (status_anti, uid) = MIFAREReader.MFRC522_Anticoll()

            if status_anti == MIFAREReader.MI_OK:
                uid_str = "-".join([str(x) for x in uid])

                if uid_str != last_uid:
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    payload = {
                        "card_id": uid_str,
                        "timestamp": current_time,
                        "reader_id": READER_ID
                    }
                    
                    try:
                        client.publish(MQTT_TOPIC, json.dumps(payload))
                        print(f"Sent: {uid_str}")
                        feedback_accepted()
                    except Exception as e:
                        print(f"MQTT Publish Error: {e}")
                    
                    last_uid = uid_str
        
        else:
            no_card_counter += 1
        
            if no_card_counter > MISS_THRESHOLD:
                last_uid = None
                no_card_counter = MISS_THRESHOLD + 1

        time.sleep(0.1)

def main():
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(BUZZER_PIN, GPIO.OUT)
        GPIO.setup(LED_PIN, GPIO.OUT)
        
        GPIO.output(BUZZER_PIN, 1) 
        GPIO.output(LED_PIN, False)

        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_start()
        except Exception as e:
            print(f"Could not connect to MQTT Broker: {e}")

        rfid_loop()
        
    except KeyboardInterrupt:
        print("\nStopping...")
        client.loop_stop()
        client.disconnect()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
