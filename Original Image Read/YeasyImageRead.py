import PySimpleGUI as sg
import os
from PIL import Image, ImageTk
import io
import numpy as np
import matplotlib.pyplot as plt
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# I based this file on ideas from https://realpython.com/pysimplegui-python/
# A demo viewer, which I was heavily inspired by, is here https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Img_Viewer.py
# The demo images are from:
# https://youtu.be/oH3u51xyUHc?si=5aOkg8Z1Sz8A78Ek
# https://www.youtube.com/watch?v=GFEgB_ytDZY
# https://www.youtube.com/watch?v=iOvrq6ssy2Y


############################## Setup ####################################

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

fnames = [0,0,0]
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

################################# Plot setup #########################################

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

############################ Start reading data #############################

# active chamber index
active_chamber = 0

# Take the first file in the directory
filename = os.path.join(flist[0][active_chamber], fnames[active_chamber][0]) 

# Extract image data
image_elem = sg.Image(data=get_img_data(filename, first=True))

# Also get display elements. This is just for debugging (so that we can see what's going on)
chamber_info_elementimg = sg.Text(text='Live video feed from Chamber {}'.format(active_chamber+1),expand_x=True,justification='center',font=('Calibri',30))
chamber_info_elementplt = sg.Text(text='Graph of data from Chamber {}'.format(active_chamber+1),expand_x=True,justification='center',font=('Calibri',30))

# define layout, show and read the form
canvas_elem = sg.Canvas(size=(1200, 400),key='-CANVAS-',expand_x=True)
imgcol = [[chamber_info_elementimg],[image_elem]]
graphcol = [[chamber_info_elementplt],[canvas_elem]]
leftcol = [
    [sg.Listbox(values=c_list,font=('Calibri', 20), change_submits=True, size=(30, 20), key='listbox',expand_y=True)],
    [sg.Button('Live view', size=(8, 2)), sg.Button('Graph', size=(8, 2))],
]

layout = [[sg.Column(leftcol,expand_x=True), sg.Column(imgcol, key='-COL1-',expand_x=True), sg.Column(graphcol, visible=False, key='-COL2-',expand_x=True)]]

window = sg.Window('Yeasy', layout, return_keyboard_events=True,size=(1920,1080),
                   location=(0, 0), use_default_focus=False, finalize=True,keep_on_top=True)
################################# The main loop ###################################

# i is the number of the image opened
i = 0

# graphing is Bool for if a graph is currently shown or not
graphing = False

while True:
    # read the form, set the timeout in miliseconds
    event, values = window.read(timeout=100)
    #print(event, values)
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
    elif event in (sg.TIMEOUT_EVENT) and not graphing:
        i += 1
        if i >= chamber_sizes[active_chamber]:
            i -= chamber_sizes[active_chamber]
        filename = os.path.join(flist[0][active_chamber], fnames[active_chamber][i])
    
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
        filename = os.path.join(flist[0][active_chamber], fnames[active_chamber][0])  # read this file
    
    # update window with new image
    # update page display
    if not graphing:
        image_elem.update(data=get_img_data(filename, first=True))
        chamber_info_elementimg.update('Live video feed from Chamber {}'.format(active_chamber+1))
    else: 
        chamber_info_elementplt.update('Graph of data from Chamber {}'.format(active_chamber+1))
# Close the window
window.close()