import time
import traceback
import gc

class EasyComms:
    
    # Initialize
    timeout = 5  # Timeout in seconds
    
#     # Backend setup
    def __init__(self, cubesat, uart_tx_pin, uart_rx_pin, baud_rate=None):
#         if baud_rate:
#             self.baud_rate = baud_rate
#         # Set up UART interface
          self.uart = cubesat.uart
          
          
    
    # Send bytes across
    def send_bytes(self, data: bytes):
        print("Sending bytes...")
        self.uart.write(data)  # write data to port
    
    # Hello!
    def start(self):
        message = "Ahoy!\n"
        print(message)
    
    # CRC Bit Check, returns 2 bytes of integers
    def calculate_crc16(self, data: bytes) -> int:
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
    

    def read_chunks(self, lowerchunk, upperchunk):

#         Generator that yields photo data chunks without accumulating them in memory.
#         Expects lowerchunk and upperchunk as strings representing integer values.

        
        error_count = 0
        print("Error count set to 0!")
        
        chunksize = 70
        for i in range(int(lowerchunk), int(upperchunk) + 1):
            gc.collect()
            time.sleep(1)  # Allow time for bytes to arrive
            if self.uart.in_waiting > 0:
                data = self.uart.read(chunksize)
                if data is None or len(data) < chunksize:
                    
                    print("No or incomplete data was received, error count: ", error_count)
                    error_count += 1
                    # If no or incomplete data is received, skip this chunk.
                    continue

                # Extract CRC and chunk number from the incoming data.
                crctagbb = data[-2:]              # Last 2 bytes: received CRC tag
                # chunknum = data[:2]              # First 2 bytes: chunk number (unused here)

                crctagb = int.from_bytes(crctagbb, 'little')
                stripped_data = data[:-2]         # Remove the CRC tag.
                crctaga = self.calculate_crc16(stripped_data)
                # Remove overhead (first 2 bytes) to isolate the photo data.
                photo_bytes = stripped_data[2:]
                
                if crctaga == crctagb:
                    self.overhead_send("A has received chunk with no error!")
                    error_count = 0
                    yield photo_bytes
                else:
                    # If CRC check fails, notify the sender.
                    self.overhead_send("Chunk has an error. Error count: ", error_count)
                    error_count += 1
                    # Optionally, you could retry reading this chunk instead of just skipping.
                    continue
            else:
                error_count += 1
                print("Uart not in waiting. Error count: ", error_count)
            

            print(f"[DEBUG] Processed chunk {i}")
            print("Error count: ", error_count)
            
            if error_count > 20:
                print("Too many errors! Breaking out:")
                break
        
        
        
        
    
    # Send strings across the port
    def overhead_send(self, msg: str):
        print(f'Sending Message: {msg}...')
        msg = msg + '\n'
        self.uart.write(bytes(msg, 'utf-8'))
    
    # Read the strings sent across
    def overhead_read(self) -> str:
        new_line = False
        message = ""
        
        logged_time = time.time()

        try:
            while not new_line:
                if self.uart.in_waiting > 0:
                    message += self.uart.read(1).decode('utf-8')
                    if '\n' in message:
                        new_line = True
                        message = message.strip('\n')
                        print("Easy comms received: ", message)
                        return message
              
                if (time.time() - logged_time) > 5:
                    print("Been in overhead read for another 5 seconds!")
                    logged_time = time.time()
        except Exception as e:
            print("Error in overhead read: " + ''.join(traceback.format_exception(e)))
    
        return None
