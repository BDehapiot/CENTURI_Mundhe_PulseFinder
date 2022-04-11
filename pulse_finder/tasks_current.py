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

# Define cellViewer class
class cellViewer(napari.Viewer):
    pass

#%% Functions

def _get_cell_data(cell_id):
        
    ''' General description.
    
    Parameters
    ----------           
    cell_id : np.ndarray
        Description.
        
    Returns
    -------  
    cell_data : dict
        Description.    
        
    Notes
    -----   
    
    '''
    
    cell_info_list = os.listdir(cell_info_path)
            
    for file_name in cell_info_list:
        
        if 'Cell_' + str(cell_id) + '_info' in file_name:
            
            temp_data_cell = np.loadtxt(
                cell_info_path + '/' + file_name, skiprows=1)

        if 'Cell_' + str(cell_id) + '_I_BGsub' in file_name:
            
            temp_data_myoii = np.loadtxt(
                cell_info_path + '/' + file_name, skiprows=1)  
         
    # Get variables        
    time = temp_data_cell[:,12].astype('int')
    ctrd_x = temp_data_cell[:,2].astype('int')
    ctrd_y = temp_data_cell[:,3].astype('int')
    area = temp_data_cell[:,1]
    myoii_mean = temp_data_myoii[:,1]
    myoii_intden = temp_data_myoii[:,7]
            
    # Create cell_display 
    cell_display = np.zeros([time.shape[0], CROP_Y, CROP_X]).astype('int')
    
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
        text_crop = cv2.putText(
            text_crop, text, (10,25), font, 0.5, (1,1,1), 1, cv2.LINE_AA)   
        
        # Append cell_display
        cell_display[t,0:myoii_crop.shape[0],0:myoii_crop.shape[1]] = myoii_crop + (outline_crop + text_crop)*255
            
    # Append all_data list                        
    cell_data = {
        'id' : cell_id,
        'time' : time,
        'area' : area,
        'ctrd_x' : ctrd_x,
        'ctrd_y' : ctrd_y,
        'myoii_mean' : myoii_mean,
        'myoii_intden' : myoii_intden,
        'display' : cell_display
        }  
                
    return cell_data

''' ........................................................................'''

def get_cell_data(
        myoii, labels, cell_info_path, all_id, crop_y, crop_x, parallel=True):
    
    ''' General description.
    
    Parameters
    ----------    
    myoii : np.ndarray
        Description.
        
    labels : np.ndarray
        Description.
        
    cell_info_path : str
        Description.
        
    all_id : np.ndarray
        Description.
        
    crop_y : int
        Description.
        
    crop_x : int   
        Description.
        
    parallel : bool
        Description.
        
    Returns
    -------  
    cell_data : list
        Description.    
        
    Notes
    -----   
    
    '''
        
    if parallel:
    
        # Run _get_cell_data (parallel)
        cell_data = Parallel(n_jobs=-1)(
            delayed(_get_cell_data)(
                cell_id
                )
            for cell_id in all_id
            )
        
    else:
        
        # Run _get_cell_data
        cell_data = [_get_cell_data(
                cell_id
                )
            for cell_id in all_id
            ]
        
    return cell_data

#%%    

start = time.time()
print('Get cell data')

cell_data = get_cell_data(
    myoii, labels, cell_info_path, all_id, CROP_Y, CROP_X) 

end = time.time()
print(f'  {(end - start):5.3f} s') 

cellViewer.cell_data = cell_data[0]

# -----------------------------------------------------------------------------     

cell_fig = plt.figure()

ax1 = cell_fig.add_subplot()
line1, = ax1.plot(
    cell_data[0]['time'], cell_data[0]['myoii_intden'], 
    color='blue', label='MyoII'
    )

ax1.set_xlabel('time_point')
ax1.set_ylabel('MyoII Int. Den. (A.U.)')

ax2 = ax1.twinx()
line2, = ax2.plot(
    cell_data[0]['time'], cell_data[0]['area'],
    color='gray', linestyle='dashed', label='area'
    ) 

ax2.set_xlabel('time_point')
ax2.set_ylabel('cell area (pixels)')  

ax1.set_title('Cell #' + str(1) + ' MyoII & cell area')
ax1.legend(handles=[line1, line2])

p1_ti = ax1.twinx(); p1_ti.axis('off')
p1_tf = ax1.twinx(); p1_tf.axis('off')

#%%

from qtpy.QtWidgets import QSlider

@magicgui(
    
    auto_call = True,
    
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
    
    )

def plot_data(
        pulse1_ti: int,
        pulse1_tf: int,
        cell_id: int=1
        ):        
                
    # -------------------------------------------------------------------------
       
    if cell_id != cellViewer.cell_data['id']:
        
        cellViewer.cell_data = cell_data[cell_id-1]
               
        # viewer.layers.pop(0)
                        
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
    

wdg = plot_data.Gui()        
def update_slider(cell_id):

    wdg.pulse1_ti_widget.setMaximum(np.max(cellViewer.cell_data['time']))
    
#%%

plot_data.native.layout().addWidget(FigureCanvas(cell_fig)) 

viewer = cellViewer()

# viewer.add_image(
#     cellViewer.cell_data['display'],
#     name='Cell #' + str(cellViewer.cell_data['id']) + ' MyoII',
#     contrast_limits = [0, np.quantile(myoii, 0.999)]
#     )

viewer.window.add_dock_widget(plot_data, area='bottom', name='widget') 
wdg.cell_id_changed.connect(update_slider)
