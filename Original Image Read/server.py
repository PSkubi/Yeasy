import socket
import threading
import time
import re
import os
from PIL import Image, ImageTk
import io
import matplotlib.pyplot as plt
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg

########################### SERVER SETUP ############################
HEADER = 64
PORT = 5050
#SERVER = '192.168.1.29'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
info_msg_pattern = r"Image size of \d+: \d+"
num_pattern = r"\d+"

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
            if re.match(info_msg_pattern, msg):
                data_number, data_size = list(map(int, re.findall(num_pattern, msg)))
                data = conn.recv(data_size)
                global image_elem
                image_elem=sg.Image(data=data)
            #print(data)

    conn.close()

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
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
filename = os.path.join(os.getcwd(), 'Original Image Read\\example.jpg')
image_elem = sg.Image(data=get_img_data(filename, first=True))

################################# The layout ##################################
# active chamber index
active_chamber = 0
c_list = []
for i in range(20):
    c_list.append('Chamber '+str(i+1))

# Also get display elements. This is just for debugging (so that we can see what's going on)
chamber_info_elementimg = sg.Text(text='Live video feed from Chamber {}'.format(active_chamber+1),expand_x=True,justification='center',font=('Calibri',30))
chamber_info_elementplt = sg.Text(text='Graph of data from Chamber {}'.format(active_chamber+1),expand_x=True,justification='center',font=('Calibri',30))

# define layout, show and read the form

canvas_elem = sg.Canvas(size=(1200, 400),key='-CANVAS-',expand_x=True)
imgcol = [[chamber_info_elementimg],[image_elem]]
graphcol = [[chamber_info_elementplt],[canvas_elem]]

leftcol = [
    [sg.Listbox(values=c_list,font=('Calibri', 20), change_submits=True, size=(30, 20), key='listbox',expand_y=True)],
    [sg.Button('Live view', size=(8, 2)), sg.Button('Graph', size=(8, 2)),sg.Button('Syringe control',size=(8,2))],
]

layout = [[sg.Column(leftcol,expand_x=True), sg.Column(imgcol, key='-COL1-',expand_x=True), sg.Column(graphcol, visible=False, key='-COL2-',expand_x=True)]]

window = sg.Window('Yeasy', layout, return_keyboard_events=True,size=(1920,1080),
                   location=(0, 0), use_default_focus=False, finalize=True,keep_on_top=False)

print("Server is starting...")
#start()
server.listen()
print(f"[LISTENING] Server is listening on {SERVER}")
################################# The main loop ###################################

# i is the number of the image opened
i = 0

# graphing is Bool for if a graph is currently shown or not
graphing = False

while True:
    # read the form, set the timeout in miliseconds
    event, values = window.read(timeout=100)
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    #print(event, values)
    # if the window closes - break the loop
    if event == sg.WIN_CLOSED:
        break
    # elif event in ('Live view'):
    #     if not graphing:
    #         pass
    #     else:
    #         graphing = False
    #         clear_canvas(window['-CANVAS-'].TKCanvas,figure_canvas)
    #         window['-COL2-'].update(visible=False)
    #         window['-COL1-'].update(visible=True)
    #         window.maximize()
    #         window['-COL1-'].expand(expand_x=True, expand_y=True, expand_row=False)
    # elif event in (sg.TIMEOUT_EVENT) and not graphing:
    #     i += 1
    #     if i >= chamber_sizes[active_chamber]:
    #         i -= chamber_sizes[active_chamber]
    #     filename = os.path.join(flist[0][active_chamber], fnames[active_chamber][i])
    
    # this statement will show the graph
    # elif event == 'Graph':
    #     graphing = True
    #     window[f'-COL1-'].update(visible=False)
    #     window[f'-COL2-'].update(visible=True)
    #     figure_canvas = draw_figure(window['-CANVAS-'].TKCanvas,create_plot(plotarguments,plotvalues))
    #     window.maximize()
    #     window['-COL2-'].expand(expand_x=True, expand_y=True, expand_row=False)
    # elif event == 'listbox':            # something from the listbox
    #     active_chamber = c_list.index(values["listbox"][0])            # selected filename
    #     filename = os.path.join(flist[0][active_chamber], fnames[active_chamber][0])  # read this file
    # elif event =='Syringe control':
    #     syringecontrols = syringewindow()
    #     syringe_operation(syringecontrols)
        
    # update window with new image
    # update page display
    # if not graphing:
    #     image_elem.update(data=get_img_data(filename, first=True))
    #     chamber_info_elementimg.update('Live video feed from Chamber {}'.format(active_chamber+1))
    # else: 
    #     chamber_info_elementplt.update('Graph of data from Chamber {}'.format(active_chamber+1))
# Close the window
window.close()