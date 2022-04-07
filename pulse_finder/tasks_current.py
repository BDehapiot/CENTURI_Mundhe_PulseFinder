#%%

import os
import cv2
import numpy as np

from skimage import io

import napari
from magicgui import magicgui

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas

#%%

from tools.idx import rwhere
from tools.conn import pixconn

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

#%%

def get_all_data(myoii, labels, cell_info_path, all_id, crop_y, crop_x):
    
    all_data = []
    cell_info_list = os.listdir(cell_info_path)
    
    for cell_id in all_id:
        
        for file_name in cell_info_list:
            
            if 'Cell_' + str(cell_id) + '_info' in file_name:
                
                temp_data_cell = np.loadtxt(
                    cell_info_path + '/' + file_name, skiprows=1)
    
            if 'Cell_' + str(cell_id) + '_I_BGsub' in file_name:
                
                temp_data_myoii = np.loadtxt(
                    cell_info_path + '/' + file_name, skiprows=1)  
                
        'id' : cell_id,
        'time' : temp_data_cell[:,12],
        'area' : temp_data_cell[:,1],
        'ctrd_x' : temp_data_cell[:,2],
        'ctrd_y' : temp_data_cell[:,3],
        'myoii_mean' : temp_data_myoii[:,1],
        'myoii_intden' : temp_data_myoii[:,7]
                
        # Create cell_display 
        cell_display = np.zeros([time.shape[0], CROP_Y, CROP_X])
        
        for t in range(time.shape[0]):
        
            # Set crop limits
            y1 = ctrd_y[t] - CROP_Y//2
            y2 = ctrd_y[t] + CROP_Y//2
            x1 = ctrd_x[t] - CROP_X//2
            x2 = ctrd_x[t] + CROP_X//2
            
            # Crop data 
            myoii_crop = myoii[time[t]-1,y1:y2,x1:x2]     
            labels_crop = labels[time[t]-1,y1:y2,x1:x2] == cell_id
            outline_crop = (pixconn(labels_crop, 2) < 8) * labels_crop
            
            # Draw text
            font = cv2.FONT_HERSHEY_DUPLEX
            text = 'Cell #' + str(cell_id) + ' Time = ' + str(time[t])
            text_crop = np.zeros(outline_crop.shape)    
            text_crop = cv2.putText(text_crop, text, (10,25), font, 0.5, (1,1,1), 1, cv2.LINE_AA)   
            
            # Append cell_display
            cell_display[t,0:myoii_crop.shape[0],0:myoii_crop.shape[1]] = myoii_crop + (outline_crop + text_crop)*255
                
        # Append all_data list                        
        all_data.append({
            'id' : cell_id,
            'time' : temp_data_cell[:,12],
            'area' : temp_data_cell[:,1],
            'ctrd_x' : temp_data_cell[:,2],
            'ctrd_y' : temp_data_cell[:,3],
            'myoii_mean' : temp_data_myoii[:,1],
            'myoii_intden' : temp_data_myoii[:,7]
            })  
                
    return all_data

all_data = get_all_data(myoii, labels, cell_info_path, all_id, CROP_Y, CROP_X)
    
stop        

#%% Functions

def get_cell_data(cell_info_path, all_id, cell_id):
    
    cell_data = []

    # Extract existing data from cell_info folder
    for file_name in cell_info_list:
        
        if 'Cell_' + str(cell_id) + '_info' in file_name:
            
            temp_data_cell = np.loadtxt(
                cell_info_path + '/' + file_name, skiprows=1)

        if 'Cell_' + str(cell_id) + '_I_BGsub' in file_name:
            
            temp_data_myoii = np.loadtxt(
                cell_info_path + '/' + file_name, skiprows=1)
    
    # Fill cell_data 
    cell_data = {
        'cell_id' : cell_id,
        'time' : temp_data_cell[:,12].astype('int'),
        'ctrd_x' : temp_data_cell[:,2].astype('int'),
        'ctrd_y' : temp_data_cell[:,3].astype('int'),
        'area' : temp_data_cell[:,1],
        'myoii_mean' : temp_data_myoii[:,1],
        'myoii_intden' : temp_data_myoii[:,7]
        } 
    
    return cell_data

# -----------------------------------------------------------------------------

def get_cell_display(myoii, labels, cell_data, crop_y, crop_x, cell_id):
    
    # Extract variables from cell_data
    time = cell_data['time']
    ctrd_x = cell_data['ctrd_x']
    ctrd_y = cell_data['ctrd_y']
    
    # Create cell_display 
    cell_display = np.zeros([time.shape[0], CROP_Y, CROP_X])
    
    for t in range(time.shape[0]):
    
        # Set crop limits
        y1 = ctrd_y[t] - CROP_Y//2
        y2 = ctrd_y[t] + CROP_Y//2
        x1 = ctrd_x[t] - CROP_X//2
        x2 = ctrd_x[t] + CROP_X//2
        
        # Crop data 
        myoii_crop = myoii[time[t]-1,y1:y2,x1:x2]     
        labels_crop = labels[time[t]-1,y1:y2,x1:x2] == cell_id
        outline_crop = (pixconn(labels_crop, 2) < 8) * labels_crop
        
        # Draw text
        font = cv2.FONT_HERSHEY_DUPLEX
        text = 'Cell #' + str(cell_id) + ' Time = ' + str(time[t])
        text_crop = np.zeros(outline_crop.shape)    
        text_crop = cv2.putText(text_crop, text, (10,25), font, 0.5, (1,1,1), 1, cv2.LINE_AA)   
        
        # Append cell_display
        cell_display[t,0:myoii_crop.shape[0],0:myoii_crop.shape[1]] = myoii_crop + (outline_crop + text_crop)*255
        
    return cell_display
        
# -----------------------------------------------------------------------------
    
def get_cell_fig(cell_data, cell_id):
    
    # Extract variables from cell_data
    time = cell_data['time']
    myoii_intden = cell_data['myoii_intden']
    area = cell_data['area']

    cell_fig = plt.figure()

    ax1 = cell_fig.add_subplot()
    
    line1, = ax1.plot(
        time, myoii_intden, 
        color='blue', label='MyoII'
        )
    
    ax1.set_xlabel('time_point')
    ax1.set_ylabel('MyoII Int. Den. (A.U.)')

    ax2 = ax1.twinx()
    
    line2, = ax2.plot(
        time, area,
        color='gray', linestyle='dashed', label='area'
        ) 
    
    ax2.set_xlabel('time_point')
    ax2.set_ylabel('cell area (pixels)')  

    ax1.set_title('Cell #' + str(cell_id) + ' MyoII & cell area')
    ax1.legend(handles=[line1, line2])

    p1_ti = ax1.twinx(); p1_ti.axis('off')
    p1_tf = ax1.twinx(); p1_tf.axis('off') 
    
    return cell_fig, ax1, ax2, line1, line2, p1_ti, p1_tf
    
#%%    

class cellViewer(napari.Viewer):
    pass
      
cellViewer.cell_data = get_cell_data(cell_info_path, all_id, 1)
cellViewer.cell_display = get_cell_display(myoii, labels, cellViewer.cell_data, CROP_Y, CROP_X, 1)

# cell_data = get_cell_data(cell_info_path, all_id, 1)
# cell_display = get_cell_display(myoii, labels, cellViewer.cell_data, CROP_Y, CROP_X, 1)
cell_fig, ax1, ax2, line1, line2, p1_ti, p1_tf = get_cell_fig(cellViewer.cell_data, 1)

@magicgui(
    pulse1_ti = {
        'widget_type': 'Slider', 
        'min': np.min(cellViewer.cell_data['time'])-1, 
        'max': np.max(cellViewer.cell_data['time'])
        },
    pulse1_tf = {
        'widget_type': 'Slider', 
        'min': np.min(cellViewer.cell_data['time'])-1, 
        'max': np.max(cellViewer.cell_data['time'])
        }, 
    auto_call = True
    )

def plot_data(
        pulse1_ti: int,
        pulse1_tf: int,
        cell_id: int=1
        ):        
                
    # -------------------------------------------------------------------------
    
    if cellViewer.cell_data['cell_id'] != cell_id:
        
        cellViewer.cell_data = get_cell_data(cell_info_path, all_id, cell_id)
        cellViewer.cell_display = get_cell_display(myoii, labels, cellViewer.cell_data, CROP_Y, CROP_X, cell_id)
                
        line1.set_xdata(cellViewer.cell_data['time'])
        line1.set_ydata(cellViewer.cell_data['myoii_intden'])
        ax1.relim()
        ax1.autoscale_view()
        
        line2.set_xdata(cellViewer.cell_data['time'])
        line2.set_ydata(cellViewer.cell_data['area'])
        ax2.relim()
        ax2.autoscale_view()
        
    # -------------------------------------------------------------------------    
    
    if pulse1_ti >= np.min(cellViewer.cell_data['time']): 
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
    
#%%

plot_data.native.layout().addWidget(FigureCanvas(cell_fig)) 

viewer = cellViewer()
viewer.add_image(cellViewer.cell_display, name='Cell #' + str(1) + ' MyoII', contrast_limits = [0, np.quantile(myoii, 0.999)])
viewer.window.add_dock_widget(plot_data, area='bottom', name='widget') 
