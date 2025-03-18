import time

from machine import I2C, Pin, SPI

ADDRESS = 0x33
TEST_INITIAL_CONDITION = 0x440000B4
TEST = True
TEST_TERMINAL = False
IS_SETUP = False

read_states = {
    "D4": False,
    "D3": False,
    "D2": False,
    "D1": False,
    "-": False,
    "M": False,
    "S2": False,
    "S1": False,
    "A4": False,
    "A3": False,
    "A2": False,
    "A1": False,
    "B4": False,
    "B3": False,
    "B2": False,
    "B1": False,
    "Time elapsed": 0,
    "SW 4.1": False,
    "SW 4": False,
    "SW 3.1": False,
    "SW 3": False,
    "SW 2.1": False,
    "SW 2": False,
    "SW 1.1": False,
    "SW 1": False
}

write_states = {
    "S2": False,
    "S1": False,
    "Ant4": False,
    "Ant3": False,
    "Ant2": False,
    "Ant1": False
}


# function to store read values to defined dictionary
# bytes [bytearray] as argument
# return read & stored values as string unless error, which is passed to generic error handler
def store(bytes):
    try:
        ret = ""
        index = 0 # index to iterate bytearray
        bit_pos = 7
        for key, value in read_states.items(): #iterate through dict
            if (index == 2): # special case for third byte that is entirely treated as 8-bit int
                value = int(bytes[index])
                #print(key + ": " + str(value) + " seconds")
                index += 1
                continue
            value = ((bytes[index] >> bit_pos) & 1) == 1 # perform AND to get bit corresponding to preestablished value
            #print(str(key) + ": " + str(value))
            #print((bytes[index]>>bit_pos) %2)
            if (bit_pos > 0):
                # bit_pos = int(bit_pos/2) # ensure bit_pos remains an int
                bit_pos -= 1
            else:
                index+=1
                bit_pos = 7
            ret += str(key) + ": " + str(value) + "\n"
        return bytearray([0x0,0x0,0x0,0x0])
    except Exception as e:
        return error(e, store.__name__)



# generic error handler function
# takes error [Exception] & function name [str] as arguments
# returns error status code of bytearray 0xffffffff
def error(error, func_name):
    try:
        print("Error occured at " + func_name)
        print(error)
        return bytearray([0xff,0xff,0xff,0xff])
    except Exception as e:
        return error(e, error.__name__)

# wrapper function of readfrom_into from busio.I2C
# takes i2c device [busio.i2c] & bytelength to read [int] as arguments
# returns buffer of readlen read or 0xffffffff if error occured

def read(i2c, readlen):
    global IS_SETUP
    buffer = bytearray(readlen)
    try:
        if not IS_SETUP:
            raise Exception("I2C device is not set up\nExiting...")
        buffer = i2c.readfrom(ADDRESS, readlen)
        store(buffer)
        return buffer
    except Exception as e:
        return error(e, "read")



# def read(i2c_arg, readlen):
#     global IS_SETUP
#     buffer = bytearray(readlen)
#     try:
#         if (not IS_SETUP):
#             raise Exception("I2C device is not set up\nExiting...")
#         if (not TEST_TERMINAL):
#             #i2c_arg.readfrom_into(ADDRESS, buffer, 0, readlen) # invoke read
#             
#             if(True):
#                 #i2c_arg.readfrom_into(ADDRESS, buffer)
#                 time.sleep(0.1)
#                 i2c_arg.readfrom_into(0x33, buffer)
#             else:
#                 print("Couldn't lock in read")
#         else:
#             buffer = bytearray([0x01,0x02,0x03,0x04])
#         #print("read " + str(readlen) + " bytes\n" + buffer.hex())
#         store(buffer)
#         return buffer
#     except Exception as e:
#         return error(e, read.__name__)

#  wrapper function of writeto from busio.I2C
# takes i2c device [busio.i2c] & command to write [bytearray] as argments
# returns status code or 0xffffffff if error occured


def write(i2c, cmd):
    print("Running Write with command:", cmd)
    try:
        if not IS_SETUP:
            raise Exception("I2C device is not set up\nExiting...")
        if not isinstance(cmd, bytearray):
            raise Exception("Command argument is of invalid type; should be bytearray")
        i2c.writeto(ADDRESS, cmd)
        print("Sent command")
        return bytearray([0x0, 0x0, 0x0, 0x0])
    except Exception as e:
        return error(e, "write")




# def write(i2c_arg, cmd):
#     
#     print("Running Write with command:" + str(cmd))
#     
#     try:
#         if (not IS_SETUP): # check if setup has been done successfully
#             raise Exception("I2C device is not set up\nExiting...")
#         if (type(cmd) != bytearray): # check if cmd is of correct datatype
#             raise Exception("command argument is of invalid type " + type(cmd) + "; should be of bytearray")
#         if (not TEST_TERMINAL):
# #             if(i2c_arg.try_lock()):
# #                 i2c_arg.writeto(ADDRESS, cmd, 0, len(cmd)) # invoke write
# #             else:
# #                 print("Couldn't lock")
# 
#             #i2c_arg.writeto(ADDRESS, cmd, 0, len(cmd)) # invoke write
#             time.sleep(1)
#             i2c_arg.writeto(ADDRESS, cmd)
#             
#         print("Sent command")
#         return bytearray([0x0,0x0,0x0,0x0])
#     except Exception as e:
#         return error(e, write.__name__)

# function to call read repeatedly over set time
# i2c_arg is the I2C device [busio.I2C] readlen is length of bytes to read per call [int], interval is time in seconds between calls [int], & duration is total time the function will be active in seconds [int]
def const_read(i2c_arg, readlen, interval, duration):
    try:
        counter = 0
        while (counter <= duration):
            print(read(i2c_arg, readlen)) # call read
            time.sleep(interval) # start wait
            counter+=interval # update time elspased
        print(const_read.__name__ + " ran for " + str(duration) + " seconds\n" + read.__name__ + " of length " + str(readlen) + " was called " + str(int(counter/interval)) 
            + " times with " + str(interval) +  "\nExiting " + const_read.__name__ + "...")
        return bytearray([0x0,0x0,0x0,0x0])
    except Exception as e:
        return error(e, const_read.__name__)



def setup():
    try:
        global IS_SETUP
        print(f"TEST MODE: {TEST}")
        print(f"TEST VIA TERMINAL: {TEST_TERMINAL}")
        i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=400000)
        
        
        print("Getting a handle on slave at GP9 as SCL & GP8 as SDA...")
        print("Found addresses:", i2c.scan())
        
        if len(i2c.scan()) != 1:
            raise Exception("CHECK WIRING")

        
        
        IS_SETUP = True
        return 0, i2c
    
    except Exception as e:
        error(e, "setup")
        return -1, None




# def setup():
#     try:
#         global IS_SETUP
#         print("TEST MODE: " + str(TEST))
#         print("TEST VIA TERMINAL: " + str(TEST_TERMINAL))
#         i2c = "DUMMY"
#         if (not TEST_TERMINAL): # execute if testing with device
#             print(TEST_TERMINAL)
# 
#             # initialize I2C with antenna slave
#             print("Getting a handle on slave at GP9 as SCL & GP8 as SDA...")
#             
#             # I think scl is pin 12 and sda is pin 11
#             i2c = I2C(0, scl = Pin(5), sda = Pin(4), freq=400*(10**3))  # GP9 = SCL, GP8 = SDA
#             
# #             if i2c.try_lock():
# #                 print("Succesfully locked")
# #             else:
# #                 print("Couldn't lock")
#                       
#             print("Following addresses found: " + '\n'.join(map(str, i2c.scan())))
#                      
#             
#             
#             if (i2c.scan()):
#                 print("Found UHF Antenna Type III at " + str(i2c.scan()))
#                 
# #             while (i2c.try_lock() == False):
# #                 print("Failed to grab I2C lock")
# #                 time.sleep(0.1)
# #             print("Grabbed I2C lock")
#             
#             # If test mode is active
#             
#             IS_SETUP = True
#             
#             if (TEST):
#                 print("---------------\nTEST MODE IS ACTIVE\n---------------")
#                 test_buffer = read(i2c, 4)
#                 if (test_buffer == bytearray([0xff,0xff,0xff,0xff])):
#                     # Fail test
#                     print("Cannot verify testing mode is active\nAborting...")
#                     return -1, None
#                 else:
#                     print("Testing mode status verified")
#         print("Setting IS_SETUP to True")
#         
#         #i2c.unlock()
#         
#         return 0, i2c
#     except Exception as e: #If error occured, print error & return error status code
#         error(e, setup.__name__)
#         return -1, None

def exec_alg1_for_all(i2c_arg):
    write(i2c_arg, bytearray([0x1f]))
    
def exec_alg2_for_all(i2c_arg):
    write(i2c_arg, bytearray([0x2f]))

def exec_alg2_for_ant1(i2c_arg):
    write(i2c_arg, bytearray([0x21]))

def exec_alg1_for_ant2_n_3(i2c_arg):
    write(i2c_arg, bytearray([0x16]))

def clear(i2c_arg):
    write(i2c_arg, bytearray([0x00]))


def deploy_antennas():
    #If it return 1 the antennas where deployed succesfully
    #else it will return 0
    TEST = True
    status, i2c = setup()
    if (status == -1):
        print("Could not get a handle on slave\nExiting...")
        return -1
    print("Successfully got hold of slave ")
    
    print(read(i2c, 4))
    
    print("----------\ntesting write\n----------")
    write(i2c, bytearray([0x1F]))
    
    print("testing read\n--------------")
    read(i2c, 4)
    
    print("----------\nCHECKING IF ANY ANTENNA IS DEPLOYED\n----------")
    undeployed_antennas = []
    data = read(i2c, 4)
    
    print(data)
    
    last_byte = data[3]  # Extract the last byte
    time_value = data[2]  # Use the third byte as time
    arms = [(last_byte >> (i * 2)) & 0b11 for i in range(4)]
    arm_states = ['1' if arm == 0b11 else '0' for arm in arms]
    for i in range(4):
        if int(arm_states[i]) == 1:
            print("Antenna",str(i+1),"already deployed")
        else:
            undeployed_antennas.append(i)
            
    after_undeployed_antennas = undeployed_antennas.copy() #Cannot work on the in loop, so created copy
    
    
    print("----------\nRUNNING ALGORITHM1 FOR ALL REMAINING\n----------")
    exec_alg1_for_all(i2c)
    for i in undeployed_antennas:
        print("----------\nDeploying Antenna with burn A:", str(i+1),"\n----------")
        time.sleep(5)
        data = read(i2c, 4)
        
        last_byte = data[3]  # Extract the last byte
        time_value = data[2]  # Use the third byte as time

        # Extract switch pairs and determine the state for each arm
        arms = [(last_byte >> (i * 2)) & 0b11 for i in range(4)]
        arm_states = ['1' if arm == 0b11 else '0' for arm in arms]
        current_antenna_state = int(arm_states[i])
        if current_antenna_state == 1:
            print("Deployment of antenna", int(i+1), "SUCCESSFUL")
            after_undeployed_antennas.remove(i)
        else:
            print("Deployment of antenna", int(i+1), "UNSUCCESSFUL")
            print("Trying to deploy with burn AB")
            
            for j in range(200):
                data = read(i2c, 4)
                time_value_seconds = int(bin(data[2]), 2)
                if time_value_seconds == 15:
                    print("Deployment of antenna", int(i+1), "SUCCESSFUL")
                    after_undeployed_antennas.remove(i)
                    break
                elif time_value_seconds == 0:
                    print("Deployment of antenna", int(i+1), "UNSUCCESSFUL")
                    print("Switching to next antenna")
                    break
    
        
    if len(after_undeployed_antennas) > 0:
        print("Unsuccesful Deployments :")
        print(after_undeployed_antennas)
        undeployed_antennas = after_undeployed_antennas.copy()
        print("----------\nRUNNING ALGORITHM2 FOR ALL REMAINING\n----------")
        exec_alg2_for_all(i2c)

        for i in undeployed_antennas:
            print("----------\nDeploying Antenna with burn AB:", str(i+1),"\n----------")
            for j in range(300):
                data = read(i2c, 4)
                time_value_seconds = int(bin(data[2]), 2)
                if time_value_seconds == 20:
                    print("Deployment of antenna", int(i+1), "SUCCESSFUL")
                    after_undeployed_antennas.remove(i)
                    break
                elif time_value_seconds == 0:
                    print("Deployment of antenna", int(i+1), "UNSUCCESSFUL")
                    print("Switching to next undeployed antenna")
                    break
                
    if len(after_undeployed_antennas) > 0:
        print("ALGO 2 FAILED FOR", after_undeployed_antennas)
        return 0
    else:
        return 1
        #TODO MANUALLY DEPLOY THE ANTENNAS
    
    
    
def are_antenna_deployed():
    status, i2c = setup()
    if (status == -1):
        print("Could not get a handle on slave\nExiting...")
        raise Exception("CHECK WIRING")
    print("Successfully got hold of slave ")
    
    print("----------\nCHECKING IF ANY ANTENNA IS DEPLOYED\n----------")
    undeployed_antennas = []
    data = read(i2c, 4)
    last_byte = data[3]  # Extract the last byte
    time_value = data[2]  # Use the third byte as time
    arms = [(last_byte >> (i * 2)) & 0b11 for i in range(4)]
    arm_states = ['1' if arm == 0b11 else '0' for arm in arms]
    for i in range(4):
        if int(arm_states[i]) == 1:
            print("Antenna",str(i+1),"already deployed")
        else:
            undeployed_antennas.append(i)
            
    print("Undeployed antennaswefwefwef: ", undeployed_antennas)
    if len(undeployed_antennas) == 0:
        return False
    else:
        return True



if __name__ == '__main__':
    print("WE FUCKED UP")
    time.sleep(1)
    deploy_antennas()
    
     
            
        

    # Print formatted output
    #print(f'{last_byte:08b} {time_value:08b}') #To print last two bytes in binary
    
        
    
#     print("----------\ntesting exec_alg2_for_all\n----------")
#     
#     print("----------\ntesting exec_alg2_for_ant1\n----------")
#     exec_alg2_for_ant1(i2c)
#     print("----------\ntesting exec_alg1_for_ant2_n_3\n----------")
#     exec_alg1_for_ant2_n_3(i2c)
#     print("----------\ntesting clear\n----------")
#     clear(i2c)

#     print("----------\ntesting const_read\n----------")
#     const_read(i2c, 4, 1, 5)