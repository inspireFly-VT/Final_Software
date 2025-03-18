from machine import UART, Pin
from time import time
import time



class Easy_comms:
    # Initialize with UART configuration
    def __init__(self, uart_id: int, baud_rate: int = None):
        
        self.uart_id = uart_id
        if baud_rate: 
            self.baud_rate = baud_rate
        # Set the baud rate for UART
        self.uart = UART(self.uart_id, self.baud_rate)
        # Initialize the UART serial port
        self.uart.init() 
    
    # Send bytes across UART
    def send_bytes(self, data: bytes):
        
        print("Sending bytes...")
        self.uart.write(data)
    
    # Calculate CRC16 for data integrity
    def calculate_crc16(self, data: bytes) -> bytes:
        
        crc = 0x1D0F  # CCITT-False is 0xFFFF
        poly = 0x1021  # CRC-CCITT polynomial
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ poly
                else:
                    crc <<= 1
                crc &= 0xFFFF  # Limit to 16 bits
        return crc

    # Send string messages across UART
    def overhead_send(self, msg: bytes):
        
        print(f'Sending Message: {msg}...')
        msg = msg + '\n'
        self.uart.write(bytes(msg, 'utf-8'))
    
    
    def default_overhead_read(self) -> str:
        
        timer = 0
        
        message = ""
        
        logged_time = time.time()
        
        while True:
            
            
            if (time.time() - logged_time) > 10:
                print("Been in overhead read for another 10 seconds!")
                logged_time = time.time()
            
            if self.uart.any() > 0:
                
                try:
                    raw_data = self.uart.read()
                    if raw_data:  # Ensure data is not None
                        decoded_data = raw_data.decode('utf-8')  # Decode safely
                        print(f"Decoded Data: {decoded_data}")
                        message += decoded_data
                    else:
                        continue  # Skip if read() returns None
                    
                    if '\n' in message:  # Check if message is complete
                        message = message.split('\n', 1)[0]  # Extract only the first message
                        print(f"Received message: {message}")
                        return message
                except UnicodeError:
                    print("Unicode error encountered. Skipping invalid characters.")
                    continue  # Skip iteration if decoding fails

            time.sleep(0.05)  # Prevents CPU overuse in an infinite loop
            timer += 1
    
    
    
    # Read string messages from UART
    def overhead_read(self) -> str:
        
        timer = 0
        message = ""   
        logged_time = time.time()
        
        while True:
            
            if (time.time() - logged_time) > 20:
                print("Been in overhead read for 20 seconds! Breaking out")
                return "timed out"
                break
                
            
            if self.uart.any() > 0:
                
                try:
                    raw_data = self.uart.read()
                    
                    if raw_data:  # Ensure data is not None
                        decoded_data = raw_data.decode('utf-8')  # Decode safely
                        print(f"Decoded Data: {decoded_data}")
                        message += decoded_data
                    else:
                        continue  # Skip if read() returns None
                    
                    if '\n' in message:  # Check if message is complete
                        message = message.split('\n', 1)[0]  # Extract only the first message
                        print(f"Received message: {message}")
                        return message
                except UnicodeError:
                    print("Unicode error encountered. Skipping invalid characters.")
                    continue  # Skip iteration if decoding fails

            time.sleep(0.05)  # Prevents CPU overuse in an infinite loop
            timer += 1
            
            
            
#             if timer > 100:
#                 print("Overhead Read Timer Timed Out! Exiting")
#                 return "time out"
#                 break


    # Wait for acknowledgment from the FCB
    def wait_for_acknowledgment(self, timeout=30):
        
        """
        Waits for an acknowledgment from the FCB.
        If acknowledgment is received, it proceeds with the data transfer.
        If timeout is reached without receiving acknowledgment, it returns False.
        
        :param timeout: Time in seconds to wait before giving up (default is 30 seconds).
        :return: True if acknowledgment is received, False if timeout is reached.
        """
        start_time = time.time()
        
        while True:
            
            print('Waiting for acknowledgment')
            acknowledgment = self.overhead_read()
            
            if acknowledgment == 'acknowledge':
                print('Acknowledgment received, proceeding with data transfer...')
                return True
            
            if time.time() - start_time > timeout:
                print("Timeout reached. No acknowledgment received.")
                return False
            
            time.sleep(1)  # Wait for a while before trying again
            
