'''
This class creates an object for each face of Yearling. 

Authors: Antony Macar, Michael Pham, Nicole Maggard
Updated July 26, 2022 
v1.1
'''

import gc
gc.collect()

from debugcolor import co
import time

import traceback

import adafruit_mcp9808     #temperature sensor
import adafruit_tca9548a    #I2C multiplexer
# import adafruit_veml7700    #light sensor

gc.collect()
#Thermoucouple ADC
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


class Face:

    def debug_print(self,statement):
        if self.debug:
            print(co("[BIG_DATA]"+statement,"teal","bold"))
            return

    def __init__(self, Add, Pos, debug_state, tca):
        self.tca=tca
        self.address = Add
        self.position = Pos
        self.debug= debug_state

        #Sensor List Contains Expected Sensors Based on Face
        self.senlist = []
        self.datalist = [] #[temp light mag accel gyro motordriver thermo]
        if Pos == "x+":
            self.senlist.append("MCP")
            self.senlist.append("VEML")
        elif Pos == "x-":
            self.senlist.append("MCP")
            self.senlist.append("VEML")
        elif Pos == "y+":
            self.senlist.append("MCP")
            self.senlist.append("VEML")
        elif Pos == "y-":
            self.senlist.append("MCP")
            self.senlist.append("VEML")
        elif Pos == "z-":
            self.senlist.append("COUPLE")
        else:
            self.debug_print("[ERROR] Please input a proper face")

        #This sensors set contains information as to whether sensors are actually working
        self.sensors = { 
            'MCP':      False,
            'VEML':     False,  
            'COUPLE':   False, 
        }

    @property
    def debug_value(self):
        return self.debug
    
    @debug_value.setter
    def debug_value(self,value):
        self.debug=value    

    # function to initialize all the sensors on that face        
    def Sensorinit(self,senlist,address):

        #Initialize Temperature Sensor
        if "MCP" in senlist:
            try:
                self.mcp = adafruit_mcp9808.MCP9808(self.tca[address],address=27)
                self.sensors['MCP'] = True
                self.debug_print('[ACTIVE][Temperature Sensor]')
            except Exception as e:
                self.debug_print('[ERROR][Temperature Sensor]' + ''.join(traceback.format_exception(e)))

        #Initialize Light Sensor
#         if "VEML" in senlist:
#             try:
#                 self.veml = adafruit_veml7700.VEML7700(self.tca[address])
#                 # self.light1.enable_color =True
#                 # self.light1.enable_proximity = True
#                 self.sensors['VEML'] = True
#                 self.debug_print('[ACTIVE][Light Sensor]')
#             except Exception as e: 
#                 self.debug_print('[ERROR][Light Sensor]' + ''.join(traceback.format_exception(e)))

                
        #Initialize Thermocouple
        if "COUPLE" in senlist:
            try:
                self.couple = ADS.ADS1015(self.tca[address], address=0x48)
                self.sensors['COUPLE'] = True
                self.debug_print('[ACTIVE][Thermocouple]')
            except Exception as e:
                self.debug_print('[ERROR][Thermocouple]' + ''.join(traceback.format_exception(e)))

        self.debug_print('Initialization Complete')

    #Meta Info Getters
    @property #Gives what sensors should be present
    def senlist_what(self): 
        return self.senlist 
    
    @property #Givens what sensors are actually present 
    def active_sensors(self): 
        return self.sensors

    #Sensor Data Getters 

    @property #Temperature Data Getter
    def temperature(self): 
        if self.sensors['MCP']:
            return self.mcp.temperature
        else:
            self.debug_print('[WARNING]Temperature sensor not initialized')

#     @property #Light Sensor Color Data Getter
#     def lux_data(self): 
#         if self.sensors['VEML']:
#             return self.veml.lux
#         else:
#             self.debug_print('[WARNING]Light sensor not initialized')




#     @property #driver sequence Getter 
#     def drive(self): 
#         if self.sensors['DRV']:
#             return self.drv.sequence[0]
#         else:
#             self.debug_print('[WARNING]Motor driver not initialized')



    @property #Thermocouple Getter 
    def couple_data(self): 
        if self.sensors['COUPLE']:
            chan = AnalogIn(self.couple, ADS.P1)
            
            tip = (chan.voltage-1.25)/0.005
            return tip
        else:
            self.debug_print('[WARNING]Thermocouple not initialized')  



    #Function to test all sensors that should be on each face. 
    #Function takes number of tests "num" and polling rate in hz "rate"
    def test_all(self, num, rate): 
        self.datalist = []
        self.debug_print('Expected Sensors: ' + str(self.senlist_what))
        self.debug_print('Initialized Sensors: ' + str(self.active_sensors))
        self.debug_print('Initializing Test')

        for i in range(num): 
            self.debug_print('Test Number: {}/{}'.format(i+1, num))

            # Test Temperature Sensor
            if ("MCP" in self.senlist) and (self.sensors.get("MCP")):
                try:
                    temp = self.temperature
                    self.debug_print(f'[DEBUG] Temperature Data: {temp}')
                    self.datalist.append(temp)
                except Exception as e:
                    self.debug_print('[ERROR] Temperature Sensor Read Failed: ' + ''.join(traceback.format_exception(e)))
                    self.datalist.append(None)
            elif self.position == "z-":
                pass
            else:
                self.debug_print('[ERROR] Temperature Sensor Missing')
                self.datalist.append(None)

#             # Test Light Sensor
#             if ("VEML" in self.senlist) and (self.sensors.get('VEML')): 
#                 try:
#                     lux = self.lux_data
#                     self.debug_print(f'[DEBUG] Light Sensor Data: {lux}')
#                     self.datalist.append(lux)
#                 except Exception as e:
#                     self.debug_print('[ERROR] Light Sensor Read Failed: ' + ''.join(traceback.format_exception(e)))
#                     self.datalist.append(None)

            # Test Thermocouple
            if ("COUPLE" in self.senlist) and (self.sensors.get('COUPLE')): 
                try:
                    self.debug_print('Thermocouple')
                    self.debug_print('Battery Thermocouple: {}C'.format(self.couple_data)) #Unformatted
                    self.datalist.append(self.couple_data)
                except Exception as e:
                    self.debug_print('[ERROR][Thermocouple]' + ''.join(traceback.format_exception(e)))
                self.debug_print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~') 
            elif self.position == "z-":
                self.debug_print('[ERROR]Thermocouple Failure')
                self.datalist.append(None)
            else:
                pass

            self.debug_print('=======================================')
            #time.sleep(rate) #Remove later for performance boost! 
        return self.datalist
    def __del__(self):
        self.debug_print("Object Destroyed!")

class AllFaces:
    def debug_print(self,statement):
        if self.debug:
            print(co("[BIG_DATA]"+statement,"teal","bold")) 
    def __init__(self,debug,tca):
        self.tca=tca
        # Create the TCA9548A object and give it the I2C1 bus
        self.debug = debug
        self.debug_print("Creating Face Objects...")
        self.BigFaceList=[]
        self.Face4 = Face(4,"z-",self.debug,self.tca)
        self.Face3 = Face(3,"x-",self.debug,self.tca)
        self.Face2 = Face(2,"x+",self.debug,self.tca)
        self.Face1 = Face(1,"y-",self.debug,self.tca)
        self.Face0 = Face(0,"y+",self.debug,self.tca)
        self.debug_print("Done!")


        #Initialize All Faces 
        try:
            self.Face0.Sensorinit(self.Face0.senlist,self.Face0.address)
        except Exception as e:
            self.debug_print('[ERROR][Face0 Initialization]' + ''.join(traceback.format_exception(e)))

        try:
            self.Face1.Sensorinit(self.Face1.senlist,self.Face1.address)
        except Exception as e:
            self.debug_print('[ERROR][Face1 Initialization]' + ''.join(traceback.format_exception(e)))
        
        try:
            self.Face2.Sensorinit(self.Face2.senlist,self.Face2.address)
        except Exception as e:
            self.debug_print('[ERROR][Face2 Initialization]' + ''.join(traceback.format_exception(e)))

        try:
            self.Face3.Sensorinit(self.Face3.senlist,self.Face3.address)
        except Exception as e:
            self.debug_print('[ERROR][Face3 Initialization]' + ''.join(traceback.format_exception(e)))
        
        try:
            self.Face4.Sensorinit(self.Face4.senlist,self.Face4.address)
        except Exception as e:
            self.debug_print('[ERROR][Face4 Initialization]' + ''.join(traceback.format_exception(e)))
        
        self.debug_print("Faces Initialized")


#     @property #driver sequence Getter 
#     def sequence(self): 
#         return self.Face0.drive,self.Face2.drive,self.Face4.drive
# 
#     @sequence.setter #setter
#     def sequence(self, seq): 
#         self.Face0.drive=seq
#         self.Face2.drive=seq
#         self.Face4.drive=seq



    #Function that polls all of the sensors on all of the faces one time and prints the results. 
    def Face_Test_All(self):
        try:
            self.BigFaceList=[]
            self.debug_print("Creating Face List")
            self.BigFaceList.append(self.Face0.test_all(1,.1))
            self.BigFaceList.append(self.Face1.test_all(1,.1))
            self.BigFaceList.append(self.Face2.test_all(1,.1))
            self.BigFaceList.append(self.Face3.test_all(1,.1))
            self.BigFaceList.append(self.Face4.test_all(1,.1))

            for face in self.BigFaceList:
                self.debug_print(str(face))

        except Exception as e:
            self.debug_print('All Face test error:' + ''.join(traceback.format_exception(e)))
        return self.BigFaceList
    
    
    def Get_Thermo_Data(self):
        f1t=self.Face4.couple_data
        return f1t
        
    def __del__(self):
        del self.Face0
        del self.Face1
        del self.Face2
        del self.Face3
        del self.Face4
        self.debug_print("Object Destroyed!")
  
