import os
import machine
import sdcard
import uos

import sdcard

from machine import Pin, SPI, reset

sd = sdcard.SDCard(SPI(0), Pin(17))  
os.mount(sd, '/sd')
print("SD card mounted")

def delete_file(filename):
    file_path = f"/sd/{filename}"
    
    try:
        if filename in os.listdir("/sd"):
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        else:
            print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error deleting file: {e}")

# Example usage: Delete 'test.txt' from the SD card
# delete_file("inspireFly_Capture_1.jpg")
# delete_file("inspireFly_Capture_2.jpg")
# delete_file("inspireFly_Capture_3.jpg")
# delete_file("last_num.txt")
print(os.listdir("/sd"))

# Unmount SD card (optional, to prevent corruption)
uos.umount("/sd")
