import socket
import time
import PySimpleGUI as sg
import os
from PIL import Image, ImageTk
import io
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Plot_setup import *
from Image_reading import *
from Syringe_control import *
start = time.time()

def log(msg):
    print(f'{round(time.time() - start,2)}: {msg}')

########################## Constant values setup ############################
HEADER = 32                                            # length of the header message
PORT = 5050                                            # port number                                 
SERVER = socket.gethostbyname(socket.gethostname())    # server IP address
ADDR = (SERVER, PORT)                                  # address of the server
FORMAT = 'utf-8'                                       # format of the message
DISCONNECT_MESSAGE = "!DISCONNECT"                     # disconnect message       
chamber_number = 20                                    # number of chambers                          

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
########################## Sending data to the server ############################
def send_string(msg):
    message = msg.encode(FORMAT)                       # encode the message
    msg_info = str(len(message))+'_str'                # get the info of the message    
    send_info = msg_info.encode(FORMAT)                # encode the length of the message
    send_info += b' ' * (HEADER - len(send_info))      # add spaces to the length of the message to make it 32 bytes
    client.send(send_info)                             # send the length of the message                             
    client.send(message)                               # send the message
def send_bytes(msg):
    msg_info = str(len(msg))+'_byt'                    # get the info of the message   
    log(f'Sent message info: {msg_info}') 
    send_info = msg_info.encode(FORMAT)                # encode the length of the message
    send_info += b' ' * (HEADER - len(send_info))      # add spaces to the length of the message to make it 64 bytes
    client.send(send_info)                             # send the length of the message                             
    client.send(msg)                                   # send the message
def ask_img():
    msg_info = 'imgask'.encode(FORMAT)
    msg_info += b' ' * (HEADER - len(msg_info))
    client.send(msg_info)
    img_size = int(client.recv(64).decode(FORMAT))
    log(f'Server is sending an image of size <<{img_size}>>')
    client.send('ok'.encode(FORMAT))
    img_rec = client.recv(img_size)
    log(f'Received an image of size <<{len(img_rec)}>> from the server!')
    return img_rec
def change_chamber(chamber):
    msg_info = 'chamber_'+str(chamber)
    msg_info = msg_info.encode(FORMAT)
    msg_info += b' ' * (HEADER - len(msg_info))
    client.send(msg_info)
########################### File Management ############################
# Start with identifying the directory and folders within it
folder =os.path.dirname(os.path.realpath(__file__))
flist = [0,0]
flist[0] = [x[0] for x in os.walk(folder)]
flist[1] = [x[1] for x in os.walk(folder)][0]
flist[0].pop(0)
# # Read the last folder to get the data - arguments file and values file

data_flist = [f[2] for f in os.walk(flist[0][-1])][0]
#ArgumentsFile = os.path.join(flist[0][-1],data_flist[0])
Arguments_file = os.path.join(os.getcwd(), 'Original Image Read\\Data\\Chamber 1 data\\YeastDataArguments.csv')
log(f'Loaded arguments file: {Arguments_file}')
#ValuesFile = os.path.join(flist[0][-1],data_flist[1])
Values_file = os.path.join(os.getcwd(), 'Original Image Read\\Data\\Chamber 1 data\\YeastDataValues.csv')
log(f'Loaded values file: {Values_file}')

# Use csv reader to read the numerical data from those two files

with open(Arguments_file, 'r') as file:
    plotarguments = next(csv.reader(file))
plotarguments = [int(x) for x in plotarguments]

with open(Values_file, 'r') as file:
    plotvalues = next(csv.reader(file))
plotvalues = [int(y) for y in plotvalues]

# create a list of chamber names 
c_list = []
for i in range(chamber_number):
    c_list.append('Chamber '+str(i+1))

################################# The layout ##################################
# active chamber index
filename = os.path.join(os.getcwd(), 'Original Image Read\\waiting.jpg')
image_elem = sg.Image(data=get_img_data(filename, first=True))
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

################################# The main loop ###################################
graphing = False
image_data = None
window = sg.Window('Yeasy', layout, return_keyboard_events=True,size=(1920,1080),location=(0, 0), use_default_focus=False, finalize=True,keep_on_top=False)
while True:
    # read the form, set the timeout in miliseconds
    event, values = window.read(timeout=250)
    # if the window closes - break the loop
    if event == sg.WIN_CLOSED:
        break
    elif event in ('Live view'):
        if not graphing:
            pass
        else:
            graphing = False
            #clear_canvas(window['-CANVAS-'].TKCanvas,figure_canvas)
            window['-COL2-'].update(visible=False)
            window['-COL1-'].update(visible=True)
            window.maximize()
            window['-COL1-'].expand(expand_x=True, expand_y=True, expand_row=False)
    elif event in (sg.TIMEOUT_EVENT) and not graphing:
        image_data = ask_img()
        log(f'Image data loaded: size <<{len(image_data)}>>')
    # this statement will show the graph
    elif event == 'Graph':
        graphing = True
        window[f'-COL1-'].update(visible=False)
        window[f'-COL2-'].update(visible=True)
        figure_canvas = draw_figure(window['-CANVAS-'].TKCanvas,create_plot(plotarguments,plotvalues))
        window.maximize()
        window['-COL2-'].expand(expand_x=True, expand_y=True, expand_row=False)
    elif event == 'listbox':            # something from the listbox
        active_chamber = c_list.index(values["listbox"][0])            # selected filename
        log(f'Changed active chamber to {active_chamber+1}')
        change_chamber(active_chamber)
    elif event =='Syringe control':
        syr_win_1 = syringewindow1()
        syr_win_2 = syringewindow2(syr_win_1[0],syr_win_1[1])
        log(syringe_operation(syr_win_2))
    # update window with new image
    # update page display
    if not graphing and image_data is not None:
            log(f'Trying to update image of type {type(image_data)}')
            if isinstance(image_data, bytes):
                image_data = io.BytesIO(image_data)
            image = Image.open(image_data)
            bio = io.BytesIO()
            image.save(bio, format='PNG')
            image_elem.update(data=bio.getvalue())
    elif graphing: 
        chamber_info_elementplt.update('Graph of data from Chamber {}'.format(active_chamber+1))
    log('Updated window')
# Close the window
window.close()