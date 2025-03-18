from machine import Pin, I2C
import time

# Initialize I2C on bus 0 (change pins if needed)

i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=400000)

print(i2c.scan())

    
    
    