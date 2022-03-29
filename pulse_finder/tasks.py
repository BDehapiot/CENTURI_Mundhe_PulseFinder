#%%

import re
import os
import cv2
import napari
import numpy as np

import matplotlib.pyplot as plt

from skimage import io

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
        'myoii_iden' : temp_data_myoii[:,7]
        })
    
#%%

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure

i = 2

# Extract cell_data 
time = cell_data[i-1]['time'].astype('int')
ctrd_x = cell_data[i-1]['ctrd_x'].astype('int')
ctrd_y = cell_data[i-1]['ctrd_y'].astype('int')
myoii_mean = cell_data[i-1]['myoii_mean']
myoii_iden = cell_data[i-1]['myoii_iden']

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
    
    # Append display
    display[t,0:myoii_crop.shape[0],0:myoii_crop.shape[1]] = myoii_crop + outline_crop*255

# Display data in napari
with napari.gui_qt():

    static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
    axes = static_canvas.figure.subplots()
    axes.plot(time, myoii_iden)
    
    viewer = napari.view_image(display, name="display", contrast_limits = [0, np.quantile(myoii, 0.999)])
    viewer.window.add_dock_widget(static_canvas, area='bottom', name='matplotlib figure') 

# viewer = napari.Viewer()
# viewer.add_image(
#     display, name="display", contrast_limits = [0, np.quantile(myoii, 0.999)])    

# # Plot MyoII IntDen
# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.set_xlabel("time")
# ax.set_ylabel("MyoII IntDen")
# ax.plot(time, myoii_iden, label="MyoII IntDen")
# ax.legend()
# ax.set_title("MyoII IntDen")

# with napari.gui_qt():
#     viewer = napari.view_image(myoii[0,...])   
#     static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
#     axes = static_canvas.figure.subplots()
#     axes.plot(myoii_iden)
#     viewer.window.add_dock_widget(static_canvas, area='bottom', name='matplotlib figure') 

# for t in range(nT):
    
#     centroid = cell_data[i-1][t]['centroid']
    
#     if np.isnan(centroid[0]) == False:
    
#         # Extract centroid & crop limits
#         ctrd_y = round(centroid[0])
#         ctrd_x = round(centroid[1])
#         y1 = ctrd_y - CROP_Y//2
#         y2 = ctrd_y + CROP_Y//2
#         x1 = ctrd_x - CROP_X//2
#         x2 = ctrd_x + CROP_X//2
        
#         # Extract cropped data 
#         myoii_crop = myoii[t,y1:y2,x1:x2]     
#         labels_crop = labels[t,y1:y2,x1:x2] == i
#         outline_crop = (pixconn(labels_crop, 2) < 8) * labels_crop
        
#         # Plot MyoII 

#         # Append display
#         display[t,0:myoii_crop.shape[0],0:myoii_crop.shape[1]] = myoii_crop + outline_crop*255
        
#%%

# # Display data in napari
# viewer = napari.Viewer()
# viewer.add_image(
#     display, name="display", contrast_limits = [0, np.quantile(myoii, 0.999)])

# viewer.add_image(
#     labels, name="labels")