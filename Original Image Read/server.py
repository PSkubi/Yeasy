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
############################## IVA PART ################################
def syringe_operation(syringecontrols):
    '''Here will be the code operating the syringe, taking the flowrate and volume/duration desired'''
    # here #
    if syringecontrols == []:
        return ('None',0,0,0,0,0)
    else:
        controltype,syringeno,flowrate,control,flowrate_units,control_units = syringecontrols
    print(f'Type: {controltype}, Syringe number: {syringeno}, Flow rate: {flowrate}{flowrate_units}, Control: {control}{control_units}')
    return (controltype,syringeno,flowrate,control,flowrate_units,control_units)
############################# END OF IVA PART ######################
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
            if 'img' in msg_info or 'str' in msg_info or 'byt' in msg_info and not msg_info == '':                                             # if the message is not empty, proceed
                msg_info = msg_info.replace(' ','')                                 # split the message info: length and type
                msg_info = msg_info.split('_')                                 # split the message info: length and type
                print(f'Received message info: {msg_info}')
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
                    #image.show()
        except UnicodeDecodeError:
            print('UnicodeDecodeError')

    conn.close()
def server_operations():
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
########################### Syringe control windows ###################################
def syringewindow():
    layout = [
        [sg.Text('Do you want to use volume or duration control?')],
        [sg.Button('Volume', size=(8, 2)),sg.Button('Duration', size=(8, 2))],
        [sg.Button('Cancel', size=(8, 2))]
    ]
    syringewindow1 = sg.Window('Control type',layout,size=(600,400))
    event, values = syringewindow1.read()
    if event == sg.WIN_CLOSED or 'Cancel':
        syringewindow1.close()
        return []
    if event=='Volume':
        syringewindow1.close()
        type = 'Volume'
        measure_units = ['µL', 'mL', 'L']
    elif event=='Duration':
        syringewindow1.close()
        type = 'Duration'
        measure_units = ['minutes','hours']
    else:
        type = 'Close :)'
    flowrate_units = ['µL/min', 'mL/min', 'µL/hr', 'mL/hr']
    layout = [
        [sg.Text(f'You have chosen {type} control')],
        [[sg.Text('Syringe number:')],[sg.Input('',size=(10, 4),key='-Syringe no-')]],
        [[sg.Text('Flow rate:')],[sg.Input('',size=(10, 4),key='-Flow rate-'),sg.Combo(flowrate_units, font=('Arial Bold', 12),key='-Flowrate units-')]],#sg.Text('L/min')]],
        [[sg.Text(f'{type}:')],[sg.Input('', size=(10, 4),key ='-Control-'),sg.Combo(measure_units, font=('Arial Bold', 12),key='-Control units-')]],
        [sg.Button('Cancel', size=(8, 2)),sg.Button('Confirm',size=(8,2))]
    ]
    syringewindow2= sg.Window(f'Flow rate and {type} control',layout,size=(600,400))
    event, values = syringewindow2.read()
    if event == 'Cancel':
        syringewindow2.close()
        return []
    elif event in ('Confirm'):
        userinput = [type,int(values['-Syringe no-']),float(values['-Flow rate-']),float(values['-Control-']),str(values['-Flowrate units-']),str(values['-Control units-'])]
        syringewindow2.close()
        return userinput
################################# Plot setup #########################################
# Start with identifying the directory and folders within it
folder =os.path.dirname(os.path.realpath(__file__))
flist = [0,0]
flist[0] = [x[0] for x in os.walk(folder)]
flist[1] = [x[1] for x in os.walk(folder)][0]
flist[0].pop(0)
# Read the last folder to get the data - arguments file and values file

data_flist = [f[2] for f in os.walk(flist[0][-1])][0]
ArgumentsFile = os.path.join(flist[0][-1],data_flist[0])
ValuesFile = os.path.join(flist[0][-1],data_flist[1])

# Use csv reader to read the numerical data from those two files

with open(ArgumentsFile, 'r') as file:
    plotarguments = next(csv.reader(file))
plotarguments = [int(x) for x in plotarguments]

with open(ValuesFile, 'r') as file:
    plotvalues = next(csv.reader(file))
plotvalues = [int(y) for y in plotvalues]

# Define the plotting function

def create_plot(plotarguments,plotvalues):
    plt.figure(figsize=(14,9))
    plt.plot(plotarguments, plotvalues, color='purple',marker = 'o')
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
filename = os.path.join(os.getcwd(), 'Original Image Read\\waiting.jpg')
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

print("Server is starting...")
#start()
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
window = sg.Window('Yeasy', layout, return_keyboard_events=True,size=(1920,1080),location=(0, 0), use_default_focus=False, finalize=True,keep_on_top=False)
window.maximize()
while True:
    # read the form, set the timeout in miliseconds
    event, values = window.read(timeout=500)
    # if the window closes - break the loop
    if event == sg.WIN_CLOSED:
        break
    elif event in ('Live view'):
        if not graphing:
            pass
        else:
            graphing = False
            clear_canvas(window['-CANVAS-'].TKCanvas,figure_canvas)
            window['-COL2-'].update(visible=False)
            window['-COL1-'].update(visible=True)
            window.maximize()
            window['-COL1-'].expand(expand_x=True, expand_y=True, expand_row=False)
    #this statement will show the graph
    elif event == 'Graph':
        graphing = True
        window[f'-COL1-'].update(visible=False)
        window[f'-COL2-'].update(visible=True)
        figure_canvas = draw_figure(window['-CANVAS-'].TKCanvas,create_plot(plotarguments,plotvalues))
        window.maximize()
        window['-COL2-'].expand(expand_x=True, expand_y=True, expand_row=False)
    # elif event == 'listbox':            # something from the listbox
    #     active_chamber = c_list.index(values["listbox"][0])            # selected filename
    #     filename = os.path.join(flist[0][active_chamber], fnames[active_chamber][0])  # read this file
    elif event =='Syringe control':
        syringecontrols = syringewindow()
        syringe_operation(syringecontrols)
        
    # update window with new image
    # update page display
    if not graphing:
        if not image == None:
            bio = io.BytesIO()
            image.save(bio, format='PNG')
            image_elem.update(data=bio.getvalue())
    #     chamber_info_elementimg.update('Live video feed from Chamber {}'.format(active_chamber+1))
    # else: 
    #     chamber_info_elementplt.update('Graph of data from Chamber {}'.format(active_chamber+1))
# Close the window
window.close()