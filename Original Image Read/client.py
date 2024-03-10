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
def setupwindow():
    layout = [
        [sg.Text(f'Please select the settings for the program')],
        [[sg.Text('Server IP:')],[sg.Input(f'{socket.gethostbyname(socket.gethostname())}',size=(20, 10),key='-Server IP-')]],
        [[sg.Text('Number of chambers')],[sg.Input('20',size=(20, 10),key='-Chamber no-')]],
        [[sg.Text('Number of syringes')],[sg.Input('3',size=(20, 10),key='-Syringe no-')]],
        [sg.Button('Cancel', size=(10,4)),sg.Button('Confirm',size=(10,4))]
    ]
    setupwindow= sg.Window(f'Program setup',layout,size=(400,300))
    while True:
        event, values = setupwindow.read()
        if event == 'Cancel' or event == sg.WIN_CLOSED:
            exit() 
        elif event =='Confirm':
            userinput = [str(values['-Server IP-']),int(values['-Chamber no-']),int(values['-Syringe no-'])]
            break
    setupwindow.close()
    return userinput
setup = setupwindow()
log(f'Loaded setup: Server IP is {setup[0]}, number of chambers is {setup[1]}, number of syringes is {setup[2]}') 
########################## Constant values setup ############################
HEADER = 32                                             # length of the header message
PORT = 5050                                             # port number                                 
SERVER = setup[0]                                       # server IP address
ADDR = (SERVER, PORT)                                   # address of the server
FORMAT = 'utf-8'                                        # format of the message
DISCONNECT_MESSAGE = "!DISCONNECT"                      # disconnect message       
chamber_number = int(setup[1])                          # number of chambers                          
syringe_number = int(setup[2])                          # number of syringes
control_dict={'Volume':0,'Duration':1,'µL':2, 'mL':3, 'L':4,'minutes':5,'hours':6,'µL/min':7, 'mL/min':8, 'µL/hr':9, 'mL/hr':10} # dictionary for the control type encoding

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a client socket
client.connect(ADDR)                                        # connect to the server
########################## Sending data to the server ############################
def send_string(msg):
    message = msg.encode(FORMAT)                        # encode the message
    msg_info = str(len(message))+'_str'                 # get the info of the message    
    send_info = msg_info.encode(FORMAT)                 # encode the length of the message
    send_info += b' ' * (HEADER - len(send_info))       # add spaces to the length of the message to make it 32 bytes
    client.send(send_info)                              # send the length of the message                             
    client.send(message)                                # send the message
def send_bytes(msg):
    msg_info = str(len(msg))+'_byt'                     # get the info of the message   
    log(f'Sent message info: {msg_info}') 
    send_info = msg_info.encode(FORMAT)                 # encode the length of the message
    send_info += b' ' * (HEADER - len(send_info))       # add spaces to the length of the message to make it 32 bytes
    client.send(send_info)                              # send the length of the message                             
    client.send(msg)                                    # send the message
def ask_img():
    msg_info = 'imgask'.encode(FORMAT)                  # encode the 'imageask' string
    msg_info += b' ' * (HEADER - len(msg_info))         # add spaces to the length of the message to make it 32 bytes
    client.send(msg_info)                               # send the header containing 'imgask'
    img_size = int(client.recv(HEADER).decode(FORMAT))  # receive the size of the image 
    log(f'Server is sending an image of size <<{img_size}>>')
    client.send('ok'.encode(FORMAT))                    # send the 'ok' message to the server
    img_rec = client.recv(img_size)                     # receive the image
    log(f'Received an image of size <<{len(img_rec)}>> from the server!')
    return img_rec
def change_chamber(number):
    msg_info = f'chamber_{number}'.encode(FORMAT)       # encode the 'chamber_{number}' string)              
    msg_info += b' ' * (HEADER - len(msg_info))         # add spaces to the length of the message to make it 32 bytes
    client.send(msg_info)
def send_syringe_control(control_list):
    control_list[0] = control_dict[control_list[0]]
    control_list[4] = control_dict[control_list[4]]
    control_list[5] = control_dict[control_list[5]]
    msg = f'syr_{control_list[0]}_{control_list[1]}_{control_list[2]}_{control_list[3]}_{control_list[4]}_{control_list[5]}'.encode(FORMAT)
    msg += b' ' * (HEADER - len(msg))
    client.send(msg)
########################### File Management ############################
active_chamber = 0
# create a list of chamber names 
c_list = []
for i in range(chamber_number):
    c_list.append('Chamber '+str(i+1))
# Load the arguments and values from the csv files
Arguments_files = []
Values_files = []
for i in range(3):
    Arguments_files.append(os.path.join(os.getcwd(), f'Original Image Read\\Data\\Chamber {i+1} data\\YeastDataArguments.csv'))
    Values_files.append(os.path.join(os.getcwd(), f'Original Image Read\\Data\\Chamber {i+1} data\\YeastDataValues.csv'))
log(f'Loaded arguments files: {Arguments_files}')
log(f'Loaded values file: {Values_files}')

# Use csv reader to read the numerical data from those two files
def read_datafiles():
    global plotarguments
    global plotvalues
    with open(Arguments_files[active_chamber], 'r') as file:
        plotarguments = next(csv.reader(file))
    plotarguments = [int(x) for x in plotarguments]
    with open(Values_files[active_chamber], 'r') as file:
        plotvalues = next(csv.reader(file))
    plotvalues = [int(y) for y in plotvalues]

################################# The layout ##################################
filename = os.path.join(os.getcwd(), 'Original Image Read\\waiting.jpg')    # Load the waiting image
image_elem = sg.Image(data=get_img_data(filename, first=True))              # Create the image element

# Also get display elements. This is just for debugging (so that we can see what's going on)
chamber_info_img = sg.Text(text='Live video feed from Chamber {}'.format(active_chamber+1),expand_x=True,justification='center',font=('Calibri',30))
chamber_info_plt = sg.Text(text='Graph of data from Chamber {}'.format(active_chamber+1),expand_x=True,justification='center',font=('Calibri',30),key='chamber_info_plt')

# define layout, show and read the form

canvas_elem = sg.Canvas(size=(1920, 1080),key='-CANVAS-',expand_x=True)
imgcol = [[chamber_info_img],[image_elem]]
graphcol = [[chamber_info_plt],[canvas_elem]]

leftcol = [
    [sg.Listbox(values=c_list,font=('Calibri', 20), change_submits=True, size=(30, 20), key='listbox',expand_y=True)],
    [sg.Button('Live view', size=(8, 2)), sg.Button('Graph', size=(8, 2)),sg.Button('Syringe control',size=(8,2))],
]

layout = [[sg.Column(leftcol,expand_x=True), sg.Column(imgcol, key='-COL1-',expand_x=True), sg.Column(graphcol, visible=False, key='-COL2-',expand_x=True)]]

################################# The main loop ###################################
graphing = False
window = sg.Window('Yeasy', layout, return_keyboard_events=True,size=(1920,1080),location=(0, 0), use_default_focus=True, finalize=True,keep_on_top=False,resizable=True).Finalize()
read_datafiles()
window['-COL2-'].expand(expand_x=True, expand_y=True, expand_row=False)
figure_canvas = draw_figure(window['-CANVAS-'].TKCanvas,create_plot(plotarguments,plotvalues))
clear_canvas(window['-CANVAS-'].TKCanvas,figure_canvas)
window['chamber_info_plt'].update(visible=False)
window.Maximize()

while True:
    event, values = window.read(timeout=250)                            # read the form, set the timeout in miliseconds
    if event == sg.WIN_CLOSED:                                          # if the window closes - break the loop
        break
    elif event in ('Live view') and graphing:                           # the live view button returns to the live view                                        
        graphing = False
        clear_canvas(window['-CANVAS-'].TKCanvas,figure_canvas)
        window['-COL2-'].update(visible=False)
        window['-COL1-'].update(visible=True)
        window['chamber_info_plt'].update(visible=False)
        window.Maximize()
        window['-COL1-'].expand(expand_x=True, expand_y=True, expand_row=False)
    elif event in (sg.TIMEOUT_EVENT) and not graphing:
        image_data = ask_img()
        log(f'Image data loaded: size <<{len(image_data)}>>')
    elif event == 'Graph':                                              # the graph button opens the graph    
        graphing = True
        read_datafiles()
        window['-COL1-'].update(visible=False)
        window['-COL2-'].update(visible=True)
        window['chamber_info_plt'].update(visible=True)
        figure_canvas = draw_figure(window['-CANVAS-'].TKCanvas,create_plot(plotarguments,plotvalues))
        window.maximize()
        window['-COL2-'].expand(expand_x=True, expand_y=True, expand_row=False)
    elif event == 'listbox':                                            # something from the list of chambers
        active_chamber = c_list.index(values["listbox"][0])             # change the active chamber
        log(f'Changed active chamber to {active_chamber+1}')            # log the change
        change_chamber(active_chamber)                                  # send the change to the server
        if graphing:
            read_datafiles()
            clear_canvas(window['-CANVAS-'].TKCanvas,figure_canvas)
            figure_canvas = draw_figure(window['-CANVAS-'].TKCanvas,create_plot(plotarguments,plotvalues))
            window['-CANVAS-'].expand(expand_x=True, expand_y=True, expand_row=False)
    elif event =='Syringe control':                                     # if the user clicks on the syringe control button
        syr_win_1 = syringewindow1()                                    # open the first syringe control window
        if syr_win_1 != []:
            syr_win_2 = syringewindow2(syr_win_1[0],syr_win_1[1],syringe_number)        # open the second syringe control window
            log(f'The user passed syringe control: {syringe_operation(syr_win_2)}')     # log the operation of the syringes
            if syringe_operation(syr_win_2) != ('None',0,0,0,0,0):                      # if the user actually selected something
                send_syringe_control(syr_win_2)                        # send the operation to the server
    if not graphing:                                                    # image update 
        chamber_info_img.update('Live video feed from Chamber {}'.format(active_chamber+1))           #                 
        log(f'Trying to update image of type {type(image_data)}')       # log the attempt
        if isinstance(image_data, bytes):                               # if the image data is bytes, change it to bytes IO
            image_data = io.BytesIO(image_data)
        image = Image.open(image_data)                                  # open the image
        bio = io.BytesIO()                                              # create a bytes IO object
        image.save(bio, format='PNG')                                   # save the image to the bytes IO object
        image_elem.update(data=bio.getvalue())                          # update the image element
    elif graphing: 
        chamber_info_plt.update('Graph of data from Chamber {}'.format(active_chamber+1))
    log('Updated window')
window.close()