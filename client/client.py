import time
import PySimpleGUI as sg
import os
from PIL import Image, ImageTk,ImageFile
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests as req
import numpy as np  
import cv2
import math
import glob
import threading
import queue
from datetime import datetime
ImageFile.LOAD_TRUNCATED_IMAGES = True
BASE_DIR = os.path.dirname(__file__)                      # base directory for relative paths
sg.set_options(icon=os.path.join(BASE_DIR,'icon.ico'))    # set the icon for the window
while True:
    start = time.time() 
    counting_timer = time.time()
    def log(msg):
        print(f'{(time.time() - start):.2f}: {msg}')
    def setupwindow():
        layout = [
            [sg.Text(f'Please select the settings for the program, and click Confirm')],
            [[sg.Text('Server IP:')],[sg.Input('127.0.0.1:5000',size=(20, 10),key='-Server IP-')]],
            [[sg.Text('Number of chambers:')],[sg.Input('30',size=(20, 10),key='-Chamber no-')]],
            [[sg.Text('Number of syringes:')],[sg.Input('3',size=(20, 10),key='-Syringe no-')]],
            [[sg.Text('Cell counting interval [s]:')],[sg.Input('20',size=(20, 10),key='-Counting int-')]],
            [sg.Button('Cancel', size=(8,2)),sg.Button('Confirm',size=(8,2)),sg.Button('Help',size=(8,2))]
        ]
        setupwindow= sg.Window(f'Program setup',layout,size=(400,300))
        while True:
            event, values = setupwindow.read()
            if event == 'Cancel' or event == sg.WIN_CLOSED:
                exit() 
            elif event =='Confirm':
                try:
                    userinput = [str(values['-Server IP-']),int(values['-Chamber no-']),int(values['-Syringe no-']),int(values['-Counting int-'])]
                except:
                    sg.popup('Invalid input! Try again')
                    userinput = [[],[],[],[]]
                break
            elif event == 'Help':
                sg.popup('Please enter the IP address of the server, the number of chambers and the number of syringes. \n \n The IP address should be similar to this: 127.0.0.1:5000, and is displayed when launching the Server.\n  \n The number of chambers for the dedicated chip is 30, but setting this to 15 will enable the user to view two chambers at once. \n \n Click Confirm after writing these settings to continue.')
        setupwindow.close()
        return userinput
    setup = setupwindow()
    while setup == [[],[],[],[]]:
        setup = setupwindow()

    log(f'Loaded setup: Server IP is {setup[0]}, number of chambers is {setup[1]}, number of syringes is {setup[2]}, counting interval is {setup[3]}s')

    ########################## Constant values setup ############################
                                
    SERVER = f"http://{setup[0]}/api"                         # api base route from server IP address
    image_files_folder = os.path.join(BASE_DIR,'Image_files') # folder for the image files
    whole_image_tif_path = os.path.join(image_files_folder,'whole_image.tif') # Create a path for the whole image tif file     
    chamber_number = int(setup[1])                          # number of chambers                          
    syringe_number = int(setup[2])                          # number of syringes
    counting_interval = int(setup[3])                       # time in seconds between counting
    control_dict={'Volume':0,'Duration':1,'µL':2, 'mL':3, 'L':4,'minutes':5,'hours':6,'µL/min':'UM', 'mL/min':'MM', 'µL/hr':'UH', 'mL/hr':'MH'} # dictionary for the control type encoding
    if not os.path.exists(image_files_folder):
        os.makedirs(image_files_folder)
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
        endpoint = f"{SERVER}/microscope/image"
        response = req.get(endpoint)
        image_bytes = io.BytesIO(response.content)
        return image_bytes
    ######################## Syringe Windows ###############################
    def syringe_operation(syringecontrols):
        '''Here will be the code operating the syringe, taking the list of controltype,syringeno,flowrate,control,flowrate_units,control_units'''
        # here #
        if syringecontrols == []:
            return ('None',0,0,0,0,0)
        else:
            controltype,syringeno,flowrate,control,flowrate_units,control_units = syringecontrols
        return (controltype,syringeno,flowrate,control,flowrate_units,control_units)
    def syringewindow1():
        layout = [
            [sg.Text('Do you want to use volume or duration control?')],
            [sg.Button('Volume', size=(8, 2)),sg.Button('Duration', size=(8, 2))],
            [sg.Button('Cancel', size=(8, 2))]
        ]
        syringewindow1 = sg.Window('Control type',layout,size=(600,400))
        while True:
            event, values = syringewindow1.read()
            if event in (sg.WIN_CLOSED,'Cancel'):
                con_type = []
                break
            elif event=='Volume':
                con_type = ['Volume',['µL', 'mL']]
                break
            elif event=='Duration':
                con_type = ['Duration',['minutes','hours']]
                break
        syringewindow1.close()
        return con_type
    def syringewindow2(type,measure_units,syringeno):
        flowrate_units = ['µL/min', 'mL/min', 'µL/hr', 'mL/hr']
        layout = [
            [sg.Text(f'You have chosen {type} control')],
            [[sg.Text('Syringe number:')],[sg.Input('',size=(10, 4),key='-Syringe no-')]],
            [[sg.Text('Flow rate:')],[sg.Input('',size=(10, 4),key='-Flow rate-'),sg.Combo(flowrate_units, font=('Arial Bold', 12),key='-Flowrate units-')]],#sg.Text('L/min')]],
            [[sg.Text(f'{type}:')],[sg.Input('', size=(10, 4),key ='-Control-'),sg.Combo(measure_units, font=('Arial Bold', 12),key='-Control units-')]],
            [sg.Button('Cancel', size=(8, 2)),sg.Button('Confirm',size=(8,2))]
        ]
        syringewindow2= sg.Window(f'Flow rate and {type} control',layout,size=(600,400))
        while True:
            event, values = syringewindow2.read()
            if event == 'Cancel':
                userinput = []  
                break
            elif event in ('Confirm'):
                userinput = [type,int(values['-Syringe no-']),float(values['-Flow rate-']),float(values['-Control-']),str(values['-Flowrate units-']),str(values['-Control units-'])]
                if userinput[2] == 0 or userinput[3] == 0:
                    sg.popup(f'Flow rate or {type} value cannot be 0')
                    continue
                elif int(userinput[2]) < 0 or userinput[3] < 0:
                    sg.popup(f'Flow rate or {type} value cannot be negative')
                    continue
                elif userinput[1]>syringeno:
                    sg.popup(f'Syringe number cannot be higher than {syringeno}')
                    continue
                elif userinput[1]<1:
                    sg.popup(f'Syringe number cannot be lower than 1')
                    continue
                elif userinput[1] == '':
                    sg.popup(f'Syringe number was not specified')
                    continue
                elif userinput[2] == '':
                    sg.popup(f'Flow rate was not specified')
                    continue
                elif userinput[3] == '':    
                    sg.popup(f'{type} was not specified')
                    continue
                elif userinput[4] == '':
                    sg.popup(f'Flow rate units were not specified')
                    continue
                elif userinput[5] == '':
                    sg.popup(f'{type} units were not specified')
                    continue
                break
        if userinput[0] == 'Duration': # Convert duration to volume
            if userinput[5] == 'minutes' and userinput[2] == 'µL/min':
                userinput[3] = userinput[3]*userinput[2]
                userinput[5] = 'µL'
            elif userinput[5] == 'minutes' and userinput[2] == 'mL/min':
                userinput[3] = userinput[3]*userinput[2]
                userinput[5] = 'mL'
            elif userinput[5] == 'hours'and userinput[2] == 'mL/min':        
                userinput[3] = userinput[3]*userinput[2]*60
                userinput[5] = 'mL'
            elif userinput[5] == 'hours'and userinput[2] == 'µL/min':        
                userinput[3] = userinput[3]*userinput[2]*60
                userinput[5] = 'µL'
            elif userinput[5] == 'minutes' and userinput[2] == 'µL/hr':
                userinput[3] = userinput[3]*userinput[2]/60
                userinput[5] = 'µL'
            elif userinput[5] == 'minutes' and userinput[2] == 'mL/hr':
                userinput[3] = userinput[3]*userinput[2]/60
                userinput[5] = 'mL'
            elif userinput[5] == 'hours'and userinput[2] == 'µL/hr':        
                userinput[3] = userinput[3]*userinput[2]
                userinput[5] = 'µL'
            elif userinput[5] == 'hours'and userinput[2] == 'mL/hr':        
                userinput[3] = userinput[3]*userinput[2]
                userinput[5] = 'mL'
        syringewindow2.close()
        return userinput
    ########################## Image Reading ##############################
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
    ########################### Cell counting functions ####################
    def cell_counting(chamber_no, mask, splitted_chamber):

        # get the chamber_num and get the prepared masks
        chamber_img = splitted_chamber[chamber_no - 1]
        chamber_mask = mask[chamber_no - 1]
        green_mask_img = chamber_mask[1]
        orange_mask_img = chamber_mask[0]

        # delete the mask out of the chamber
        green_mask_img[:, 0:50] = 0
        green_mask_img[:, 550::] = 0
        green_mask_img[0:190, :] = 0
        green_mask_img[660::, :] = 0
        orange_mask_img[:, 0:50] = 0
        orange_mask_img[:, 550::] = 0
        orange_mask_img[0:200, :] = 0
        orange_mask_img[660::, :] = 0
        cropped_mask = [green_mask_img, orange_mask_img]

        # find the contour
        green_mask = cropped_mask[0]
        orange_mask = cropped_mask[1]
        contours_green, hierarchy = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_orange, hierarchy = cv2.findContours(orange_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = [contours_green, contours_orange]
        mask_name = ['green', 'orange']

        # define the area of cell
        average_cell_area = 290
        connected_cell_area = 600
        minimum_cell_area = 30

        # counting the cell and draw the detected contour
        cell_numbers = []
        area_list = []
        for i in range(0, len(mask_name)):
            cells = 0
            contour_color = [(0, 128, 0), (0, 128, 255)]
            sum_area = 0

            for c in contours[i]:
                area = cv2.contourArea(c)
                if area > minimum_cell_area:
                    sum_area = sum_area + area
                    cv2.drawContours(chamber_img, [c], -1, contour_color[i], 2)
                    if area > connected_cell_area:
                        cells += math.floor(area / average_cell_area)
                    else:
                        cells += 1

            cell_numbers.append(cells)
            area_list.append(sum_area)

            # print(mask_name[i] + 'Cells: {}'.format(cells))
            # print(mask_name[i] + 'Area: {}'.format(sum_area))

        return cell_numbers, area_list, chamber_img
    def sample_read(sample, chamber_num):

        # read and display the image
        image_file = sample
        img = cv2.imread(image_file)
        img_colnum = img.shape[1]
        print('sample colnum: ' + str(img_colnum))
        img_rownum = img.shape[0]
        print('sample rownum: ' + str(img_rownum))

        # crop the image and split into multiple chambers
        cropped_img = img[img_rownum // 2 - 400:img_rownum // 2 + 450, img_colnum // 2 - 9300:img_colnum // 2 + 8800]
        cropped_colnum = cropped_img.shape[1]
        print('cropped sample colnum: ' + str(cropped_colnum))
        cropped_rownum = cropped_img.shape[0]
        print('cropped sample rownum: ' + str(cropped_rownum))
        chamber_col = cropped_colnum // chamber_num
        print('chamber colnum: ' + str(chamber_col))
        print('chamber rownum: ' + str(cropped_rownum))
        chamber_right_boundary = 0
        chamber_index = 0

        splitted_chamber = [0] * chamber_num
        for chamber_left_boundary in range(0, cropped_colnum, chamber_col):
            if (cropped_colnum - chamber_left_boundary) < chamber_col:
                break

            chamber_right_boundary = chamber_left_boundary + chamber_col - 1
            chamber = cropped_img[:, chamber_left_boundary:chamber_right_boundary]
            splitted_chamber[chamber_index] = chamber
            chamber_index += 1

        # separate two different fluorescence
        mask = []
        for i in range(1, chamber_num + 1):
            chamber_mask = [0] * 2
            chamber_img = splitted_chamber[i - 1]
            chamber_hsv = cv2.cvtColor(chamber_img, cv2.COLOR_BGR2HSV)

            # get the orange one
            hsv_orange_lower = np.array([10, 40, 40])
            if i == 24:
                hsv_orange_upper = np.array([12, 255, 255])
            else:
                hsv_orange_upper = np.array([18, 255, 255])

            orange_mask = cv2.inRange(chamber_hsv, hsv_orange_lower, hsv_orange_upper)
            # cv2.imwrite('chamber'+str(i)+' orange'+'.tif',orange_mask)

            # get the green one
            if i == 30:
                hsv_green_lower = np.array([42, 40, 40])
            else:
                hsv_green_lower = np.array([36, 40, 35])
            hsv_green_upper = np.array([70, 255, 255])
            green_mask = cv2.inRange(chamber_hsv, hsv_green_lower, hsv_green_upper)
            # cv2.imwrite('chamber' + str(i) + ' green' + '.tif', green_mask)

            # process the orange and green mask
            kernel = np.ones((2, 2), np.uint8)

            # denoise
            orange_open = cv2.morphologyEx(orange_mask, cv2.MORPH_OPEN, kernel, iterations=1)
            green_open = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel, iterations=1)
            # cv2.imwrite('chamber' + str(i) + ' open_orange' + '.tif', orange_open)
            # cv2.imwrite('chamber' + str(i) + ' open_green' + '.tif', green_open)

            # find the background
            orange_dilation = cv2.dilate(orange_open, kernel, iterations=2)
            green_dilation = cv2.dilate(green_open, kernel, iterations=2)

            chamber_mask[0] = orange_dilation
            chamber_mask[1] = green_dilation

            mask.append(chamber_mask)

        return splitted_chamber, mask
    ########################### Graph data Management ############################
    active_chamber = 0
    # Prepare the lists for data storage
    Arguments_list = []
    Green_values_list = []
    Orange_values_list = []
    c_list = []                             # create a list of chamber names 
    for i in range(chamber_number):
        c_list.append('Chamber '+str(i+1))
        Green_values_list.append([])
        Orange_values_list.append([])
    ################################# The layout ##################################
    waiting_image = os.path.join(BASE_DIR, 'waiting.jpg')    # Load the waiting image
    user_image = Image.open(waiting_image)                    # Load the waiting image
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
        [sg.Button('Live view', size=(8, 2)), sg.Button('Graph', size=(8, 2)),sg.Button('Syringe control',size=(8,2)),sg.Button('Restart program',size=(8,2)),sg.Button('Help',size=(8,2))],
    ]

    layout = [[sg.Column(leftcol,expand_x=True), sg.Column(imgcol, key='-COL1-',expand_x=True), sg.Column(graphcol, visible=False, key='-COL2-',expand_x=True)]]
    ################################# Plot setup #########################################

    # Define the plotting function

    def create_plot(plotarguments,plotvalues1,plotvalues2):
        plt.figure(figsize=(14,9))
        plt.plot(plotarguments, plotvalues1, color='green',marker = 'o')
        plt.plot(plotarguments, plotvalues2, color='orange',marker = 'o')
        plt.title('Number of yeast cells in time',fontsize=20)
        plt.xlabel('Time [min]',fontsize=20)
        plt.ylabel('Number of cells', fontsize=20)
        plt.grid(True)
        return plt.gcf()
    # Define drawing a figure 

    def draw_figure(canvas,figure):
        figure_canvas_agg = FigureCanvasTkAgg(figure,canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top',fill='both',expand=1)
        return figure_canvas_agg

    # Define clearing a canvas
    def clear_canvas(canvas, figure_canvas_agg):
        # Clear the figure
        figure_canvas_agg.get_tk_widget().destroy()
        plt.close('all')
    ###################### Splitting image thread ################################
    stop_event = threading.Event()
    error = False
    new_image = False
    def split_image(stop_event):
        while not stop_event.is_set():
            log(f'[Splitting thread]: Asking for the image. Time is {datetime.now().time()}')
            try:
                user_image_full = Image.open(imgask())
                log(f'[Splitting thread]: Received the image from the server. Time is {datetime.now().time()}.') 
                width, height = user_image_full.size
                log(f'[Splitting thread]: Size: >> {width}x{height}')                                   
                user_image_cropped = user_image_full.crop((2517, 546, width - 3039, height - 500))   # Crop the image in order: left, top, right, bottom   
                width, height = user_image_cropped.size                                 # Get the size of the image
                small_width = width // chamber_number                                   # Define the width of each smaller image
                small_images = []
                for i in range(chamber_number):         # Loop over the width of the image in increments of small_width
                    small_image = user_image_cropped.crop((i*small_width, 0, (i + 1) * small_width, height))   # Crop the current small image 
                    small_images.append(small_image)                                    # Append the small image to the list of small images
                small_images_queue.put(small_images)                                    # Put the list of small images in the queue
                global new_image 
                new_image = True
                log('[Splitting thread]: Sent the image to the queue')
            except Exception as e:
                global error
                error = True
                log(f'[Splitting thread]: Failed to load the image: {e}')
                stop_event.set()
                break
    split_image_thread = threading.Thread(target=split_image,args=(stop_event,))
    small_images_queue = queue.Queue()
    split_image_thread.start()
    ###################### Counting cells thread ################################
    counting_index = 0 
    def counting_cells_loop(stop_event):
        while not stop_event.is_set():
            time.sleep(counting_interval)
            if not stop_event.is_set():
                log(f'[Counting thread]: Trying to count cells in all chambers')   # try to count the cells
                # Save the current image as a tif file.
                global counting_index
                try: 
                    full_image = Image.open(imgask())
                    whole_image_tif_path = os.path.join(image_files_folder,f'whole_image{counting_index}.tif') # Create a path for the whole image tif file
                    full_image.save(whole_image_tif_path)
                    [splitted_chamber,mask]=sample_read(whole_image_tif_path,chamber_number)
                    for i in range(chamber_number):
                        [cell_numbers,area_list,chamber_img] = cell_counting(i+1,mask,splitted_chamber)
                        log(f'Counted cells in chamber {i+1}, green: {cell_numbers[0]}, orange: {cell_numbers[1]}')
                        Green_values_list[i].append(cell_numbers[0])
                        Orange_values_list[i].append(cell_numbers[1])
                    Arguments_list.append((round((time.time() - start)/60,2))) # append the time (in mins) to the arguments list
                    log(f'[Counting thread]: Green values list: {Green_values_list}')
                    log(f'[Counting thread]: Green values list size:\n[Counting thread]: First dimension: {len(Green_values_list)} \n[Counting thread]: Second dimension: {len(Green_values_list[0])} \n')
                    log(f'[Counting thread]: Orange values list: {Orange_values_list} ')
                    log(f'[Counting thread]: Orange values list size: \n[Counting thread]: First dimension: {len(Orange_values_list)} \n[Counting thread]: Second dimension: {len(Orange_values_list[0])} \n')
                    log(f'[Counting thread]: Arguments list: {Arguments_list}')
                    log(f'[Counting thread]: Arguments list size: {len(Arguments_list)}')
                    counting_index += 1
                except:
                    global error
                    error = True
                    log('[Counting thread]: Counting thread failed to load the image')
                    #sg.popup('Failed to receive the image from the server. Please restart the program.')
                    stop_event.set()
                    break
    counting_cells_thread = threading.Thread(target=counting_cells_loop,args=(stop_event,))
    counting_cells_thread.start()
    ################################# The main loop ###################################
    graphing = False
    bio = io.BytesIO()
    window = sg.Window('Yeasy', layout, return_keyboard_events=True,size=(1920,1080),location=(0, 0), use_default_focus=True, finalize=True,keep_on_top=False,resizable=True).Finalize()
    window['-COL2-'].expand(expand_x=True, expand_y=True, expand_row=False)
    window['chamber_info_plt'].update(visible=False)
    window.Maximize()

    while True:
        event, values = window.read(timeout=100)                    # read the form, set the timeout in miliseconds
        if event == sg.TIMEOUT_EVENT and new_image and not graphing:          # if user doesn't do anything, update the image
            log('Processing new image...')
            new_image = False
            small_images = small_images_queue.get()
            user_image = ImageTk.PhotoImage(small_images[active_chamber])
            image_elem.update(data=user_image)
            log('Loaded new image!')
        elif event == 'Live view' and graphing:                   # the live view button returns to the live view if graphing                                        
            graphing = False
            clear_canvas(window['-CANVAS-'].TKCanvas,figure_canvas) # clear the canvas
            window['-COL2-'].update(visible=False)                  # make the canvas column invisible
            window['-COL1-'].update(visible=True)                   # show the image column
            window['chamber_info_plt'].update(visible=False)        # make the graph info invisible
            window.Maximize()                                       # maximise the window
            window['-COL1-'].expand(expand_x=True, expand_y=True, expand_row=False) # expand the image column
        elif event == sg.WIN_CLOSED:          # if the window closes - break the loop
            break
        elif event == 'Graph':                                              # the graph button opens the graph    
            graphing = True
            if 'figure_canvas' in globals():
                clear_canvas(window['-CANVAS-'].TKCanvas,figure_canvas)
            window['-COL1-'].update(visible=False)
            window['-COL2-'].update(visible=True)
            window['chamber_info_plt'].update(visible=True)
            figure_canvas = draw_figure(window['-CANVAS-'].TKCanvas,create_plot(Arguments_list,Green_values_list[active_chamber],Orange_values_list[active_chamber]))
            window.Maximize()
            window['-COL2-'].expand(expand_x=True, expand_y=True, expand_row=False)
        elif event == 'listbox':                                            # something from the list of chambers
            active_chamber = c_list.index(values["listbox"][0])             # change the active chamber
            log(f'Changed active chamber to {active_chamber+1}')            # log the change
            if graphing:
                clear_canvas(window['-CANVAS-'].TKCanvas,figure_canvas)
                figure_canvas = draw_figure(window['-CANVAS-'].TKCanvas,create_plot(Arguments_list,Green_values_list[active_chamber],Orange_values_list[active_chamber]))
                window.Maximize()
        elif event =='Syringe control':                                     # if the user clicks on the syringe control button
            syr_win_1 = syringewindow1()                                    # open the first syringe control window
            if syr_win_1 != []:
                syr_win_2 = syringewindow2(syr_win_1[0],syr_win_1[1],syringe_number)        # open the second syringe control window
                log(f'The user passed syringe control: {syringe_operation(syr_win_2)}')     # log the operation of the syringes
                if syringe_operation(syr_win_2) != ('None',0,0,0,0,0):                      # if the user actually selected something
                    send_syringe_control(syr_win_2)                        # send the operation to the server
        elif event == 'Help':                                              # if the user clicks on the help button
            sg.popup('If you can\'t see the images from the microscope, click Restart Program and make sure that you have provided the correct IP address for the server. \n \n Choose the chamber you wish to see using the list on the left. \n \n If you want to see the graph of the number of cells in a chamber, click on the Graph button. \n \n If you want to control the syringes, click on the Syringe control button. \n \n If you want to change the settings, click on the Restart program button. \n \n If you want to close the program, click on the X in the top right corner of the window.')
        elif event == 'Restart program':                         # if the user clicks on the return to the setup window button
            break
        if not graphing and not error:      
            chamber_info_img.update('Live video feed from Chamber {}'.format(active_chamber+1)) 
        elif graphing: 
            chamber_info_plt.update('Graph of data from Chamber {}'.format(active_chamber+1))
        elif error:
            error_popup = sg.popup_yes_no('The connection to the server was lost. Would you like to restart the program?')
            if error_popup == 'Yes':
                event = 'Restart program'
                break
            else:
                error = False
                stop_event.clear()
                split_image_thread = threading.Thread(target=split_image,args=(stop_event,))
                split_image_thread.start()
                counting_cells_thread = threading.Thread(target=counting_cells_loop,args=(stop_event,))
                counting_cells_thread.start()
    window.close()
    stop_event.set()
    if event != 'Restart program':
        break