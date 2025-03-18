import os
import sdcard
from machine import Pin, SPI, reset

sd = sdcard.SDCard(SPI(0), Pin(17))  
os.mount(sd, '/sd')

print(os.listdir('/sd'))

def move_file(source, destination):
    """Move a file from internal storage to SD card"""
    try:
        # Read the file from internal storage
        with open(source, 'rb') as f_source:
            data = f_source.read()

        # Write the file to the SD card
        with open(destination, 'wb') as f_dest:
            f_dest.write(data)

        # Delete the original file from internal storage
        os.remove(source)
        print(f"File moved from {source} to {destination}")

    except Exception as e:
        print(f"Error: {e}")

# Move "test.txt" from internal storage to SD card
# move_file('/inspireFly_Capture_0.jpg', '/sd/inspireFly_Capture_0.jpg')
#move_file('/last_num.txt', '/sd/last_num.txt')

# Verify the file is on the SD card
print("Files on SD:", os.listdir('/sd'))