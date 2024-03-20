import socket
import time
import PySimpleGUI as sg
import os
from PIL import Image, ImageTk,ImageFile
import io
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Plot_setup import *
from Image_reading import *
from Syringe_control import *
import requests as req
import numpy as np  
from real_sample import *
from real_sample_counting import *
import cv2
import glob
ImageFile.LOAD_TRUNCATED_IMAGES = True
start = time.time() # Hello world!
counting_timer = time.time()
def log(msg):
    print(f'{round(time.time() - start,2)}: {msg}')
def setupwindow():
    layout = [
        [sg.Text(f'Please select the settings for the program')],
        [[sg.Text('Server IP:')],[sg.Input(f'{socket.gethostbyname(socket.gethostname())}',size=(20, 10),key='-Server IP-')]],
        [[sg.Text('Number of chambers')],[sg.Input('30',size=(20, 10),key='-Chamber no-')]],
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
# HEADER = 32                                             # length of the header message
# PORT = 5050                                             # port number                                 
SERVER = f"http://{setup[0]}/api"                         # api base route from server IP address
BASE_DIR = os.path.dirname(__file__)                      # base directory for relative paths
image_files_folder = os.path.join(BASE_DIR,'Image_files') # folder for the image files
whole_image_tif_path = os.path.join(image_files_folder,'whole_image.tif') # Create a path for the whole image tif file
# ADDR = (SERVER, PORT)                                   # address of the server
# FORMAT = 'utf-8'                                        # format of the message
# DISCONNECT_MESSAGE = "!DISCONNECT"                      # disconnect message       
chamber_number = int(setup[1])                          # number of chambers                          
syringe_number = int(setup[2])                          # number of syringes
control_dict={'Volume':0,'Duration':1,'µL':2, 'mL':3, 'L':4,'minutes':5,'hours':6,'µL/min':'UM', 'mL/min':'MM', 'µL/hr':'UH', 'mL/hr':'MH'} # dictionary for the control type encoding
# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a client socket
# client.connect(ADDR)                                        # connect to the server

def send_syringe_control(control_list):
    '''Send instructions to a syringe based on the control list'''
    for i in (0,4,5):
        try:
            control_list[i] = control_dict[control_list[i]]
        except:
            sg.popup('Wrong units selected!')
            return
    new_phase = {'rate':control_list[2],'units':control_list[4],'direction':"INF",'volume':control_list[3]}
    endpoint = f"{SERVER}/syringe/{control_list[1]}/pump_phase"
    req.post(endpoint, new_phase) 
    # msg = f'syr_{control_list[0]}_{control_list[1]}_{control_list[2]}_{control_list[3]}_{control_list[4]}_{control_list[5]}'.encode(FORMAT)
    # msg += b' ' * (HEADER - len(msg))
    # client.send(msg)
def stop_syringe(syringe_id):
    '''Send a message to the syringe asking to stop a syringe with a given id'''
    endpoint = f"{SERVER}/syringe/{syringe_id}/stop"
    req.post(endpoint)
def run_syringe(syringe_id):
    '''Send a message to the syringe asking to run a syringe with a given id'''
    endpoint = f"{SERVER}/syringe/{syringe_id}/run"
    req.post(endpoint)
def syringe_set_d(syringe_id,diameter):
    '''Send a message to the syringe asking to set the diameter of a syringe with a given id'''
    endpoint = f"{SERVER}/syringe/{syringe_id}/diameter"
    req.post(endpoint, {'value':diameter})
def syringe_clear(syringe_id):
    '''Clears the Pumping Program on the syringe with given id'''
    endpoint = f"{SERVER}/syringe/{syringe_id}/clear"
    req.post(endpoint)
def imgask():
    '''Ask the server for an image, output an array representing the image'''
    endpoint = f"{SERVER}/api/microscope/image"
    response = req.get(endpoint)
    img_array = np.array(response.content)
    return img_array
def count_all_chambers():
    '''Count the cells in all chambers, output a 2D list of cell numbers'''
    counting_list = []
    for i in range(chamber_number):
        cell_numbers,area_list = cell_counting(i+1)
        counting_list.append(cell_numbers)
    return counting_list
def getarguments(arg_list,active_chamber):
    '''Get argument lists for a given chamber from a list of argument lists'''
    arg_time_list_1 = []
    arg_time_list_2 = []
    for i in range(len(arg_list)):
        arg_time_list_1.append(arg_list[i][active_chamber][0])
        arg_time_list_2.append(arg_list[i][active_chamber][1])
    return arg_time_list_1,arg_time_list_2

########################### File Management ############################
active_chamber = 0
# create a list of chamber names 
c_list = []
for i in range(chamber_number):
    c_list.append('Chamber '+str(i+1))
# Prepare the lists for data
Arguments_list = []
Values_list = []
################################# The layout ##################################
#filename = os.path.join(BASE_DIR, 'Original Image Read\\waiting.jpg')    # Load the waiting image
waiting_image = os.path.join(BASE_DIR, 'waiting.jpg')    # Load the waiting image
#waiting_image='C:\\Users\\piotr\OneDrive - Imperial College London\\Yeasy\\YeasyImageRead\\Original Image Read\\waiting.jpg'

image_elem = sg.Image(data=get_img_data(waiting_image, first=True))              # Create the image element

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
#read_datafiles()
window['-COL2-'].expand(expand_x=True, expand_y=True, expand_row=False)
window['chamber_info_plt'].update(visible=False)
window.Maximize()

while True:
    event, values = window.read(timeout=250)                    # read the form, set the timeout in miliseconds
    if event == sg.WIN_CLOSED:                                  # if the window closes - break the loop
        break
    elif event in ('Live view') and graphing:                   # the live view button returns to the live view if graphing                                        
        graphing = False
        clear_canvas(window['-CANVAS-'].TKCanvas,figure_canvas) # clear the canvas
        window['-COL2-'].update(visible=False)                  # make the canvas column invisible
        window['-COL1-'].update(visible=True)                   # show the image column
        window['chamber_info_plt'].update(visible=False)        # make the graph info invisible
        window.Maximize()                                       # maximise the window
        window['-COL1-'].expand(expand_x=True, expand_y=True, expand_row=False) # expand the image column
    elif event in (sg.TIMEOUT_EVENT) and not graphing:          # if user doesn't do anything, update the image
        try:
            img_array = imgask()                                # ask the server for the image data
            image = Image.fromarray(img_array)                  # load the image from the array
            image_tiff = io.BytesIO()                           # create a bytes IO object for storing tiff data
            image.save(image_tiff, format='TIFF')               # save the image to the bytes IO object
            log(f'Image data loaded>>')                         
            image_files = glob.glob(image_files_folder+'\\*.tif') # get the list of tif files in the image_files folder
            for file in image_files:
                os.remove(file)                                 # Clean the Image_files folder before saving new files
            log(f'Cleaned the Image_files folder')
            # save the image as a tif file
            image_tiff.save(whole_image_tif_path)               # Save the whole image as a tif file
            log(f'Saved the whole image as a tif file')
            sample_read(whole_image_tif_path,chamber_number)    # split the whole image into chambers
            user_image = Image.open(f'Image_files\\chamber{active_chamber}.tif') # Open the image of the active chamber
            if time.time() - counting_timer > 60:               # If more than 60 seconds passed from last counting
                log(f'Trying to count cells in all chambers')   # try to count the cells
                counting_timer = time.time()                    # reset the timer
                cell_numbers,area_list = count_all_chambers()   # count the cells in all chambers
                log(f'Counted cells in chambers')
                Values_list.append(cell_numbers)                # append the cell numbers to the values list
                Arguments_list.append((time.time() - start)/60) # append the time (in mins) to the arguments list
        except:
            sg.popup('Connection error')                # throw a popup if that fails
    elif event == 'Graph':                                              # the graph button opens the graph    
        graphing = True
        #read_datafiles()
        green_arguments,orange_arguments = getarguments(Arguments_list,active_chamber)
        window['-COL1-'].update(visible=False)
        window['-COL2-'].update(visible=True)
        window['chamber_info_plt'].update(visible=True)
        figure_canvas = draw_figure(window['-CANVAS-'].TKCanvas,create_plot(Values_list,green_arguments,orange_arguments))
        window.maximize()
        window['-COL2-'].expand(expand_x=True, expand_y=True, expand_row=False)
    elif event == 'listbox':                                            # something from the list of chambers
        active_chamber = c_list.index(values["listbox"][0])             # change the active chamber
        log(f'Changed active chamber to {active_chamber+1}')            # log the change
        if graphing:
            #read_datafiles()
            green_arguments,orange_arguments = getarguments(Arguments_list,active_chamber)
            clear_canvas(window['-CANVAS-'].TKCanvas,figure_canvas)
            figure_canvas = draw_figure(window['-CANVAS-'].TKCanvas,create_plot(Values_list,green_arguments,orange_arguments))
            window['-CANVAS-'].expand(expand_x=True, expand_y=True, expand_row=False)
    elif event =='Syringe control':                                     # if the user clicks on the syringe control button
        syr_win_1 = syringewindow1()                                    # open the first syringe control window
        if syr_win_1 != []:
            syr_win_2 = syringewindow2(syr_win_1[0],syr_win_1[1],syringe_number)        # open the second syringe control window
            log(f'The user passed syringe control: {syringe_operation(syr_win_2)}')     # log the operation of the syringes
            if syringe_operation(syr_win_2) != ('None',0,0,0,0,0):                      # if the user actually selected something
                send_syringe_control(syr_win_2)                        # send the operation to the server
    if not graphing:      
        #image = imgask()                                            # image update 
        chamber_info_img.update('Live video feed from Chamber {}'.format(active_chamber+1))           #                 
        # log(f'Trying to update image of type {type(image_data)}')       # log the attempt
        # if isinstance(image_data, bytes):                               # if the image data is bytes, change it to bytes IO
        #     image_data = io.BytesIO(image_data)
        # image = Image.open(image_data)                                  # open the image
        bio = io.BytesIO()                                              # create a bytes IO object
        user_image.save(bio, format='PNG')                                   # save the image to the bytes IO object
        image_elem.update(data=bio.getvalue())                          # update the image element
        pass
    elif graphing: 
        chamber_info_plt.update('Graph of data from Chamber {}'.format(active_chamber+1))
    log('Updated window')
window.close()