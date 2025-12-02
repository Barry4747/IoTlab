import time
import board
import busio
import math
import adafruit_bme280.advanced as adafruit_bme280

def oblicz_wysokosc(cisnienie_hpa, cisnienie_odniesienia=1013.25):
    """
    Oblicza wysokość n.p.m. na podstawie wzoru hipsometrycznego.
    Wzór: h = 44330 * (1 - (p / p0)^(1/5.255))
    
    Argumenty:
    cisnienie_hpa -- aktualne ciśnienie zmierzone przez czujnik
    cisnienie_odniesienia -- ciśnienie na poziomie morza (standardowo 1013.25 hPa)
    """
    try:
        wysokosc = 44330 * (1.0 - math.pow(cisnienie_hpa / cisnienie_odniesienia, 0.1903))
        return wysokosc
    except ValueError:
        return 0.0

def main():
    i2c = busio.I2C(board.SCL, board.SDA)
    
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)

    bme280.sea_level_pressure = 1013.25 
    bme280.standby_period = adafruit_bme280.STANDBY_TC_500
    bme280.iir_filter = adafruit_bme280.IIR_FILTER_X16
    bme280.overscan_pressure = adafruit_bme280.OVERSCAN_X16
    bme280.overscan_humidity = adafruit_bme280.OVERSCAN_X1
    bme280.overscan_temperature = adafruit_bme280.OVERSCAN_X2

    print("\nRozpoczęcie pomiarów (BME280)...")
    print("Naciśnij CTRL+C, aby zakończyć.\n")

    try:
        while True:
            temp = bme280.temperature
            hum = bme280.humidity
            press = bme280.pressure
            
            altitude_calc = oblicz_wysokosc(press, 1013.25)
            
            print("-" * 30)
            print(f"Temperatura: {temp:0.1f} {chr(176)}C")
            print(f"Wilgotność:  {hum:0.1f} %")
            print(f"Ciśnienie:   {press:0.1f} hPa")
            print(f"Wysokość:    {altitude_calc:0.2f} m n.p.m.")
            
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nProgram zatrzymany przez użytkownika.")
        GPIO.cleanup()

if __name__ == "__main__":
    main()