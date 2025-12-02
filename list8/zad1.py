#!/usr/bin/env python3

from config import *
import RPi.GPIO as GPIO
import time

current_led = 1  
brightness = 50  
pwm_objects = {}  
encoder_last_state = None
encoder_jump = 5

leds = {
    1: led1,
    2: led2,
    3: led3,
    4: led4
}

def init_pwm():
    global pwm_objects
    for led_num, led_pin in leds.items():
        pwm_objects[led_num] = GPIO.PWM(led_pin, 100)
        pwm_objects[led_num].start(0)

def update_display():
    for led_num in leds.keys():
        if led_num == current_led:
            pwm_objects[led_num].ChangeDutyCycle(brightness)
        else:
            pwm_objects[led_num].ChangeDutyCycle(0)
    
    print(f'\rLED {current_led} | Jasność: {brightness:3d}%', end='', flush=True)

def encoder_callback(channel):
    global brightness, encoder_last_state

    left_state = GPIO.input(encoderLeft)
    right_state = GPIO.input(encoderRight)

    if right_state == GPIO.LOW:
        brightness = min(100, brightness + encoder_jump)
    elif left_state == GPIO.LOW:
        brightness = max(0, brightness - encoder_jump)
        
    
    
    update_display()

def button_red_callback(channel):
    global current_led
    current_led = current_led - 1 if current_led > 1 else 4
    print(f'\n--- Wybrano LED {current_led} ---')
    update_display()

def button_green_callback(channel):
    global current_led
    current_led = current_led + 1 if current_led < 4 else 1
    print(f'\n--- Wybrano LED {current_led} ---')
    update_display()

def setup_events():
    GPIO.add_event_detect(encoderLeft, GPIO.FALLING, 
                         callback=encoder_callback, bouncetime=20)
    
    GPIO.add_event_detect(buttonRed, GPIO.FALLING, 
                         callback=button_red_callback, bouncetime=200)
    GPIO.add_event_detect(buttonGreen, GPIO.FALLING, 
                         callback=button_green_callback, bouncetime=200)

def main():
    init_pwm()
    setup_events()
    update_display()
    
    try:
        while True:
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\n\nZakończenie programu")
    
    finally:
        for pwm in pwm_objects.values():
            pwm.stop()
        GPIO.cleanup()
        print("Program zakończony.")

if __name__ == "__main__":
    main()