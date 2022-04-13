#%%

import os
import cv2
import time
import napari
import numpy as np

from skimage import io

from magicgui import magicgui

from joblib import Parallel, delayed 

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas

#%%

from functions import get_cell_data

#%%

# Inputs
DATA_PATH = '../data/'
FOLD_NAME = 'ecadgfp_sqhmch_200820_e4_controlforhkbfog'
CROP_Y = 250; CROP_X = 400

# Manage paths
myoii_path = DATA_PATH + '/' + FOLD_NAME + '/' + FOLD_NAME + '_MyoII_MAX.tif'
labels_path = DATA_PATH + '/' + FOLD_NAME + '/' + FOLD_NAME + '_cell_tracks.tif'
cell_info_path = DATA_PATH + '/' + FOLD_NAME + '/cell_info'

# Open data
myoii = io.imread(myoii_path) 
labels = io.imread(labels_path)  

# Get variables
nT = myoii.shape[0]
nY = myoii.shape[1]
nX = myoii.shape[2]

# Get unique cell id
all_id = np.arange(1, np.max(labels)+1) # works with continuous labels

# Define cellViewer class
class cellViewer(napari.Viewer):
    pass

#%%    

cell_data = get_cell_data(
    myoii, labels, cell_info_path, all_id, CROP_Y, CROP_X) 

cellViewer.cell_data = cell_data[0]
cellViewer.pulse_data = [None] * len(all_id)

# -----------------------------------------------------------------------------     

cell_fig = plt.figure()

ax1 = cell_fig.add_subplot()
line1, = ax1.plot(
    cell_data[0]['timepoint'], cell_data[0]['myoii_intden'], 
    color='blue', label='MyoII'
    )

ax1.set_xlabel('Timepoint')
ax1.set_ylabel('MyoII Int. Den. (A.U.)')

ax2 = ax1.twinx()
line2, = ax2.plot(
    cell_data[0]['timepoint'], cell_data[0]['area'],
    color='gray', linestyle='dashed', label='area'
    ) 

ax2.set_xlabel('Timepoint')
ax2.set_ylabel('Cell area (pixels)')  

ax1.set_title('Cell #' + str(1) + ' MyoII & cell area')
ax1.legend(handles=[line1, line2])


cstep = ax1.twinx(); cstep.axis('off')
p1_ti = ax1.twinx(); p1_ti.axis('off')
p1_tf = ax1.twinx(); p1_tf.axis('off')

#%%

@magicgui(
    
    auto_call = True,
    
    next_cell = {
        'widget_type': 'PushButton',
        'value': False, 
        'label': 'next cell'
        },
    
    pulse1_ti = {
        'widget_type': 'Slider', 
        'min': np.min(cellViewer.cell_data['timepoint'])-1, 
        'max': np.max(cellViewer.cell_data['timepoint'])
        },
    
    pulse1_tf = {
        'widget_type': 'Slider', 
        'min': np.min(cellViewer.cell_data['timepoint'])-1, 
        'max': np.max(cellViewer.cell_data['timepoint'])
        }, 

    )

def plot_data(
        next_cell: bool,
        pulse1_ti: int,
        pulse1_tf: int,
        ):        
                      
    # ------------------------------------------------------------------------- 
    
    cellViewer.current_step = viewer.dims.current_step[0] + np.min(cellViewer.cell_data['timepoint'])
    cstep.axvline(x=cellViewer.current_step) 
    
    
    # -------------------------------------------------------------------------    
    
    if pulse1_ti >= np.min(cellViewer.cell_data['timepoint']): 
        p1_ti.clear()
        p1_ti.axvline(x=pulse1_ti)
        p1_ti.text(pulse1_ti+0.25,0.77,'p1_ti',rotation=90)
        p1_ti.axis('off')
        pulse1_ti = plot_data.pulse1_ti.value
    else:
        p1_ti.clear()
        p1_ti.axis('off')
    
    if pulse1_tf >= pulse1_ti: 
        p1_tf.clear()
        p1_tf.axvline(x=pulse1_tf)
        p1_ti.text(pulse1_tf+0.25,0.77,'p1_tf',rotation=90)
        p1_tf.axis('off')
        pulse1_tf = plot_data.pulse1_tf.value
    else:
        p1_tf.clear()
        p1_tf.axis('off')
        
    cell_fig.canvas.draw()
    
    if plot_data.pulse1_ti.value > np.min(cellViewer.cell_data['timepoint'])-1:
        cellViewer.pulse_data[cellViewer.cell_data['cell_id']-1] = (
            plot_data.pulse1_ti.value, 
            plot_data.pulse1_tf.value,
            
            )

@plot_data.next_cell.changed.connect  
def update_slider():
    
    cellViewer.cell_data = cell_data[cellViewer.cell_data['cell_id']] # 
    
    # -------------------------------------------------------------------------
    
    viewer.layers.pop(0)
    viewer.add_image(
        cellViewer.cell_data['display'],
        name='Cell #' + str(cellViewer.cell_data['cell_id']) + ' MyoII',
        contrast_limits = [0, np.quantile(myoii, 0.999)]
        )
    
    # ------------------------------------------------------------------------- 
    
    line1.set_xdata(cellViewer.cell_data['timepoint'])
    line1.set_ydata(cellViewer.cell_data['myoii_intden'])
    ax1.relim()
    ax1.autoscale_view()
    
    line2.set_xdata(cellViewer.cell_data['timepoint'])
    line2.set_ydata(cellViewer.cell_data['area'])
    ax2.relim()
    ax2.autoscale_view()
    
    ax1.set_title('Cell #' + str(cellViewer.cell_data['cell_id']) + ' MyoII & cell area')

    # ------------------------------------------------------------------------- 

    plot_data.pulse1_ti.min = np.min(cellViewer.cell_data['timepoint'])-1
    plot_data.pulse1_ti.max = np.max(cellViewer.cell_data['timepoint'])
    plot_data.pulse1_ti.value = np.min(cellViewer.cell_data['timepoint'])-1
    
    plot_data.pulse1_tf.min = np.min(cellViewer.cell_data['timepoint'])-1
    plot_data.pulse1_tf.max = np.max(cellViewer.cell_data['timepoint'])
    plot_data.pulse1_tf.value = np.min(cellViewer.cell_data['timepoint'])-1

# @plot_data.next_cell.changed.connect         
    
#%%

plot_data.native.layout().addWidget(FigureCanvas(cell_fig)) 

viewer = cellViewer()

viewer.add_image(
    cellViewer.cell_data['display'],
    name='Cell #' + str(cellViewer.cell_data['cell_id']) + ' MyoII',
    contrast_limits = [0, np.quantile(myoii, 0.999)]
    )

viewer.window.add_dock_widget(plot_data, area='bottom', name='widget') 

test = cellViewer.pulse_data
