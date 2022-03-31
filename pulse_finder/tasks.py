#%%

import os
import cv2
import numpy as np

from skimage import io
from skimage.filters import gaussian

import napari
from magicgui import magicgui

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
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
cell_info_list = os.listdir(cell_info_path)

# Open data
myoii = io.imread(myoii_path) 
labels = io.imread(labels_path)  

# Get variables
nT = myoii.shape[0]
nY = myoii.shape[1]
nX = myoii.shape[2]

# Get unique cell id
cell_id = np.arange(1, np.max(labels)+1) # works with continuous labels
 
#%% Extract cell_data

cell_data = []  
  
for i in cell_id:  

    # Extract existing data from cell_info folder
    for file_name in cell_info_list:
        
        if 'Cell_' + str(i) + '_info' in file_name:
            
            temp_data_cell = np.loadtxt(
                cell_info_path + '/' + file_name, skiprows=1)

        if 'Cell_' + str(i) + '_I_BGsub' in file_name:
            
            temp_data_myoii = np.loadtxt(
                cell_info_path + '/' + file_name, skiprows=1)
    
    # Append cell_data list                        
    cell_data.append({
        'time' : temp_data_cell[:,12],
        'area' : temp_data_cell[:,1],
        'ctrd_x' : temp_data_cell[:,2],
        'ctrd_y' : temp_data_cell[:,3],
        'myoii_mean' : temp_data_myoii[:,1],
        'myoii_intden' : temp_data_myoii[:,7]
        })
    
#%%

# i = 5

# # Extract cell_data 
# time = cell_data[i-1]['time'].astype('int')
# ctrd_x = cell_data[i-1]['ctrd_x'].astype('int')
# ctrd_y = cell_data[i-1]['ctrd_y'].astype('int')
# myoii_mean = cell_data[i-1]['myoii_mean']
# myoii_intden = cell_data[i-1]['myoii_intden']
# area = cell_data[i-1]['area']

# # Create empty display 
# display = np.zeros([time.shape[0], CROP_Y, CROP_X])

# for t in range(time.shape[0]):

#     # Set crop limits
#     y1 = ctrd_y[t] - CROP_Y//2
#     y2 = ctrd_y[t] + CROP_Y//2
#     x1 = ctrd_x[t] - CROP_X//2
#     x2 = ctrd_x[t] + CROP_X//2
    
#     # Crop data 
#     myoii_crop = myoii[time[t]-1,y1:y2,x1:x2]     
#     labels_crop = labels[time[t]-1,y1:y2,x1:x2] == i
#     outline_crop = (pixconn(labels_crop, 2) < 8) * labels_crop
    
#     # Draw text
#     font = cv2.FONT_HERSHEY_DUPLEX
#     text = 'Cell #' + str(i) + ' Time = ' + str(time[t])
#     text_crop = np.zeros(outline_crop.shape)    
#     text_crop = cv2.putText(text_crop, text, (10,25), font, 0.5, (1,1,1), 1, cv2.LINE_AA)   
    
#     # Append display
#     display[t,0:myoii_crop.shape[0],0:myoii_crop.shape[1]] = myoii_crop + (outline_crop + text_crop)*255

# # Show results in napari viewer
# with napari.gui_qt():

#     # Plot data
#     static_canvas = FigureCanvas(Figure(figsize=(5, 5)))
    
#     ax1 = static_canvas.figure.subplots()    
#     line1, = ax1.plot(time, myoii_intden, color='blue', label='MyoII')
#     ax1.axvline(x=60)
#     ax1.set_xlabel('time_point')
#     ax1.set_ylabel('MyoII Int. Den. (A.U.)')
    
#     ax2 = ax1.twinx()    
#     line2, = ax2.plot(time, area, color='gray', linestyle='dashed', label='area')
#     ax2.set_xlabel('time_point')
#     ax2.set_ylabel('cell area (pixels)')    
    
#     ax1.set_title('Cell #' + str(i) + ' MyoII & cell area')
#     ax1.legend(handles=[line1, line2])
    
#     # Add to napari viewer
    
#     @magicgui(
#         auto_call=True,
#         call_button="select pulse(s)")
    
#     def select_pulses(
#             data: napari.types.ImageData, 
#             pulse1_ti: int = None,
#             pulse1_tf: int = None,
#             pulse2_ti: int = None,
#             pulse2_tf: int = None,
#             pulse3_ti: int = None,
#             pulse3_tf: int = None,
#             pulse4_ti: int = None,
#             pulse4_tf: int = None
#         ) -> napari.types.ImageData:
#         return data
    
#     viewer = napari.Viewer()
#     viewer.add_image(display, name='Cell #' + str(i) + ' MyoII', contrast_limits = [0, np.quantile(myoii, 0.999)])
#     viewer.window.add_dock_widget(static_canvas, area='bottom', name='plot')
#     viewer.window.add_dock_widget(select_pulses, area='right', name='widget')  
        
#%%

i = 5

# Extract cell_data 
time = cell_data[i-1]['time'].astype('int')
ctrd_x = cell_data[i-1]['ctrd_x'].astype('int')
ctrd_y = cell_data[i-1]['ctrd_y'].astype('int')
myoii_mean = cell_data[i-1]['myoii_mean']
myoii_intden = cell_data[i-1]['myoii_intden']
area = cell_data[i-1]['area']

# Create empty display 
display = np.zeros([time.shape[0], CROP_Y, CROP_X])

for t in range(time.shape[0]):

    # Set crop limits
    y1 = ctrd_y[t] - CROP_Y//2
    y2 = ctrd_y[t] + CROP_Y//2
    x1 = ctrd_x[t] - CROP_X//2
    x2 = ctrd_x[t] + CROP_X//2
    
    # Crop data 
    myoii_crop = myoii[time[t]-1,y1:y2,x1:x2]     
    labels_crop = labels[time[t]-1,y1:y2,x1:x2] == i
    outline_crop = (pixconn(labels_crop, 2) < 8) * labels_crop
    
    # Draw text
    font = cv2.FONT_HERSHEY_DUPLEX
    text = 'Cell #' + str(i) + ' Time = ' + str(time[t])
    text_crop = np.zeros(outline_crop.shape)    
    text_crop = cv2.putText(text_crop, text, (10,25), font, 0.5, (1,1,1), 1, cv2.LINE_AA)   
    
    # Append display
    display[t,0:myoii_crop.shape[0],0:myoii_crop.shape[1]] = myoii_crop + (outline_crop + text_crop)*255
   
    # Add to napari viewer
    
@magicgui(
    auto_call=True,
    call_button="select pulse(s)")

def select_pulses( 
        pulse1_ti: int = None,
        pulse1_tf: int = None,
        pulse2_ti: int = None,
        pulse2_tf: int = None,
        pulse3_ti: int = None,
        pulse3_tf: int = None,
        pulse4_ti: int = None,
        pulse4_tf: int = None
    ) -> napari.types.ImageData:
    
    # Show results in napari viewer
    with napari.gui_qt():

        # Plot data
        static_canvas = FigureCanvas(Figure(figsize=(5, 5)))
        
        ax1 = static_canvas.figure.subplots()    
        line1, = ax1.plot(time, myoii_intden, color='blue', label='MyoII')
        ax1.axvline(x=60)
        ax1.set_xlabel('time_point')
        ax1.set_ylabel('MyoII Int. Den. (A.U.)')
        
        ax2 = ax1.twinx()    
        line2, = ax2.plot(time, area, color='gray', linestyle='dashed', label='area')
        ax2.set_xlabel('time_point')
        ax2.set_ylabel('cell area (pixels)')    
        
        ax1.set_title('Cell #' + str(i) + ' MyoII & cell area')
        ax1.legend(handles=[line1, line2])
    
    return static_canvas
    
viewer = napari.Viewer()
viewer.add_image(display, name='Cell #' + str(i) + ' MyoII', contrast_limits = [0, np.quantile(myoii, 0.999)])
viewer.window.add_dock_widget(static_canvas, area='bottom', name='plot')
viewer.window.add_dock_widget(select_pulses, area='right', name='widget')  