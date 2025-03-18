#Code created by David Encarnacion with assistance from ChatGPT
#Last Updated: 11/4/2024 10:14
from machine import Pin, Timer

burn_a = Pin(5, Pin.OUT, value=0)
burn_b = Pin(4, Pin.OUT, value=0)


import utime
dog_pin = Pin(20, Pin.OUT)
dog_pin.value(0)

# Pet function
def pet(timer):
    dog_pin.value(1)
    utime.sleep_us(10000)  # Pull high for 1ms
    dog_pin.value(0)      # Pull low

# Create a hardware timer that calls `pet()` every 500ms
watchdog_timer = Timer()
watchdog_timer.init(freq=2, mode=Timer.PERIODIC, callback=pet)	





from PCB_class import PCB
import time

from watchdog import Watchdog

import machine

from antenna import are_antenna_deployed, deploy_antennas





try:
    print("Starting antenna code")
    if are_antenna_deployed():
        print("Antennas not deployed. Waiting for 3000 seconds...")
        time.sleep(3000)
        
        print("Attempting to deploy antennas")
        
        try:
            
            for i in range(10):
                deploy_antennas()

            
        except Exception as e:
            print(e)
                    
except Exception as e:
    print("Error in antenna code",e)
    print("Performing manual burn")

    
            

pcb_succesful = False

for i in range(6):
    
    try:
        pcb = PCB()
        pcb_succesful = True
        break  # Exit loop if successful
    except Exception as e:
        print(f"Error mounting PCB: {e}. Retrying...")  # Log the error
        
        time.sleep(0.5)

if pcb_succesful == False:
    machine.reset()






for i in range(10):
    try:
        pcb.TakePicture('PicForLarsen100', '128X128')
        break  # Exit loop if successful
    except Exception as e:
        print(f"Error taking picture: {e}. Retrying...")  # Log the error
        
        time.sleep(0.5)  # Small delay before retrying



pcb.display.display_on()
pcb.display_image('image1.raw')
time.sleep(0.5)

time.sleep(0.5)

pcb.display.clear()



pcb.wait_for_command()


#     pcb.TakePicture('PicForLarsen10', '640x480')

# print("Displaying image...")
#The image displayed, for the purposes of the
#mission, must be modifyable to pull the latest
#image uploaded by the ground station
#TODO: Replace 'RaspberryPiWB128x128.raw' with a variable
#directory, pulled from the FCB memory
# while True:
# pcb.display_image('/sd/potato.raw')
# 
#     count = (pcb.last_num + 2) - pcb.last_num
#     print("Initiating TakeMultiplePictures...")
# 
#     pcb.TakeMultiplePictures('inspireFly_Capture_', '320x240', 1, count)
#     file_path = f"/sd/inspireFly_Capture_{pcb.last_num}.jpg"
#     with open(file_path, "rb") as file:
#         jpg_bytes = file.read()
# 
#     print("Initiating data transmission with flight computer...")
#     pcb.communicate_with_fcb(jpg_bytes)