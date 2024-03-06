import socket
import threading
import time
import PySimpleGUI as sg
import os
from PIL import Image, ImageTk
import io
import matplotlib.pyplot as plt
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

########################### SERVER SETUP ############################
HEADER = 64
PORT = 5050
SERVER = '192.168.1.29'
#SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            print(f"[{addr}] {msg}")

    conn.close()

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
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

################################## Image reading ######################################

# Define a function which opens an image file using Python Imaging Library
def get_img_data(f, maxsize=(1600, 1000), first=False):
    """Generate image data using PIL"""
    img = Image.open(f)
    img.thumbnail(maxsize)
    if first:                     
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)

##################################  Start reading data ######################################

# active chamber index
active_chamber = 0

# Take the first file in the directory
filename = os.path.join(flist[0][active_chamber], fnames[active_chamber][0]) 

# Extract image data
image_data = bytes(get_img_data(filename, first=True))
image_size = len(image_data)
print(f'Image size: {image_size}')
i = 0
while True:
    time.sleep(1)
    i += 1
    if i >= chamber_sizes[active_chamber]:
        i -= chamber_sizes[active_chamber]
    filename = os.path.join(flist[0][active_chamber], fnames[active_chamber][i])
    image_data = bytes(get_img_data(filename, first=True))
    image_size = len(image_data)
    print(f'Image size of {i}: {image_size}')
#print("Server is starting...")
#start()