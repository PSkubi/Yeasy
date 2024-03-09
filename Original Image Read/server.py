import socket
import threading
import os
from PIL import Image, ImageTk
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import csv
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import time
from Image_reading import *
from Syringe_control import *
from Plot_setup import *
########################### SERVER SETUP ############################
HEADER = 64
PORT = 5050
#SERVER = '192.168.1.29'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        try:
            msg_info = conn.recv(HEADER).decode(FORMAT,errors='ignore')                    # receive and decode the message
            if  'str' in msg_info or 'byt' in msg_info and not msg_info == '':                                             # if the message is not empty, proceed
                msg_info = msg_info.replace(' ','')                                 # split the message info: length and type
                msg_info = msg_info.split('_')                                 # split the message info: length and type
                #print(f'Received message info: {msg_info}')
                if msg_info[1] == 'str':
                    msg_length = int(msg_info[0])
                    msg = conn.recv(msg_length).decode(FORMAT)
                    if msg == DISCONNECT_MESSAGE:
                        connected = False
                    print(f"[{addr}] {msg}")
                elif msg_info[1] == 'byt':
                    msg_length = int(msg_info[0]) 
                    msg = conn.recv(msg_length)
                    global image_num
                    image_num+=1
                    print(f'Received bytes: Image number {image_num},size {msg_length} bytes')
                    global image
                    image_data = io.BytesIO(msg)
                    image = Image.open(image_data)
                    conn.send(f'Received bytes: Image number {image_num},size {msg_length} bytes'.encode(FORMAT))
                    #image.show()
            elif 'imgask' in msg_info and not msg_info == '':
                print(f'The server was asked for an image by {addr}')
                msg_info = str(len(byte_im)).encode(FORMAT)
                msg_info += b' ' * (HEADER - len(msg_info))
                conn.send(msg_info)
                if conn.recv(2).decode(FORMAT) == 'ok':
                    print(f'Sending image to {addr}')
                    conn.send(byte_im)
        except UnicodeDecodeError:
            print('UnicodeDecodeError')
        except ConnectionResetError:
            print(f"[CONNECTION LOST] {addr} disconnected.")
            connected = False

    conn.close()
def server_operations():
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

########################### File Management ############################
# Start with identifying the directory and folders within it
folder =os.path.dirname(os.path.realpath(__file__))
flist = [0,0]
flist[0] = [x[0] for x in os.walk(folder)]
flist[1] = [x[1] for x in os.walk(folder)][0]
flist[0].pop(0)

# create a list of chamber names 
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
if chamber_sizes[0] == 0:
    sg.popup('No files from Chamber 1!')
    raise SystemExit()
if chamber_sizes[1] == 0:
    sg.popup('No files from Chamber 2!')
    raise SystemExit()
if chamber_sizes[2] == 0:
    sg.popup('No files from Chamber 3!')
    raise SystemExit()


# ################################# The layout ##################################
# active chamber index
active_chamber = 0
c_list = []
for i in range(20):
    c_list.append('Chamber '+str(i+1))

print("Server is starting...")
server.listen()
print(f"[LISTENING] Server is listening on {SERVER}")

################################# The main loop ###################################

# image_num is the number of the image opened
image_num = 0

# graphing is Bool for if a graph is currently shown or not
graphing = False
image = None
server_thread = threading.Thread(target=server_operations)
server_thread.start()
while True:
    time.sleep(1)
    if i >= chamber_sizes[active_chamber]:
       i -= chamber_sizes[active_chamber]
    filename = os.path.join(flist[0][active_chamber], fnames[active_chamber][i])
    byte_im = image_to_bytes(filename)
    i+=1