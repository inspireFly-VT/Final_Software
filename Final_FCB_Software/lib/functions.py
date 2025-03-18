'''
This is the class that contains all of the functions for our CubeSat. 
We pass the cubesat object to it for the definitions and then it executes 
our will.
Authors: Nicole Maggard, Michael Pham, and Rachel Sarmiento
'''
import time

import gc

import traceback

from debugcolor import co

import os
import math

class functions:

    # INSPIREFLY FUNCTIONS:
    
    def send_total_packets(self):
        
        
        file_path = self.get_file_path()
        file_info = os.stat(file_path)
            
        
        file_size = file_info[6]
        print(f"Image size: ", file_size)
        
        total_packets = math.ceil(file_size / self.bytes_per_packet)
        print("Total Packets: ", total_packets)
        
        message = b'\x30' + total_packets.to_bytes(2, 'big')
        
        self.inspireFly_send(message)



    def send_full_image(self):
        
        file_path = self.get_file_path()
        file_info = os.stat(file_path)
        
        file_size = file_info[6]
        print(f"Image size: ", file_size)
        image = open(file_path, 'rb')
        
        total_packets = math.ceil(file_size / self.bytes_per_packet)
        print("Total Packets: ", total_packets)
        
        
        current_packet_index = 0
        
        for i in range (total_packets):
            message = b'\x31'
            message = message + current_packet_index.to_bytes(2, 'big')
            
            print("Message Header: ", message)
                
            current_image_bytes = image.read(self.bytes_per_packet)
            message = message + current_image_bytes
            
            print("Final Message Before Wrapper: ", message)
            
            for i in range(1):
                self.inspireFly_send(message)
                
            current_packet_index += 1
            
            
    def send_packet(self, packet_index):
        print("Attempting to send packet: ", packet_index)
        packet_index_bytes = packet_index.to_bytes(2, 'big')
        
        message = b'\x32'
        message = message + packet_index_bytes
        

        file_path = self.get_file_path()
        file_info = os.stat(file_path)
            
        file_size = file_info[6]
        print(f"Image size: ", file_size)
        image = open(file_path, 'rb')
        
        total_packets = math.ceil(file_size / self.bytes_per_packet)
        print("Total Packets: ", total_packets)
        
        if(packet_index >= total_packets):
            print("Received an out of bounds index")
            message = b'\x32\xFF\xFF'
            self.inspireFly_send(message)
        
        image_bytes = None
        for i in range(packet_index + 1):
            image_bytes = image.read(self.bytes_per_packet)
        
        
        message = message + image_bytes
        self.inspireFly_send(message)
        
        print("Send packet index: ", packet_index)
        
        

            
            

    def debug_print(self, statement):
        if self.debug:
            print(co("[Functions]" + str(statement), 'green', 'bold'))
            return

    def __init__(self, cubesat):
        self.cubesat = cubesat
        self.debug = cubesat.debug
        self.debug_print("Initializing Functionalities")
        self.Errorcount = 0
        self.facestring = []
        self.jokes = ["Hey Its pretty cold up here, did someone forget to pay the electric bill?"]
        self.last_battery_temp = 20
        self.callsign = "KQ4LFD"
        self.state_bool = False
        self.face_data_baton = False
        self.detumble_enable_z = True
        self.detumble_enable_x = True
        self.detumble_enable_y = True
        try:
            self.cubesat.all_faces_on()
        except Exception as e:
            self.debug_print("Couldn't turn faces on: " + ''.join(traceback.format_exception(e)))
            
        self.commands = {
            b'\x10':    'noop',
            b'\x11': 'hreset',   # new
            b'\x12': 'shutdown',
            b'\x13':    'query',    # new
            #b'\x14': 'exec_cmd',   # not getting implemented
            b'\x15': 'joke_reply',
            b'\x16': 'send_SOH',
            b'\x30': 'take_and_send_pic',
            b'\x31': 'take_pic',
            b'\x32': 'send_pic',
            b'\x33': 'downlink_num_packets',
            b'\x34': 'downlink_full_image',
            b'\x35': 'downlink_packet',
            b'\x1C': 'mag_on',
            b'\x1D': 'mag_off',
            b'\x1E': 'burn_on',
            b'\x1F': 'heat_on',
        }
        
        self.image_number = 1

        self.transmit_image_running = False
        
        self.bytes_per_packet = 30
        
        self.has_picture = 0
        
        self.image_index = 0
        
        self.last_communications_time = time.time()
        
    def time_since_last_communication(self):
        return time.time() - self.last_communications_time
        
        
    def get_file_path(self):
        print("Printing out files on SD card: ")
        for file in os.listdir('/sd/'):
            print(file)
            
        if self.image_index is not 0:
            try:
                file_path = f"/sd/inspireFly_Capture_{self.image_index}.jpg"
                file_info = os.stat(file_path)
                
                return file_path
            except Exception as e:
                        debug_print(f"Couldn't find image at image index ({i}): " + ''.join(traceback.format_exception(e)))
        
        else:
            for i in range(10):
                try:
                    index = 10 - i
                    file_path = f"/sd/inspireFly_Capture_{index}.jpg"
                    file_info = os.stat(file_path)
                    
                    self.debug_print(f"Returing image at {file_path}")
                    return file_path
                except Exception as e:
                    self.debug_print(f"Couldn't find image at index {10 - i}: " + ''.join(traceback.format_exception(e)))
        
        self.debug_print("Returing image at /sd/inspireFly_Capture_0.jpg")
        return "/sd/inspireFly_Capture_0.jpg"
    

    def default_beacon(self):
        
    
        
        power_mode = self.cubesat.power_mode
        if power_mode == "critical":
            power_mode = "C"
        elif power_mode == "minimum":
            power_mode = "M"
        elif power_mode == "normal":
            power_mode = "N"
        elif power_mode == "maximum":
            power_mode = "X"
        
        battery_voltage = round(self.cubesat.battery_voltage, 2)
        
        
        message = b'\x21P'
        message += power_mode.encode("utf-8")
        
        message_second = b'V'
        message_second += str(battery_voltage).encode("utf-8")
        
        message_third = b'I'
        message_third += str(self.has_picture).encode("utf-8")
        
        message += message_second
        message += message_third
        
        #self.debug_print(beacon_message)
        
        self.inspireFly_send(message)
            
            # This send works for the line below i think the mock gs just sucks
            #self.cubesat.radio1.send(("Hello?").encode())
     
     
            
    def joke_reply(self):
        try:
            self.debug_print("Sending a joke!")
            
            
            joke = "Michael was here"
            joke = joke.encode()
            message = b'\x20' + joke
            
            self.inspireFly_send(message)
#             send_message = self.message_wrapper(message)
#             
#             for i in range(10):
#                 self.cubesat.radio1.send(send_message)
        except Exception as e:
            self.debug_print("Error in Joke Reply: " + ''.join(traceback.format_exception(e)))
        
            
    
    def listen(self, timeout):
        #This just passes the message through. Maybe add more functionality later. 
        try:
            self.debug_print("Listening")
            
            
            # Change timeout back to 10
            self.cubesat.radio1.receive_timeout=timeout
            received = self.cubesat.radio1.receive_with_ack(keep_listening=True)
        except Exception as e:
            self.debug_print("An Error has occured while listening: " + ''.join(traceback.format_exception(e)))
            received=None

        try:
            if received is not None:
                self.debug_print("Recieved Packet: "+str(received))
                self.message_handler(received)
                return True
        except Exception as e:
            self.debug_print("An Error has occured while handling command: " + ''.join(traceback.format_exception(e)))

        return False
    
    
    def message_wrapper(self, msg):
        
        try:
            header = "K4KDJ2K4KDJ1"
            header = header.encode()
            return_message = header + msg
        except Exception as e:
            self.debug_print("Error wrapping message " + ''.join(traceback.format_exception(e)))
            
        return return_message
    

            
#     def get_imu_data(self):
#         
#         self.cubesat.all_faces_on()
#         try:
#             data=[]
#             data.append(self.cubesat.IMU.acceleration)
#             data.append(self.cubesat.IMU.gyro)
#             data.append(self.cubesat.magnetometer.magnetic)
#         except Exception as e:
#             self.debug_print("Error retrieving IMU data" + ''.join(traceback.format_exception(e)))
#         
#         return data
            
        
    def battery_heater(self):
        """
        Battery Heater Function reads temperature at the end of the thermocouple and tries to 
        warm the batteries until they are roughly +4C above what the batteries should normally sit(this 
        creates a band stop in which the battery heater never turns off) The battery heater should not run
        forever, so a time based stop is implemented
        """
        try:
            try:
                import Big_Data
                a = Big_Data.AllFaces(self.debug,self.cubesat.tca)
                
                self.last_battery_temp = a.Get_Thermo_Data()
                
                battery_temperature_message = "Battery Temperature: " + str(self.last_battery_temp)
                
                self.debug_print(battery_temperature_message)
                
                
            except Exception as e:
                self.debug_print("[ERROR] couldn't get thermocouple data!" + ''.join(traceback.format_exception(e)))
                raise Exception("Thermocouple failure!")

            if self.last_battery_temp < self.cubesat.NORMAL_BATT_TEMP:
                end_time=0
                self.cubesat.heater_on()
                while self.last_battery_temp < self.cubesat.NORMAL_BATT_TEMP+4 and end_time<5:
                    time.sleep(1)
                    self.last_battery_temp = a.Get_Thermo_Data()
                    end_time+=1
                    self.debug_print(str(f"Heater has been on for {end_time} seconds and the battery temp is {self.last_battery_temp}C"))
                self.cubesat.heater_off()
                del a
                del Big_Data
                return True
            else: 
                self.debug_print("Battery is already warm enough")
                del a
                del Big_Data
                return False
        except Exception as e:
            self.cubesat.heater_off()
            self.debug_print("Error Initiating Battery Heater" + ''.join(traceback.format_exception(e)))
            del a
            del Big_Data
            return False
        finally:
            self.cubesat.heater_off()
        
    def emergency_heater_on(self):
        try:
            self.cubesat.heater_on()
            time.sleep(5)
            self.cubesat.heater_off()
        except Exception as e:
            self.debug_print("Error Running Emergency Battery Heater" + ''.join(traceback.format_exception(e)))
            
            
    
        
    def inspireFly_send(self, msg):
        
        if(self.cubesat.is_shutdown == False):
            try:
                message = self.message_wrapper(msg)
                for i in range(10):
                    self.cubesat.radio1.send(message)
                    time.sleep(0.025)
            except Exception as e:
                self.debug_print("[ERROR] couldn't send message" + ''.join(traceback.format_exception(e)))
                
        else:
            self.debug_print("Satellite is in shutdown mode!")
    
    
    
    
    # Previous cdh files stuff. Handles command processing and function calling
    # inspireFly commands
    
    
    
    def message_handler(self,msg):
    
        print("Handling a message")
        
        # inspireFly - this code should eventually be swapped out with our own command processor which will pull
        # out the important data such as the command
        
        message = bytes(msg)
        self.debug_print(f"Received: {message}")
        
        if message[0:12] == b'K4KDJ1K4KDJ2':
            self.debug_print("Receiving something from ground station. Resetting no command clock")
            self.last_communications_time = time.time()
        
        command = message[12:13]
        
        print("Received Command: ", command)
        
        
        
    #     command.append(commands)
        if(command in self.commands):
            if(command == b'\x10'):
                print("Received no-op command")
                return
            
            elif(command == b'\x11'):
                print("Received Hard Reset Command")
                reply = '\x40Resetting'
                self.inspireFly_send(reply)
                
                microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
                microcontroller.reset()
                return
            
            elif(command == b'\x12'):
                print("Received Shutdown Command")
                reply = b'\x40Shut_Down_Received'
                self.inspireFly_send(reply)
                
                self.cubesat.is_shutdown = not self.cubesat.is_shutdown
                self.debug_print(f"Satellite shutdown mode is: {self.cubesat.is_shutdown}")
                
                return
            
            elif(command == b'\x15'):
                print("Replying with a joke")
                self.joke_reply()
                return
            
            elif(command == b'\x16'):
                print("Sending SOH")
                self.state_of_health()
                return
                
            elif(command == b'\x30'):
                print("Received command x30. Telling PCB to take and send picture")
                
                reply = b'\x40Take_And_Send'
                self.inspireFly_send(reply)
                
                self.overhead_send(b'\x31')
                print("Waiting for picture taking process for 15 seconds...")
                time.sleep(15)
                
                self.overhead_send(b'\x32')
                self.pcb_comms()
                return
                
            elif(command == b'\x31'):
                print("Received command x31 (Take Picture)")
                reply = b'\x40Pic_Taking'
                self.inspireFly_send(reply)
                
                self.overhead_send(b'\x31')
                return
                
            elif(command == b'\x32'):
                print("Received command x32. (Send Image)")
                reply = b'\x40Send_Image'
                self.inspireFly_send(reply)
                
                self.overhead_send(b'\x32')
                
                gc.collect()
                self.pcb_comms()
                return
                
            elif(command == b'\x33'):
                print("Sending Total Packets")
                self.send_total_packets()
                return
            
            elif(command == b'\x34'):
                print("Sending Full Image")
                self.send_full_image()
                return
            

            elif(command == b'\x35'):
                print("Sending a packet")
                packet_index = msg[13:15]
                packet_index = int.from_bytes(packet_index, 'big')
                self.send_packet(packet_index)
                return
            
            elif(command == b'\x1E'):
                print("Received Burnwire Command. Turning on Burnwire")
                reply = b'\x40Burn_Wire'
                self.inspireFly_send(reply)
                
                self.cubesat.deploy_boomarm()
                return
            
            elif(command == b'\x1F'):
                print("Received Battery Heater Command. Turning on Battery Heater")
                reply = b'\x40Heater_On'
                self.inspireFly_send(reply)
                
                self.emergency_heater_on()
                return
                
        
        if message[0:12] == b'K4KDJ1K4KDJ2':
            self.debug_print("Receiving invalid command from the ground station. Downlinking Invalid Command")
            self.inspireFly_send('\x41Invalid_Command')

        
        print("Warning: command received did not match any.")
        print("The command received is: ", command)
        print("The full message received is: ", msg)
             
            
    #     elif(command in commands):
    #         packetIndex = (msg[7:31]) #999999 is 20 bits long, should be able to handle any packet index request
    # #         print("Transmitting image")
    # 
    # #         time.sleep(0.5)
    # #         f.pcb_comms()
    
    
    
    
    
    
    
    
    
    
    # PCB Communication Functions with Fixes:
    
    def pcb_comms(self):
        """Main PCB communications routine."""
        self.debug_print("Yapping to the PCB now - D")
        gc.collect()
        image_count = 1
        image_dir = "/sd"

        # Check that the SD card is accessible and get the list of existing files.
        existing_files = self.get_existing_files(image_dir)
        if existing_files is None:
            self.debug_print("[ERROR] SD card not detected or cannot be accessed!")
            gc.collect()
            return

        gc.collect()
        self.debug_print(f"[DEBUG] Free memory before communication start: {gc.mem_free()} bytes")

        # Initialize communication objects.
        com1, fcb_comm = self.initialize_comms()
        if com1 is None or fcb_comm is None:
            return

        # Process communication cycles.
        self.process_communication(com1, fcb_comm, image_dir, existing_files, image_count)

        # Cleanup communication objects.
        self.cleanup_comms(com1, fcb_comm)

    def get_existing_files(self, image_dir):
        #Attempt to list files on the SD card. Returns a set of filenames or None on failure.
        try:
            return set(os.listdir(image_dir))
        except OSError:
            return None

    def initialize_comms(self):
        """Initializes the communication objects."""
        gc.collect()
        try:
            # Lazy import of hardware-specific modules to defer heavy initialization.
            from board import TX, RX
            from easy_comms_circuit import EasyComms
            
            gc.collect()
            print("Memory free before importing FCB_class: ", gc.mem_free())
            from FCB_class import FCBCommunicator

            com1 = EasyComms(self.cubesat, TX, RX, baud_rate=9600)
            com1.start()
            fcb_comm = FCBCommunicator(com1)
            return com1, fcb_comm
            
        except Exception as e:
            print("[ERROR] Failed to initialize communication: " + ''.join(traceback.format_exception(e)))
            return None, None

    def process_communication(self, com1, fcb_comm, image_dir, existing_files, image_count):
        """Runs the main communication loop."""
        
        timer = 0
        while True:
            
            print("While loop in process_communication is running")
            if timer >= 20:
                self.debug_print("Fcb Communications Stalled! Exiting")
                break
            
            try:
                self.debug_print(f"[DEBUG] Free memory before cycle: {gc.mem_free()} bytes")
                # Read an overhead command (if any) – this may be used to drive logic.
                overhead_command = com1.overhead_read()

                # For our example, we assume a "chunk" command is desired.
                command = 'chunk'
                if command.lower() == 'chunk':
                    fcb_comm.send_command("chunk")
                    if fcb_comm.wait_for_acknowledgment():
                        time.sleep(1)  # Pause for stability.
                        gc.collect()
                        self.debug_print(f"[DEBUG] Free memory before data transfer: {gc.mem_free()} bytes")
                        fcb_comm.send_command("acknowledge")
                        # Get the next available image filename.
                        image_count = self.find_next_image_count(existing_files, image_count)
                        # Write the image data to SD card.
                        self.write_image(fcb_comm, image_dir, image_count)
                        
                        timer = 0
                        

                # For demonstration, we end the communication cycle after the chunk.
                command = 'end'
                if command.lower() == 'end':
                    fcb_comm.end_communication()
                    break

            except MemoryError:
                self.debug_print("[ERROR] MemoryError: Restarting communication cycle")
                gc.collect()
                continue  # Restart the cycle.
            except Exception as e:
                error_message = "[ERROR] PCB communication failed: " + str(traceback.format_exception(e))
                self.debug_print(error_message)
                break  # Break out of the loop after logging the error.
            
            timer = timer + 1
            self.debug_print("Process Communications Timer is at: ", timer)

    def find_next_image_count(self, existing_files, image_count):
        """Find the next available image filename based on the current set of files."""
        filename = f"inspireFly_Capture_{image_count}.jpg"
        while filename in existing_files:
            image_count += 1
            filename = f"inspireFly_Capture_{image_count}.jpg"
        return image_count


    def write_image(self, fcb_comm, image_dir, image_count):
        """Writes image data to the SD card by streaming chunks directly to file."""
        img_file_path = f"/sd/inspireFly_Capture_{image_count}.jpg"
        
        try:
            with open(img_file_path, "wb") as img_file:
                offset = 0
                # Get the chunk range from the PCB. The lowerchunk is fixed here as "0".
                lowerchunk = "0"
                upperchunk = fcb_comm.com.overhead_read()
                if not (lowerchunk.isdigit() and upperchunk.isdigit()):
                    self.debug_print("[ERROR] Invalid chunk range received.")
                    return
                
                # Iterate over each chunk yielded by read_chunks.
                for chunk in fcb_comm.com.read_chunks(lowerchunk, upperchunk):
                    if chunk:
                        img_file.write(chunk)
                        offset += len(chunk)
                
                self.debug_print(f"[INFO] Finished writing image to {img_file_path}. Data size: {offset} bytes")
                self.has_picture += 1
                self.picture_index += 1
                print("Has picture: ", self.has_picture)
                
                
        
        except OSError as e:
            self.debug_print(f"[ERROR] Writing to SD card failed: {str(e)}")


    def safe_send_chunk_request(self, fcb_comm, buffer, retries=3, delay=0.1):
        """
        Attempts to retrieve a data chunk from the PCB.
        If a MemoryError occurs (e.g., failing to allocate ~472 bytes), forces garbage collection
        and retries a few times before giving up.
        """
        for attempt in range(retries):
            try:
                return fcb_comm.send_chunk_request(buffer)
            except MemoryError:
                self.debug_print(f"[WARN] MemoryError during chunk request, retry {attempt+1}/{retries}.")
                gc.collect()
                time.sleep(delay)
        return None

    def cleanup_comms(self, com1, fcb_comm):
        """Closes communication objects and frees resources."""
        try:
            com1.close()
        except Exception:
            pass
        del com1, fcb_comm
        gc.collect()
        self.debug_print(f"[DEBUG] Free memory after cleanup: {gc.mem_free()} bytes")

    # ... Remaining methods of your class remain unchanged ...
    
    def overhead_send(self, msg):
        """Lightweight function to initialize UART and send overhead data."""
        try:
            from board import TX, RX
            from easy_comms_circuit import EasyComms

            com1 = EasyComms(self.cubesat, TX, RX, baud_rate=9600)
#             com1.start()
            com1.overhead_send(msg)
            self.debug_print(f"[INFO] Overhead data sent: {msg}")
        except Exception as e:
            self.debug_print(f"[ERROR] Failed to send overhead data: {str(e)}")
        finally:
            if 'com1' in locals():
                com1.close()
                
                
    def Hybernate(self, delay):
        self.debug_print(f"Hybernating for Seconds: {delay}")
        gc.collect()
        #all should be off from cubesat powermode
        self.cubesat.all_faces_off()
        self.cubesat.enable_rf.value=False
        self.cubesat.f_softboot=True
        time.sleep(delay)
        self.cubesat.all_faces_on()
        self.cubesat.enable_rf.value=True
        return True
    
    
    def state_of_health(self):
            
        # 14 bytes (including callsign)
        header = b'\x25\x00'
        
        # 3 bytes, 17
        power_mode = self.cubesat.power_mode
        if power_mode == "critical":
            power_mode = "C"
        elif power_mode == "minimum":
            power_mode = "M"
        elif power_mode == "normal":
            power_mode = "N"
        elif power_mode == "maximum":
            power_mode = "X"
        power_mode_bytes = b'PM' + power_mode.encode("utf-8")
            
        # 6 bytes, 23
        battery_voltage = round(self.cubesat.battery_voltage, 2)
        battery_voltage_bytes = b'VB' + str(battery_voltage).encode("utf-8")
        
        # 6 bytes, 29
        current_draw = round(self.cubesat.current_draw, 2)
        current_draw_bytes = b'ID' + str(current_draw).encode("utf-8")
        
        # 6 bytes, 35
        charge_current = round(self.cubesat.charge_current, 2)
        charge_current_bytes = b'IC' + str(charge_current).encode("utf-8")
        
        # 6 bytes, 41
        system_voltage = round(self.cubesat.system_voltage, 2)
        system_voltage_bytes = b'VS' + str(system_voltage).encode("utf-8")
        
        first_chunk = header + power_mode_bytes + battery_voltage_bytes + current_draw_bytes + charge_current_bytes + system_voltage_bytes
        
        self.inspireFly_send(first_chunk)
        time.sleep(0.1)
        
        
        # 14 bytes
        header = b'\x25\x01'
        
        # 5 bytes, 19
        uptime = self.cubesat.uptime
        uptime_bytes = b'UT' + uptime.to_bytes(3, 'big')
        
        # 4 bytes, 23
        boot_num = self.cubesat.c_boot
        boot_num_bytes = b'BN' + boot_num.to_bytes(2, 'big')
        
        # 7 bytes, 30
        micro_temp = round(self.cubesat.micro.cpu.temperature, 2)
        micro_temp_bytes = b'MT' + str(micro_temp).encode("utf-8")
        
        # 7 bytes, 37
        radio_temp = round(self.cubesat.radio1.former_temperature, 2)
        radio_temp_bytes = b'RT' + str(radio_temp).encode("utf-8")
        
        second_chunk = header + uptime_bytes + boot_num_bytes + micro_temp_bytes + radio_temp_bytes
        
        self.inspireFly_send(second_chunk)
        
        # 14 bytes
        header = b'\x25\x02'
        
        # 7 bytes, 21
        internal_temp = round(self.cubesat.internal_temperature, 2)
        internal_temp_bytes = b'AT' + str(internal_temp).encode("utf-8")
        
        # 7 bytes, 28
        battery_temp = round(self.last_battery_temp, 2)
        battery_temp_bytes = b'BT' + str(battery_temp).encode("utf-8")
        
        
        # 3 bytes, 31
        print("Burned: ", self.cubesat.burned)
        burned = self.cubesat.burned
        
        if burned == True:
            burned = 1
        else:
            burned = 0
        
        burned_bytes = b'AB' + str(burned).encode("utf-8")
        
        # 3 bytes, 34
        has_picture = self.has_picture
        has_picture_bytes = b'HP' + str(self.has_picture).encode("utf-8")
        
        message = header + internal_temp_bytes + battery_temp_bytes + burned_bytes + has_picture_bytes
        self.inspireFly_send(message)
        
        
    
