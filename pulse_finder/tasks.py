#%%

import napari
import numpy as np

from skimage import io
from skimage.segmentation import expand_labels

#%%

from tools.idx import rwhere

#%%

''' Inputs -----------------------------------------------------------------'''

DATA_PATH = '../data/'
FOLD_NAME = 'ecadgfp_sqhmch_200820_e4_controlforhkbfog'

''' Initialize -------------------------------------------------------------'''

# Open data
myoii = io.imread(
    DATA_PATH + '/' + FOLD_NAME + '/' + FOLD_NAME + '_MyoII_MAX.tif') 
cell_tracks = io.imread(
    DATA_PATH + '/' + FOLD_NAME + '/' + FOLD_NAME + '_cell_tracks.tif')  

# Get variables
nT = myoii.shape[0]
nY = myoii.shape[1]
nX = myoii.shape[2]

# Get unique cell id
cell_id = np.arange(1, np.max(cell_tracks)+1) # works with continuous labels
 
#%%

cell_data = []
for i in cell_id:
    for t in range(nT):
        idx = rwhere(cell_tracks[t,...], i)
        ctrd = (idx[0].squeeze().mean(), idx[1].squeeze().mean()) 
        cell_data[i][t] = ctrd

# # Display data in napari
# viewer = napari.Viewer()
# viewer.add_image(
#     myoii, name="MyoII", contrast_limits = [0, np.quantile(myoii, 0.999)])
# viewer.add_image(
#     cell_tracks, name="cell_tracks")