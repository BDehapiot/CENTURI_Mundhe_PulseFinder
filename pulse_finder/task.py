#%% Imports

import numpy as np
from skimage import io

from functions import get_cell_data

#%% Inputs

DATA_PATH = '../data/'
FOLD_NAME = 'ecadgfp_sqhmch_200820_e4_controlforhkbfog'
CROP_Y = 250; CROP_X = 400

#%% Initialize

# Create paths
myoii_path = f'{DATA_PATH}/{FOLD_NAME}/{FOLD_NAME}_MyoII_MAX.tif'
labels_path = f'{DATA_PATH}/{FOLD_NAME}/{FOLD_NAME}_cell_tracks.tif'
pulse_data_path = f'{DATA_PATH}/{FOLD_NAME}/pulse_data.csv'
cell_info_path = f'{DATA_PATH}/{FOLD_NAME}/cell_info'

# Open data
myoii = io.imread(myoii_path) 
labels = io.imread(labels_path)  

# Get unique cell id
all_id = np.arange(1, np.max(labels)+1) # works with continuous labels

#%% Extract cell data

cell_data = get_cell_data(
    myoii, labels, cell_info_path, all_id, CROP_Y, CROP_X, parallel=True
    ) 

#%% Show data widget

from widget_new import display_cell_data

pulse_data, pulse_string, test = display_cell_data(
    cell_data, all_id, myoii, pulse_data_path
    )  

#%%

# print('\n'.join(string for string in pulse_string))

test = len(pulse_string)

for i, string in enumerate(pulse_string):

    if (i % 2) == 0:
        line_string = string
    else:
        line_string += ' ' + string
        
    if i < 2:
        full_string = line_string
    else:    
        full_string = (full_string + '\n' + line_string)
        
    
    # if ((i % 2) == 0) and (i < len(pulse_string)):
    #     pass
    # else:
    #     full_string = (full_string + '\n' + line_string)    

    # if (i % 2) == 0:
    #     line_string = string
    # else:
    #     line_string += ' ' + string
        
    # if i < 2:
    #     full_string = line_string
    # else:
    #     full_string = (full_string + '\n' + line_string) 
    
print(full_string)

        
        
        