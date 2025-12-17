import time
import datetime
import json
import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import paho.mqtt.client as mqtt

# --- Configuration ---
BUZZER_PIN = 23
LED_PIN = 24

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "lab/rfid/access"
READER_ID = "Reader_Lab_1"

# --- MQTT Setup ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT Broker: {MQTT_BROKER}")
    else:
        print(f"Failed to connect, return code {rc}")

client = mqtt.Client()
client.on_connect = on_connect

# --- Hardware Feedback ---
def feedback_accepted():
    """
    Provides Audio/Visual feedback.
    Assumes Active Low Buzzer (0 = ON, 1 = OFF).
    """
    # Beep ON
    GPIO.output(BUZZER_PIN, 0) 
    
    # Blink LED twice
    for _ in range(2):
        GPIO.output(LED_PIN, True)  # LED ON
        time.sleep(0.1)
        GPIO.output(LED_PIN, False) # LED OFF
        time.sleep(0.1)
        
    # Beep OFF
    GPIO.output(BUZZER_PIN, 1)

# --- Main RFID Loop ---
def rfid_loop():
    MIFAREReader = MFRC522()
    last_uid = None

    print("RFID Reader Ready...")

    while True:
        # Scan for cards
        (status_req, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        if status_req == MIFAREReader.MI_OK:
            # Get the UID of the card
            (status_anti, uid) = MIFAREReader.MFRC522_Anticoll()

            if status_anti == MIFAREReader.MI_OK:
                uid_str = "-".join([str(x) for x in uid])

                # CHECK: Only process if this is a new read (debouncing)
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
                    
                    # Update state to prevent re-reading the same card immediately
                    last_uid = uid_str
                
        else:
            # If no card is found, reset the last_uid so the card can be read again if removed and replaced
            last_uid = None

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
