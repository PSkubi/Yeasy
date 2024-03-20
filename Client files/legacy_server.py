########################## Sending data to the server ############################
# def send_string(msg):
#     message = msg.encode(FORMAT)                        # encode the message
#     msg_info = str(len(message))+'_str'                 # get the info of the message    
#     send_info = msg_info.encode(FORMAT)                 # encode the length of the message
#     send_info += b' ' * (HEADER - len(send_info))       # add spaces to the length of the message to make it 32 bytes
#     client.send(send_info)                              # send the length of the message                             
#     client.send(message)                                # send the message
# def send_bytes(msg):
#     msg_info = str(len(msg))+'_byt'                     # get the info of the message   
#     log(f'Sent message info: {msg_info}') 
#     send_info = msg_info.encode(FORMAT)                 # encode the length of the message
#     send_info += b' ' * (HEADER - len(send_info))       # add spaces to the length of the message to make it 32 bytes
#     client.send(send_info)                              # send the length of the message                             
#     client.send(msg)                                    # send the message
# def ask_img():
#     msg_info = 'imgask'.encode(FORMAT)                  # encode the 'imageask' string
#     msg_info += b' ' * (HEADER - len(msg_info))         # add spaces to the length of the message to make it 32 bytes
#     client.send(msg_info)                               # send the header containing 'imgask'
#     img_size = int((client.recv(HEADER)).decode(FORMAT))# receive the size of the image 
#     log(f'Server is sending an image of size <<{img_size}>>')
#     #client.send('ok'.encode(FORMAT))                    # send the 'ok' message to the server
#     img_rec = client.recv(img_size)                     # receive the image
#     log(f'Received an image of size <<{len(img_rec)}>> from the server!')
#     return img_rec
# def change_chamber(number):
#     msg_info = f'chamber_{number}'.encode(FORMAT)       # encode the 'chamber_{number}' string)              
#     msg_info += b' ' * (HEADER - len(msg_info))         # add spaces to the length of the message to make it 32 bytes
#     client.send(msg_info)
# for i in range(3):
#     #Arguments_files.append(os.path.join(BASE_DIR, f'C:\\Users\\piotr\\OneDrive - Imperial College London\\Yeasy\\YeasyImageRead\\Original Image Read\\Data\\Chamber {i+1} data\\YeastDataArguments.csv'))
#     #Values_files.append(os.path.join(BASE_DIR, f'C:\\Users\\piotr\\OneDrive - Imperial College London\\Yeasy\\YeasyImageRead\\Original Image Read\\Data\\Chamber {i+1} data\\YeastDataValues.csv'))
#     Arguments_files.append(os.path.join(BASE_DIR, f'Data/Chamber {i+1} data/YeastDataArguments.csv'))
#     Values_files.append(os.path.join(BASE_DIR, f'Data/Chamber {i+1} data/YeastDataValues.csv'))
#     log(f'Loaded arguments files: {Arguments_files[i]}')
#     log(f'Loaded values file: {Values_files[i]}')

# Use csv reader to read the numerical data from those two files
# def read_datafiles():
#     global plotarguments
#     global plotvalues
#     with open(Arguments_files[active_chamber], 'r') as file:
#         plotarguments = next(csv.reader(file))
#     plotarguments = [int(x) for x in plotarguments]
#     with open(Values_files[active_chamber], 'r') as file:
#         plotvalues = next(csv.reader(file))
#     plotvalues = [int(y) for y in plotvalues]