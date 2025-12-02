#task2:

import time
import datetime
import RPi.GPIO as GPIO
import board
import neopixel
from mfrc522 import MFRC522
from config import *

NUM_PIXELS = 8
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(board.D18, NUM_PIXELS, brightness=0.2, auto_write=False)

def feedback_accepted():
    GPIO.output(buzzerPin, 0)
    
    pixels.fill((0, 255, 0))
    pixels.show()
    
    time.sleep(0.2) 
    
    GPIO.output(buzzerPin, 1) 
    pixels.fill((0, 0, 0))
    pixels.show()

def rfid_loop():
    MIFAREReader = MFRC522()
    
    last_uid = None
    card_present = False

    print("Oczekiwanie na karty RFID... (CTRL+C aby przerwać)")

    while True:
        (status_req, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        
        if status_req == MIFAREReader.MI_OK:
            (status_anti, uid) = MIFAREReader.MFRC522_Anticoll()
            
            if status_anti == MIFAREReader.MI_OK:
                if card_present and uid == last_uid:
                    pass 
                else:
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    uid_str = "-".join([str(x) for x in uid])
                    
                    print(f"[{current_time}] Zarejestrowano kartę UID: {uid_str}")
                    
                    feedback_accepted()
                    
                    last_uid = uid
                    card_present = True
        else:
            card_present = False
            last_uid = None

        time.sleep(0.1)

def main():
    try:
        GPIO.output(buzzerPin, 1)
        pixels.fill((0, 0, 0))
        pixels.show()
        
        rfid_loop()
        
    except KeyboardInterrupt:
        print("\nZakończono działanie.")
        GPIO.cleanup()
        pixels.fill((0, 0, 0))
        pixels.show()

if __name__ == "__main__":
    main()