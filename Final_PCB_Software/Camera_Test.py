import time
import os


from machine import Pin, SPI, reset

from Camera import Camera

cam_Pin = Pin(12, Pin.OUT, value=0)

spi_camera = SPI(1, sck=Pin(10), miso=Pin(8), mosi=Pin(11), baudrate=8000000)

cs = Pin(9, Pin.OUT)

cam = Camera(spi_camera, cs)


imageName = "test_image7"

finalImageName = f"/sd/{imageName}.jpg"

print("Saving at: ", finalImageName)

time.sleep(0.5)

try:
    cam.capture_jpg()
except Exception as e:
    print("Error during capture:", e)

time.sleep(0.5)
cam.saveJPG(finalImageName)


