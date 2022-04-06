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

# 
current_cell = 1

# 
class CellViewer(napari.Viewer):
    current_cell = 1
    
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

def get_cell_data(i):

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
        
    return time, myoii_intden, area, display

#%%

# class USegWidget(widgets.Container):
    
#     def __init__(self, viewer: napari.Viewer):
        
#         super().__init__()
#         self.viewer = viewer
#         self.extend([plot_data])
#         for widget in self:
#             widget.container.bind(self)
            
#         self.merge_widget = widgets.Container() # HBox    
            
#         self.select_merge_btn = widgets.PushButton(
#             value=False, label="select pairs of labels to merge")
    
# -----------------------------------------------------------------------------

time, myoii_intden, area, display = get_cell_data(1)

# -----------------------------------------------------------------------------

fig = plt.figure()

ax1 = fig.add_subplot()
line1, = ax1.plot(time, myoii_intden, color='blue', label='MyoII')
ax1.set_xlabel('time_point')
ax1.set_ylabel('MyoII Int. Den. (A.U.)')

ax2 = ax1.twinx()
line2, = ax2.plot(time, area, color='gray', linestyle='dashed', label='area') 
ax2.set_xlabel('time_point')
ax2.set_ylabel('cell area (pixels)')  

# ax1.set_title('Cell #' + str(i) + ' MyoII & cell area')
ax1.legend(handles=[line1, line2])

p1_ti = ax1.twinx(); p1_ti.axis('off')
p1_tf = ax1.twinx(); p1_tf.axis('off')
p2_ti = ax1.twinx(); p2_ti.axis('off')
p2_tf = ax1.twinx(); p2_tf.axis('off')

# -----------------------------------------------------------------------------

@magicgui(
    pulse1_ti = {'widget_type': 'Slider', 'min': np.min(time)-1, 'max': np.max(time)},
    pulse1_tf = {'widget_type': 'Slider', 'min': np.min(time)-1, 'max': np.max(time)}, 
    pulse2_ti = {'widget_type': 'Slider', 'min': np.min(time)-1, 'max': np.max(time)},
    pulse2_tf = {'widget_type': 'Slider', 'min': np.min(time)-1, 'max': np.max(time)}, 
    auto_call = True
    )

def plot_data(
        cell_number: int,
        pulse1_ti: int,
        pulse1_tf: int,
        pulse2_ti: int,
        pulse2_tf: int
        ):

    # ------------------------------------------------------------------------- 
    
    if (cell_number == 1) or (cell_number != viewer.current_cell):
    
        viewer.current_cell = cell_number
        time, myoii_intden, area, display = get_cell_data(cell_number)
    
        line1.set_xdata(time)
        line1.set_ydata(myoii_intden)
        
        line2.set_xdata(time)
        line2.set_ydata(area)
        
        # Mettre à jour l'image

    
    # pulse1 ------------------------------------------------------------------      

    if pulse1_ti >= np.min(time): 
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
            
    # pulse2 ------------------------------------------------------------------

    if pulse2_ti >= np.min(time) and pulse2_ti >= pulse1_tf: 
        p2_ti.clear()
        p2_ti.axvline(x=pulse2_ti)
        p2_ti.text(pulse2_ti+0.25,0.77,'p2_ti',rotation=90)
        p2_ti.axis('off')
        pulse2_ti = plot_data.pulse2_ti.value
    else:
        p2_ti.clear()
        p2_ti.axis('off')
    
    if pulse2_tf >= pulse2_ti: 
        p2_tf.clear()
        p2_tf.axvline(x=pulse2_tf)
        p2_ti.text(pulse2_tf+0.25,0.77,'p2_tf',rotation=90)
        p2_tf.axis('off')
        pulse2_tf = plot_data.pulse2_tf.value
    else:
        p2_tf.clear()
        p2_tf.axis('off')    
    
    fig.canvas.draw()
    
plot_data.native.layout().addWidget(FigureCanvas(fig)) 

# -----------------------------------------------------------------------------
  
viewer = CellViewer()
viewer.current_cell = 1
viewer.add_image(display, name='Cell #' + str(i) + ' MyoII', contrast_limits = [0, np.quantile(myoii, 0.999)])
viewer.window.add_dock_widget(plot_data, area='bottom', name='widget') 