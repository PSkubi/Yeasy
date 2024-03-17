import matplotlib.pyplot as plt
import os
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
################################# Plot setup #########################################

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