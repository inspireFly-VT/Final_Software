# import time
# import random
# 
# 
# 
# 
# 
# # from FCB_class import FCBCommunicator as fcb
# import microcontroller
# 
# # our 4 byte code to authorize commands
# # pass-code for DEMO PURPOSES ONLY
# #jokereply=["Your Mom","Your Mum","Your Face","not True lol","I have brought peace, freedom, justice, and security to my new empire! Your New Empire?"]
# # our 4 byte code to authorize commands
# # pass-code for DEMO PURPOSES ONLY
# password = b'\xFF\xFF' #put your own code here
# 
# 
# # com1 = EasyComms(board.TX, board.RX, baud_rate=9600)
# # fcb_comm = FCBCommunicator(com1)
# 
# # Bronco's commands
# # commands = {
# #     b'\x8eb':    'noop',
# #     b'\xd4\x9f': 'hreset',   # new
# #     b'\x12\x06': 'shutdown',
# #     b'8\x93':    'query',    # new
# #     b'\x96\xa2': 'exec_cmd',
# #     b'\xa5\xb4': 'joke_reply',
# #     b'\x56\xc4': 'FSK'
# # }
# 
# # inspireFly commands
# commands = {
#     b'\x10':    'noop',
#     b'\x11': 'hreset',   # new
#     b'\x12': 'shutdown',
#     b'\x13':    'query',    # new
#     #b'\x14': 'exec_cmd',   # not getting implemented
#     b'\x15': 'joke_reply',
#     b'\x16': 'send_SOH',
#     b'\x30': 'start_imgae_transfer',
#     b'\x31': 'take_pic',
#     b'\x32': 'send_pic',
#     b'\x33': 'downlink_pic',
#     b'\x34': 'receive_pic',
#     b'\x1C': 'mag_on',
#     b'\x1D': 'mag_off',
#     b'\x1E': 'burn_on',
#     b'\x1F': 'heat_on',
# }
# 
# transmit_image_running = False
# 
# ############### hot start helper ###############
# def hotstart_handler(cubesat,msg):
#     # try
#     try:
#         cubesat.radio1.node = cubesat.cfg['id'] # this sat's radiohead ID
#         cubesat.radio1.destination = cubesat.cfg['gs'] # target gs radiohead ID
#     except: pass
#     # check that message is for me
#     if msg[0]==cubesat.radio1.node:
#         # TODO check for optional radio config
# 
#         # manually send ACK
#         cubesat.radio1.send('!',identifier=msg[2],flags=0x80)
#         # TODO remove this delay. for testing only!
#         time.sleep(0.5)
#         message_handler(cubesat, msg)
#     else:
#         print(f'not for me? target id: {hex(msg[0])}, my id: {hex(cubesat.radio1.node)}')
# 
# ############### message handler ###############
# def message_handler(cubesat,msg):
#     
#     print("Handling a message")
#     
#     # inspireFly - this code should eventually be swapped out with our own command processor which will pull
#     # out the important data such as the command
#     
#     f = functions.functions(cubesat)
#     
#     command = bytes(msg)
#     command = command[12:13]
#     
#     print("Received Command: ", command)
#     
# #     command.append(commands)
#     if(command in commands):
#         if(command == b'\x10'):
#             print("Received no-op command")
#             return
#         
#         elif(command == b'\x11'):
#             print("Received Hard Reset Command")
#             microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
#             microcontroller.reset()
#             return
#         
#         elif(command == b'\x12'):
#             print("Received Shutdown Command")
#             cubesat.is_shutdown = True
#             return
#         
#         elif(command == b'\x15'):
#             print("Replying with a joke")
#             f.joke_reply()
#             return
#             
#         elif(command == b'\x31'):
#             print("Received command x31")
#             f.overhead_send(b'\x31')
#             return
#             
#         elif(command == b'\x32'):
#             print("Received command x32")
#             f.overhead_send(b'\x32')
#             f.pcb_comms()
#             return
#             
#         elif(command == b'\x33'):
#             print("Starting to downlink image")
#             f.transmit_image()
#             return
#         
#         elif(command == b'\x1E'):
#             print("Received Burnwire Command. Turning on Burnwire")
#             cubesat.deploy_boomarm()
#             return
#         
#         elif(command == b'\x1F'):
#             print("Received Battery Heater Command. Turning on Battery Heater")
#             f.emergency_heater_on()
#             return
#             
#             
#             
#              
#         
#     del f
#     
#     print("Warning: command received did not match any.")
#     print("The command received is: ", command)
#     print("The full message received is: ", msg)
#          
#         
# #     elif(command in commands):
# #         packetIndex = (msg[7:31]) #999999 is 20 bits long, should be able to handle any packet index request
# # #         print("Transmitting image")
# # 
# # #         time.sleep(0.5)
# # #         f.pcb_comms()
# 
# 
#             
#        
# 
# 
# 