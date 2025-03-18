
# Created by Nicole Maggard and Michael Pham 8/19/2022
# Updated for Yearling by Nicole Maggard and Rachel Sarmiento 2/4/2023
# This is where the processes get scheduled, and satellite operations are handeled

print("Hi inspireFly")

from lib.pysquared import cubesat as c
#import asyncio
import time
import traceback
import gc #Garbage collection
import microcontroller
import functions
from debugcolor import co
#from easy_comms_circuit import EasyComms

#from FCB_class import FCBCommunicator
import sdcardio

import os


f=functions.functions(c)





def debug_print(statement):
    if c.debug:
        print(co("[MAIN]" + str(statement), 'blue', 'bold'))
        return


# Here is the start up loop so we can use the initialized cubesat
try:
    os.stat("/sd/StartedUp.txt")
    debug_print("Already started up! Skipping wait")
except OSError as e:
    print(e)
    print("Has not started up yet. Waiting 3000 seconds")    

    time.sleep(3000)
    
    try:
        with open("/sd/StartedUp.txt", "w") as file:
            debug_print("Creating StartedUp.txt")
            file.write("T\n")
    except Exception as e:
        print("Error creating StartedUp file: ", traceback.format_exception(e)) 

        
        
# --- Below is inspireFly's main Loop
# Boot sequence:
try:
    debug_print("Boot number: " + str(c.c_boot))
    
    c.all_faces_off()
    time.sleep(1)
    c.all_faces_on()
    
    c.battery_manager()
    
    c.deploy_antenna()
    
    c.deploy_boomarm()
    
    

    
except Exception as e:
    debug_print("Error in Boot Sequence: " + ''.join(traceback.format_exception(e)))
finally:
    debug_print("All Faces off!")
    
    
def critical_power_operations():
    # Note that were not listening. We don't want the satellite doing anything in this mode.
    f.default_beacon()
    time.sleep(10)
    f.default_beacon()
     
    f.Hybernate(590)

def minimum_power_operations():
    
    f.default_beacon() 
    f.listen(10)
    f.default_beacon()
    f.listen(10)
    
    f.Hybernate(110)
    
def normal_power_operations():
    
    f.battery_heater()
    f.default_beacon()
    f.listen(10)
    f.default_beacon()
    f.listen(30)
    
    
    
    
# inspireFlys Main Loop!
try:
    c.all_faces_on()
    
    drop_image_timer = 86400
    
    while True:
        #L0 automatic tasks no matter the battery level
        c.battery_manager()
        c.check_reboot()
        
        debug_print(f"Time since last communication is: {f.time_since_last_communication()}")
        debug_print(f"Dropping image in: {drop_image_timer - f.time_since_last_communication()}")
        if f.time_since_last_communication() > drop_image_timer:
                
            f.overhead_send(b'\x31')
            print("Waiting for picture taking process for 15 seconds...")
            time.sleep(15)
            
            f.overhead_send(b'\x32')
            f.pcb_comms()
            
            f.send_full_image()

            drop_image_timer += 5400
        
        
        if c.power_mode == 'critical':
            c.RGB=(0,0,0)
            critical_power_operations()
            
        elif c.power_mode == 'minimum':
            c.RGB=(255,0,0)
            minimum_power_operations()
            
        elif c.power_mode == 'normal':
            c.RGB=(255,255,0)
            normal_power_operations()
            
        elif c.power_mode == 'maximum':
            c.RGB=(0,255,0)
            normal_power_operations()       
        else:
            f.listen()
            
except Exception as e:
    debug_print("Error in Main Loop: " + ''.join(traceback.format_exception(e)))
    time.sleep(10)
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()
finally:
    #debug_print("All Faces off!")
    #c.all_faces_off()
    c.RGB=(0,0,0)


    
    
        
        


