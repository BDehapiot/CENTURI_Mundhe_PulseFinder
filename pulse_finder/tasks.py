#%%

import napari
import numpy as np

from skimage import io
from skimage.segmentation import expand_labels

#%%

DATA_PATH = '../data/'
FOLD_NAME = 'ecadgfp_sqhmch_200820_e4_controlforhkbfog'

#%%

# Open data
myoii = io.imread(
    DATA_PATH + '/' + FOLD_NAME + '/' + FOLD_NAME + '_MyoII_MAX.tif') 
cell_tracks = io.imread(
    DATA_PATH + '/' + FOLD_NAME + '/' + FOLD_NAME + '_cell_tracks.tif')  

# Get variables
nT = myoii.shape[0]
nY = myoii.shape[1]
nX = myoii.shape[2]
 
stop

#%%

# Get unique cell_id
cell_id = np.arange(1, np.max(cell_tracks)+1) # works with continuous labels

for i in cell_id:
    cell_mask = cell_tracks[cell_tracks==i]
    
# Display data in napari
viewer = napari.Viewer()
viewer.add_image(cell_mask)   

# # Process data
# for i in range(cell_tracks.shape[0]):
#     cell_tracks[i,...] = expand_labels(cell_tracks[i,...], distance=1)

# # Display data in napari
# viewer = napari.Viewer()
# viewer.add_image(
#     myoii, name="MyoII", contrast_limits = [0, np.quantile(myoii, 0.999)])
# viewer.add_image(
#     cell_tracks, name="cell_tracks")