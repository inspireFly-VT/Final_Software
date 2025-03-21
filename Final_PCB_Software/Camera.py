from machine import Pin, SPI, reset

from utime import sleep_ms, sleep_us


import utime

import uos
import os
import ujson

import machine


class Camera:
    # Required imports
    
    ### Register definitions


    ## For camera Reset
    CAM_REG_SENSOR_RESET = 0x07
    CAM_SENSOR_RESET_ENABLE = 0x40
    
    ## For get_sensor_config
    CAM_REG_SENSOR_ID = 0x40
    
    SENSOR_5MP_1 = 0x81
    SENSOR_3MP_1 = 0x82
    SENSOR_5MP_2 = 0x83
    SENSOR_3MP_2 = 0x84
    
    ## Camera effect control
    
    # Set Colour Effect
    CAM_REG_COLOR_EFFECT_CONTROL = 0x27
    
    SPECIAL_NORMAL = 0x00
    SPECIAL_COOL = 1
    SPECIAL_WARM = 2
    SPECIAL_BW = 0x04
    SPECIAL_YELLOWING = 4
    SPECIAL_REVERSE = 5
    SPECIAL_GREENISH = 6
    SPECIAL_LIGHT_YELLOW = 9 # 3MP Only


    # Set Brightness
    CAM_REG_BRIGHTNESS_CONTROL = 0X22

    BRIGHTNESS_MINUS_4 = 8
    BRIGHTNESS_MINUS_3 = 6
    BRIGHTNESS_MINUS_2 = 4
    BRIGHTNESS_MINUS_1 = 2
    BRIGHTNESS_DEFAULT = 0
    BRIGHTNESS_PLUS_1 = 1
    BRIGHTNESS_PLUS_2 = 3
    BRIGHTNESS_PLUS_3 = 5
    BRIGHTNESS_PLUS_4 = 7


    # Set Contrast
    CAM_REG_CONTRAST_CONTROL = 0X23

    CONTRAST_MINUS_3 = 6
    CONTRAST_MINUS_2 = 4
    CONTRAST_MINUS_1 = 2
    CONTRAST_DEFAULT = 0
    CONTRAST_PLUS_1 = 1
    CONTRAST_PLUS_2 = 3
    CONTRAST_PLUS_3 = 5


    # Set Saturation
    CAM_REG_SATURATION_CONTROL = 0X24

    SATURATION_MINUS_3 = 6
    SATURATION_MINUS_2 = 4
    SATURATION_MINUS_1 = 2
    SATURATION_DEFAULT = 0
    SATURATION_PLUS_1 = 1
    SATURATION_PLUS_2 = 3
    SATURATION_PLUS_3 = 5


    # Set Exposure Value
    CAM_REG_EXPOSURE_CONTROL = 0X25

    EXPOSURE_MINUS_3 = 6
    EXPOSURE_MINUS_2 = 4
    EXPOSURE_MINUS_1 = 2
    EXPOSURE_DEFAULT = 0
    EXPOSURE_PLUS_1 = 1
    EXPOSURE_PLUS_2 = 3
    EXPOSURE_PLUS_3 = 5
    
    
    # Set Whitebalance
    CAM_REG_WB_MODE_CONTROL = 0X26
    
    WB_MODE_AUTO = 0
    WB_MODE_SUNNY = 1
    WB_MODE_OFFICE = 2
    WB_MODE_CLOUDY = 3
    WB_MODE_HOME = 4

    # Set Sharpness
    CAM_REG_SHARPNESS_CONTROL = 0X28 #3MP only
    
    SHARPNESS_NORMAL = 0
    SHARPNESS_1 = 1
    SHARPNESS_2 = 2
    SHARPNESS_3 = 3
    SHARPNESS_4 = 4
    SHARPNESS_5 = 5
    SHARPNESS_6 = 6
    SHARPNESS_7 = 7
    SHARPNESS_8 = 8
    
    # Set Autofocus
    CAM_REG_AUTO_FOCUS_CONTROL = 0X29 #5MP only

    # Set Image quality
    CAM_REG_IMAGE_QUALITY = 0x2A
    
    IMAGE_QUALITY_HIGH = 0
    IMAGE_QUALITY_MEDI = 1
    IMAGE_QUALITY_LOW = 2
    
    # Manual gain, and exposure are explored in the datasheet - https://www.arducam.com/downloads/datasheet/Arducam_MEGA_SPI_Camera_Application_Note.pdf

    # Device addressing
    CAM_REG_DEBUG_DEVICE_ADDRESS = 0x0A
    deviceAddress = 0x78
    
    # For Waiting
    CAM_REG_SENSOR_STATE = 0x44
    CAM_REG_SENSOR_STATE_IDLE = 0x01
    
    # Setup for capturing photos
    CAM_REG_FORMAT = 0x20
    
    CAM_IMAGE_PIX_FMT_JPG = 0x01
    CAM_IMAGE_PIX_FMT_RGB565 = 0x02
    CAM_IMAGE_PIX_FMT_YUV = 0x03
    
    # Resolution settings
    CAM_REG_CAPTURE_RESOLUTION = 0x21

    # Some resolutions are not available - refer to datasheet https://www.arducam.com/downloads/datasheet/Arducam_MEGA_SPI_Camera_Application_Note.pdf
#     RESOLUTION_160X120 = 0X00
    RESOLUTION_320X240 = 0X01
    RESOLUTION_640X480 = 0X02
#     RESOLUTION_800X600 = 0X03
    RESOLUTION_1280X720 = 0X04
#     RESOLUTION_1280X960 = 0X05
    RESOLUTION_1600X1200 = 0X06
    RESOLUTION_1920X1080 = 0X07
    RESOLUTION_2048X1536 = 0X08 # 3MP only
    RESOLUTION_2592X1944 = 0X09 # 5MP only
    RESOLUTION_96X96 = 0X0a
    RESOLUTION_128X128 = 0X0b
    RESOLUTION_320X320 = 0X0c
    
    valid_3mp_resolutions = {
        '320x240': RESOLUTION_320X240, 
        '640x480': RESOLUTION_640X480, 
        '1280x720': RESOLUTION_1280X720, 
        '1600x1200': RESOLUTION_1600X1200,
        '1920x1080': RESOLUTION_1920X1080,
        '2048x1536': RESOLUTION_2048X1536,
        '96X96': RESOLUTION_96X96,
        '128X128': RESOLUTION_128X128,
        '320X320': RESOLUTION_320X320
    }

    valid_5mp_resolutions = {
        '320x240': RESOLUTION_320X240, 
        '640x480': RESOLUTION_640X480, 
        '1280x720': RESOLUTION_1280X720, 
        '1600x1200': RESOLUTION_1600X1200,
        '1920x1080': RESOLUTION_1920X1080,
        '2592x1944': RESOLUTION_2592X1944,
        '96X96': RESOLUTION_96X96,
        '128X128': RESOLUTION_128X128,
        '320X320': RESOLUTION_320X320
    }

    # FIFO and State setting registers
    ARDUCHIP_FIFO = 0x04
    FIFO_CLEAR_ID_MASK = 0x01
    FIFO_START_MASK = 0x02
    
    ARDUCHIP_TRIG = 0x44
    CAP_DONE_MASK = 0x04
    
    FIFO_SIZE1 = 0x45
    FIFO_SIZE2 = 0x46
    FIFO_SIZE3 = 0x47
    
    SINGLE_FIFO_READ = 0x3D
    BURST_FIFO_READ = 0X3C
    
    # Size of image_buffer (Burst reading)
    BUFFER_MAX_LENGTH = 255
    
    # For 5MP startup routine
    WHITE_BALANCE_WAIT_TIME_MS = 500


# User callable functions
## Main functions
## Setting functions
# Internal functions
## High level internal functions
## Low level

##################### Callable FUNCTIONS #####################

########### CORE PHOTO FUNCTIONS ###########
    def __init__(self, spi_bus, cs, skip_sleep=False, debug_information=False):
        self.cs = cs
        self.spi_bus = spi_bus

        self._write_reg(self.CAM_REG_SENSOR_RESET, self.CAM_SENSOR_RESET_ENABLE) # Reset camera
        self._wait_idle()
        self._get_sensor_config() # Get camera sensor information
        self._wait_idle()
        self._write_reg(self.CAM_REG_DEBUG_DEVICE_ADDRESS, self.deviceAddress)
        self._wait_idle()

        self.run_start_up_config = True

        # Set default format and resolution
        self.current_pixel_format = self.CAM_IMAGE_PIX_FMT_JPG
        self.old_pixel_format = self.current_pixel_format
        
        self.current_resolution_setting = self.RESOLUTION_640X480 # ArduCam driver defines this as mode
        self.old_resolution = self.current_resolution_setting
        
        
        self.set_filter(self.SPECIAL_NORMAL)
        
        self.received_length = 0
        self.total_length = 0
        
        # Burst setup
        self.first_burst_run = False
        self.image_buffer = bytearray(self.BUFFER_MAX_LENGTH)
        self.valid_image_buffer = 0
        
        
        # Tracks the AWB warmup time
        self.start_time = utime.ticks_ms()
        if debug_information:
            print('Camera version =', self.camera_idx)
        if self.camera_idx == '3MP':
            self.startup_routine_3MP()
        
        if self.camera_idx == '5MP' and skip_sleep == False:
            utime.sleep_ms(self.WHITE_BALANCE_WAIT_TIME_MS)



    def startup_routine_3MP(self):
        # Leave the shutter open for some time seconds (i.e. take a few photos without saving)
        print('Running 3MP startup routine')
        
        
        sleep_ms(500)
        
        
        
#         self.capture_jpg()
#         print('picture taken')
#         sleep_ms(500)
#         print('saving picture')
#         self.saveJPG('dummy_image.jpg')
#         print('picture saved')
#         uos.remove('dummy_image.jpg')
#         print('complete')

    '''
    Issue warning if the filepath doesnt end in .jpg (Blank) and append
    Issue error if the filetype is NOT .jpg
    '''
    def capture_jpg(self):
        
        if (utime.ticks_diff(utime.ticks_ms(), self.start_time) <= self.WHITE_BALANCE_WAIT_TIME_MS) and self.camera_idx == '5MP':
            print('Please add a ', self.WHITE_BALANCE_WAIT_TIME_MS, 'ms delay to allow for white balance to run')
            
        else:
#             print('Starting capture JPG')
            # JPG, bmp ect
            # TODO: PROPERTIES TO CONFIGURE THE PIXEL FORMAT
            if (self.old_pixel_format != self.current_pixel_format) or self.run_start_up_config:
                self.old_pixel_format = self.current_pixel_format
                self._write_reg(self.CAM_REG_FORMAT, self.current_pixel_format) # Set to capture a jpg
                self._wait_idle()
#             print('old',self.old_resolution,'new',self.current_resolution_setting)
                # TODO: PROPERTIES TO CONFIGURE THE RESOLUTION
            if (self.old_resolution != self.current_resolution_setting) or self.run_start_up_config:
                self.old_resolution = self.current_resolution_setting
                self._write_reg(self.CAM_REG_CAPTURE_RESOLUTION, self.current_resolution_setting)
#                 print('setting res', self.current_resolution_setting)
                self._wait_idle()
            
            self.run_start_up_config = False
            
            # Start capturing the photo
            
            self._set_capture()
#             print('capture jpg complete')
        

    # TODO: After reading the camera data clear the FIFO and reset the camera (so that the first time read can be used)
    def saveJPG(self,filename):
        headflag = 0
        print('Saving image, please dont remove power')
#         print('rec len:', self.received_length)
        
        image_data = 0x00
        image_data_next = 0x00
        
        image_data_int = 0x00
        image_data_next_int = 0x00
        
        print(self.received_length)
        
        try:
            os.remove(filename)
        except Exception as e:
            print("Error deleting old file: ", e)
        
        
        if(self.received_length > 100000):
            machine.reset()
        
        while(self.received_length):
            
            
            
            image_data = image_data_next
            image_data_int = image_data_next_int
            
            image_data_next = self._read_byte()
            image_data_next_int = int.from_bytes(image_data_next, 1) # TODO: CHANGE TO READ n BYTES
            if headflag == 1:
                jpg_to_write.write(image_data_next)
            
            if (image_data_int == 0xff) and (image_data_next_int == 0xd8):
                # TODO: Save file to filename
#                 print('start of file')
                headflag = 1
                jpg_to_write = open(filename,'ab')
                jpg_to_write.write(image_data)
                jpg_to_write.write(image_data_next)
                
            if (image_data_int == 0xff) and (image_data_next_int == 0xd9):
#                 print('TODO: Save and close file?')
                headflag = 0
                jpg_to_write.write(image_data_next)
                jpg_to_write.close()





    def save_JPG_burst(self):
        headflag = 0
        print('Saving image, please dont remove power')

        image_data = 0x00
        image_data_next = 0x00

        image_data_int = 0x00
        image_data_next_int = 0x00

        print(self.received_length)

        while(self.received_length):
            
            
            
            self._burst_read_FIFO()
            
            start_bytes = self.image_buffer[0]
            end_bytes = self.image_buffer[self.valid_image_buffer-1]
            
        
#     def _read_byte(self):
#         self.cs.off()
#         self.spi_bus.write(bytes([self.SINGLE_FIFO_READ]))
#         data = self.spi_bus.read(1)
#         data = self.spi_bus.read(1)
#         self.cs.on()
#         self.received_length -= 1
#         return data


    def _burst_read_FIFO(self):
        #compute how many bytes to read
        burst_read_length = self.BUFFER_MAX_LENGTH # Default to max length
        if self.received_length < self.BUFFER_MAX_LENGTH:
            burst_read_length = self.received_length
        current_buffer_byte = 0
        
        self.cs.off()
        self.spi_bus.write(bytes([self.BURST_FIFO_READ]))
        
        data = self.spi_bus.read(1)
        # Throw away first byte on first read
        if self.first_burst_fifo == True:
            self.image_buffer[current_buffer_byte] = data
            current_buffer_byte += 1
            burst_read_length -= 1
            print('first burst read')
            
        
        while burst_read_length:
            
            
            
            data = self.spi_bus.read(1) # Read from camera
            self.image_buffer[current_buffer_byte] = data # write to buffer
            current_buffer_byte += 1
            burst_read_length -= 1

        self.cs.on()
        self.received_length -= burst_read_length
        self.valid_image_buffer = burst_read_length


    @property
    def resolution(self):
        return self.current_resolution_setting
    @resolution.setter
    def resolution(self, new_resolution):
        input_string_lower = new_resolution.lower()        
        if self.camera_idx == '3MP':
            if True:
                self.current_resolution_setting = self.valid_3mp_resolutions['320x240']
            else:
                raise ValueError("Invalid resolution provided for {}, please select from {}".format(self.camera_idx, list(self.valid_3mp_resolutions.keys())))

        elif self.camera_idx == '5MP':
            if input_string_lower in self.valid_5mp_resolutions:
                self.current_resolution_setting = self.valid_5mp_resolutions[input_string_lower]
            else:
                raise ValueError("Invalid resolution provided for {}, please select from {}".format(self.camera_idx, list(self.valid_5mp_resolutions.keys())))
    

    def set_pixel_format(self, new_pixel_format):
        self.current_pixel_format = new_pixel_format

########### ACCSESSORY FUNCTIONS ###########









    # TODO: Complete for other camera settings
    # Make these setters - https://github.com/CoreElectronics/CE-PiicoDev-Accelerometer-LIS3DH-MicroPython-Module/blob/abcb4337020434af010f2325b061e694b808316d/PiicoDev_LIS3DH.py#L118C1-L118C1
    
#     # Set Brightness
#     CAM_REG_BRIGHTNESS_CONTROL = 0X22
# 
#     BRIGHTNESS_MINUS_4 = 8
#     BRIGHTNESS_MINUS_3 = 6
#     BRIGHTNESS_MINUS_2 = 4
#     BRIGHTNESS_MINUS_1 = 2
#     BRIGHTNESS_DEFAULT = 0
#     BRIGHTNESS_PLUS_1 = 1
#     BRIGHTNESS_PLUS_2 = 3
#     BRIGHTNESS_PLUS_3 = 5
#     BRIGHTNESS_PLUS_4 = 7


    def set_brightness_level(self, brightness):
        self._write_reg(self.CAM_REG_BRIGHTNESS_CONTROL, brightness)
        self._wait_idle()

    def set_filter(self, effect):
        self._write_reg(self.CAM_REG_COLOR_EFFECT_CONTROL, effect)
        self._wait_idle()

#     # Set Saturation
#     CAM_REG_SATURATION_CONTROL = 0X24
# 
#     SATURATION_MINUS_3 = 6
#     SATURATION_MINUS_2 = 4
#     SATURATION_MINUS_1 = 2
#     SATURATION_DEFAULT = 0
#     SATURATION_PLUS_1 = 1
#     SATURATION_PLUS_2 = 3
#     SATURATION_PLUS_3 = 5

    def set_saturation_control(self, saturation_value):
        self._write_reg(self.CAM_REG_SATURATION_CONTROL, saturation_value)
        self._wait_idle()

#     # Set Exposure Value
#     CAM_REG_EXPOSURE_CONTROL = 0X25
# 
#     EXPOSURE_MINUS_3 = 6
#     EXPOSURE_MINUS_2 = 4
#     EXPOSURE_MINUS_1 = 2
#     EXPOSURE_DEFAULT = 0
#     EXPOSURE_PLUS_1 = 1
#     EXPOSURE_PLUS_2 = 3
#     EXPOSURE_PLUS_3 = 5


#     # Set Contrast
#     CAM_REG_CONTRAST_CONTROL = 0X23
# 
#     CONTRAST_MINUS_3 = 6
#     CONTRAST_MINUS_2 = 4
#     CONTRAST_MINUS_1 = 2
#     CONTRAST_DEFAULT = 0
#     CONTRAST_PLUS_1 = 1
#     CONTRAST_PLUS_2 = 3
#     CONTRAST_PLUS_3 = 5

    def set_contrast(self, contrast):
        self._write_reg(self.CAM_REG_CONTRAST_CONTROL, contrast)
        self._wait_idle()


    def set_white_balance(self, environment):
        register_value = self.WB_MODE_AUTO

        if environment == 'sunny':
            register_value = self.WB_MODE_SUNNY
        elif environment == 'office':
            register_value = self.WB_MODE_OFFICE
        elif environment == 'cloudy':
            register_value = self.WB_MODE_CLOUDY
        elif environment == 'home':
            register_value = self.WB_MODE_HOME
        elif self.camera_idx == '3MP':
            print('TODO UPDATE: For best results set a White Balance setting')

        self.white_balance_mode = register_value
        self._write_reg(self.CAM_REG_WB_MODE_CONTROL, register_value)
        self._wait_idle()

##################### INTERNAL FUNCTIONS - HIGH LEVEL #####################

########### CORE PHOTO FUNCTIONS ###########
    def _clear_fifo_flag(self):
        self._write_reg(self.ARDUCHIP_FIFO, self.FIFO_CLEAR_ID_MASK)

    def _start_capture(self):
        self._write_reg(self.ARDUCHIP_FIFO, self.FIFO_START_MASK)

    def _set_capture(self):
        self._clear_fifo_flag()
        self._wait_idle()
        self._start_capture()
        while (self._get_bit(self.ARDUCHIP_TRIG, self.CAP_DONE_MASK) == 0):
            
            
            
            sleep_ms(1)
        self.received_length = self._read_fifo_length()
        self.total_length = self.received_length
        self.burst_first_flag = False
    
    def _read_fifo_length(self): # TODO: CONFIRM AND SWAP TO A 3 BYTE READ
        len1 = int.from_bytes(self._read_reg(self.FIFO_SIZE1),1)
        len2 = int.from_bytes(self._read_reg(self.FIFO_SIZE2),1)
        len3 = int.from_bytes(self._read_reg(self.FIFO_SIZE3),1)
#         print(len1,len2,len3)
        return ((len3 << 16) | (len2 << 8) | len1) & 0xffffff

    def _get_sensor_config(self):
        camera_id = self._read_reg(self.CAM_REG_SENSOR_ID);
        self._wait_idle()
        if (int.from_bytes(camera_id, 1) == self.SENSOR_3MP_1) or (int.from_bytes(camera_id, 1) == self.SENSOR_3MP_2):
            self.camera_idx = '3MP'
        if (int.from_bytes(camera_id, 1) == self.SENSOR_5MP_1) or (int.from_bytes(camera_id, 1) == self.SENSOR_5MP_2):
            self.camera_idx = '5MP'


##################### INTERNAL FUNCTIONS - LOW LEVEL #####################

    def _read_buffer(self):
        print('COMPLETE')

    def _bus_write(self, addr, val):
        self.cs.off()
        self.spi_bus.write(bytes([addr]))
        self.spi_bus.write(bytes([val])) # FixMe only works with single bytes
        self.cs.on()
        sleep_ms(1) # From the Arducam Library
        return 1
    
    def _bus_read(self, addr):
        self.cs.off()
        self.spi_bus.write(bytes([addr]))
        data = self.spi_bus.read(1) # Only read second set of data
        data = self.spi_bus.read(1)
        self.cs.on()
        return data

    def _write_reg(self, addr, val):
        self._bus_write(addr | 0x80, val)

    def _read_reg(self, addr):
        data = self._bus_read(addr & 0x7F)
        return data # TODO: Check that this should return raw bytes or int (int.from_bytes(data, 1))

    def _read_byte(self):
        self.cs.off()
        self.spi_bus.write(bytes([self.SINGLE_FIFO_READ]))
        data = self.spi_bus.read(1)
        data = self.spi_bus.read(1)
        self.cs.on()
        self.received_length -= 1
        return data
    
    def _wait_idle(self):
        
        
        
        data = self._read_reg(self.CAM_REG_SENSOR_STATE)
        while ((int.from_bytes(data, 1) & 0x03) == self.CAM_REG_SENSOR_STATE_IDLE):
            
            
            
            data = self._read_reg(self.CAM_REG_SENSOR_STATE)
            
            sleep_ms(2)
            

    def _get_bit(self, addr, bit):
        data = self._read_reg(addr);
        return int.from_bytes(data, 1) & bit;


