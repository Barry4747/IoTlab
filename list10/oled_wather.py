#task 1

import time
import board
import busio
from PIL import Image, ImageDraw, ImageFont
import lib.oled.SSD1331 as SSD1331
import adafruit_bme280.advanced as adafruit_bme280
from config import *

def draw_icons(draw):
    c_temp = "RED"
    c_hum = "BLUE"
    c_press = "GREEN"
    
    draw.ellipse((2, 2, 8, 8), outline=c_temp, fill=c_temp)
    draw.line((5, 2, 5, 0), fill=c_temp)
    
    draw.polygon([(5, 22), (2, 28), (8, 28)], fill=c_hum)
    
    draw.ellipse((2, 44, 10, 52), outline=c_press)
    draw.line((6, 48, 8, 46), fill=c_press)

def main():
    disp = SSD1331.SSD1331()
    disp.Init()
    disp.clear()

    image = Image.new("RGB", (disp.width, disp.height), "BLACK")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype('./lib/oled/Font.ttf', 10)
    except IOError:
        font = ImageFont.load_default()

    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)
    
    bme280.sea_level_pressure = 1013.25
    bme280.standby_period = adafruit_bme280.STANDBY_TC_500

    try:
        while True:
            draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
            
            temp = bme280.temperature
            hum = bme280.humidity
            press = bme280.pressure
            
            draw_icons(draw)
            
            draw.text((15, 0), f"{temp:.1f} C", font=font, fill="WHITE")
            draw.text((15, 20), f"{hum:.1f} %", font=font, fill="WHITE")
            draw.text((15, 42), f"{press:.0f} hPa", font=font, fill="WHITE")
            
            disp.ShowImage(image, 0, 0)
            
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nZatrzymano program.")
        disp.clear()
        disp.reset()

if __name__ == "__main__":
    main()