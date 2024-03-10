import socket
import threading
import os
from PIL import Image, ImageTk, ImageFile
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import csv
ImageFile.LOAD_TRUNCATED_IMAGES = True
import time
from Image_reading import *
from Syringe_control import *
from Plot_setup import *
start = time.time()

def log(msg):
    print(f'{round(time.time() - start,2)}: {msg}')
########################### SERVER SETUP ############################
HEADER = 32
PORT = 5050
#SERVER = '192.168.1.29'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(conn, addr):
    log(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        try:
            msg_info = conn.recv(HEADER).decode(FORMAT,errors='ignore')                    # receive and decode the message
            if msg_info != '':                                             # if the message is not empty, proceed
                if  'str' in msg_info:
                    msg_info = msg_info.replace(' ','')                                 # split the message info: length and type
                    msg_info = msg_info.split('_') 
                    if msg_info[1] == 'str':
                        msg_length = int(msg_info[0])
                        msg = conn.recv(msg_length).decode(FORMAT)
                        if msg == DISCONNECT_MESSAGE:
                            connected = False
                        log(f"[{addr}] {msg}")
                elif 'byt' in msg_info:                                             # if the message is not empty, proceed
                    msg_info = msg_info.replace(' ','')                                 # split the message info: length and type
                    msg_info = msg_info.split('_')                                 # split the message info: length and type
                    #log(f'Received message info: {msg_info}')
                    if msg_info[1] == 'byt':
                        msg_length = int(msg_info[0]) 
                        msg = conn.recv(msg_length)
                        global image_num
                        image_num+=1
                        log(f'Received bytes: Image number {image_num},size {msg_length} bytes')
                        global image
                        image_data = io.BytesIO(msg)
                        image = Image.open(image_data)
                        conn.send(f'Received bytes: Image number {image_num},size {msg_length} bytes'.encode(FORMAT))
                        #image.show()
                elif 'imgask' in msg_info:
                    log(f'The server was asked for an image by {addr}')
                    msg_info = str(len(byte_im)).encode(FORMAT)
                    msg_info += b' ' * (HEADER - len(msg_info))
                    conn.send(msg_info)
                    if conn.recv(2).decode(FORMAT) == 'ok':
                        log(f'Sending image to {addr}')
                        conn.send(byte_im)
                elif 'chamber' in msg_info:
                    msg_info = msg_info.split('_')
                    log(f'Changing chamber to {msg_info[1]}')
                    global active_chamber
                    active_chamber = int(msg_info[1])
                elif 'syr' in msg_info:
                    log(f'The server was asked for syringe control by {addr}')
                    msg_info = msg_info.replace(' ','')
                    msg_info = msg_info.split('_')
                    msg_info = msg_info[1:]
                    syringe_operation(msg_info)
                    log(f'The server received data for the syringe operation: {syringe_operation(msg_info)}')
        except UnicodeDecodeError:
            log('UnicodeDecodeError')
        except ConnectionResetError:
            log(f"[CONNECTION LOST] {addr} disconnected.")
            connected = False

    conn.close()
def server_operations():
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        log(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

########################### File Management ############################
# Start with identifying the directory and folders within it
folder =os.path.dirname(os.path.realpath(__file__))
flist = [0,0]
flist[0] = [x[0] for x in os.walk(folder)]
flist[1] = [x[1] for x in os.walk(folder)][0]
flist[0].pop(0)

# create a list of chamber names 
active_chamber = 0  # The chamber that is currently being viewed    
c_list = []
for i in range(20):
    c_list.append('Chamber '+str(i+1))
c_flist = [os.listdir(flist[0][0]), os.listdir(flist[0][1]), os.listdir(flist[0][2])]

chamber_sizes = [len(c_flist[0]), len(c_flist[1]), len(c_flist[2])]

# Which types of images are supported:
img_types = (".png", ".jpg", "jpeg", ".tiff", ".bmp")

# create sub list of image files (no wrong file types)

fnames = [0,0,0] # List storing the names of image files
fnames[0] = [f for f in c_flist[0] if f.lower().endswith(img_types)]

fnames[1] = [f for f in c_flist[1] if f.lower().endswith(img_types)]

fnames[2] = [f for f in c_flist[2] if f.lower().endswith(img_types)]

# If there are no suitable images, throw a popup
for i in range(3):
    if chamber_sizes[i] == 0:
        sg.popup(f'No files from Chamber {i}!')
        raise SystemExit()
################################# Server Setup ###################################

log("Server is starting...")
server.listen()
log(f"[LISTENING] Server is listening on {SERVER}")

################################# The main loop ###################################

# image_num is the number of the image opened
image_num = 0

# graphing is Bool for if a graph is currently shown or not
graphing = False
image = None
server_thread = threading.Thread(target=server_operations)
server_thread.start()
while True:
    time.sleep(0.25)
    if i >= chamber_sizes[active_chamber]:
       i -= chamber_sizes[active_chamber]
    filename = os.path.join(flist[0][active_chamber], fnames[active_chamber][i])
    byte_im = image_to_bytes(filename)
    i+=1