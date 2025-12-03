#task2:

import time
import datetime
import RPi.GPIO as GPIO
import board
from mfrc522 import MFRC522
from config import *

def feedback_accepted():
    GPIO.output(buzzerPin, 0)
    
    for i in range(4):
        GPIO.output(led1, True)
        time.sleep(0.05)
        GPIO.output(led1, False)
        time.sleep(0.05)
    
    GPIO.output(buzzerPin, 1) 


def rfid_loop():
    MIFAREReader = MFRC522()
    
    last_uid = None
    card_present = False


    while True:
        (status_req, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        
        if status_req == MIFAREReader.MI_OK or card_present:
            card_present=False
            (status_anti, uid) = MIFAREReader.MFRC522_Anticoll()
            uid_str = "-".join([str(x) for x in uid])
            print(uid_str)
            if status_anti == MIFAREReader.MI_OK:
                
                if uid_str == last_uid:
                    time.sleep(1)
                    card_present=True
                else:
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    uid_str = "-".join([str(x) for x in uid])
                    
                    print("feedback")
                    feedback_accepted()
                    
                    last_uid = uid_str
                    card_present = True
                    
                    
        else:
            print("status not ok")
            last_uid = None
            card_present=False

        time.sleep(0.1)

def main():
    try:
        GPIO.output(buzzerPin, 1)
        diode1 = GPIO.PWM(led1, 50)
        rfid_loop()
        
    except KeyboardInterrupt:
        print("\nZakończono działanie.")
        GPIO.cleanup()
        pixels.fill((0, 0, 0))
        pixels.show()

if __name__ == "__main__":
    main()
