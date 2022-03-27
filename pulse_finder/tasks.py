#%%

import os
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

# Inspect cell_info directory
cell_info_list = os.listdir(cell_info_path)
for file_name in cell_info_list:
    if 'BGsub' in file_name:
        test = file_name.find('_') 

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

    temp_data = []    

    for t in range(nT):
        
        idx = rwhere(labels[t,...], i)
        ctrd = (idx[0].squeeze().mean(), idx[1].squeeze().mean()) 
        
        temp_data.append({
            'id' : i,
            'time_point' : t,
            'idx' : idx,
            'centroid' : ctrd
            })
        
    cell_data.append(temp_data)
    
#%%

i = 2

display = np.zeros([nT, CROP_Y, CROP_X])

for t in range(nT):
    
    centroid = cell_data[i-1][t]['centroid']
    
    if np.isnan(centroid[0]) == False:
    
        # Extract centroid & crop limits
        ctrd_y = round(centroid[0])
        ctrd_x = round(centroid[1])
        y1 = ctrd_y - CROP_Y//2
        y2 = ctrd_y + CROP_Y//2
        x1 = ctrd_x - CROP_X//2
        x2 = ctrd_x + CROP_X//2
        
        # Extract cropped data 
        myoii_crop = myoii[t,y1:y2,x1:x2]     
        labels_crop = labels[t,y1:y2,x1:x2] == i
        outline_crop = (pixconn(labels_crop, 2) < 8) * labels_crop
        
        # Plot MyoII 

        # Append display
        display[t,0:myoii_crop.shape[0],0:myoii_crop.shape[1]] = myoii_crop + outline_crop*255
        
#%%

# Display data in napari
viewer = napari.Viewer()
viewer.add_image(
    display, name="display", contrast_limits = [0, np.quantile(myoii, 0.999)])

# viewer.add_image(
#     labels, name="labels")