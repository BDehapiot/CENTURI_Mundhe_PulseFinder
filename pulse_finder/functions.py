#%%

import os
import cv2
import time
import numpy as np

from joblib import Parallel, delayed 

#%%

from tools.conn import pixconn

#%%

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
    
    def _get_cell_data(cell_id):
        
        cell_info_list = os.listdir(cell_info_path)
                
        for file_name in cell_info_list:
            
            if 'Cell_' + str(cell_id) + '_info' in file_name:
                
                temp_data_cell = np.loadtxt(
                    cell_info_path + '/' + file_name, skiprows=1)
    
            if 'Cell_' + str(cell_id) + '_I_BGsub' in file_name:
                
                temp_data_myoii = np.loadtxt(
                    cell_info_path + '/' + file_name, skiprows=1)  
             
        # Get variables        
        time_range = temp_data_cell[:,12].astype('int')
        ctrd_x = temp_data_cell[:,2].astype('int')
        ctrd_y = temp_data_cell[:,3].astype('int')
        area = temp_data_cell[:,1]
        myoii_mean = temp_data_myoii[:,1]
        myoii_intden = temp_data_myoii[:,7]
                
        # Create cell_display 
        cell_crop = np.zeros([time_range.shape[0], crop_y, crop_x]).astype('int')
        
        for t in range(time_range.shape[0]):
        
            # Set crop limits
            y1 = ctrd_y[t] - crop_y//2
            y2 = ctrd_y[t] + crop_y//2
            x1 = ctrd_x[t] - crop_x//2
            x2 = ctrd_x[t] + crop_x//2
            
            # Crop data 
            myoii_crop = myoii[time_range[t]-1,y1:y2,x1:x2] 
            labels_crop = labels[time_range[t]-1,y1:y2,x1:x2] == cell_id
            outline_crop = (pixconn(labels_crop, 2) < 8) * labels_crop
            
            # Draw text
            font = cv2.FONT_HERSHEY_DUPLEX
            text = 'Cell #' + str(cell_id) + ' time point = ' + str(time_range[t])
            text_crop = np.zeros(outline_crop.shape)    
            text_crop = cv2.putText(
                text_crop, text, (10,25), font, 0.5, (1,1,1), 1, cv2.LINE_AA)   
            
            # Append cell_display
            cell_crop[t,0:myoii_crop.shape[0],0:myoii_crop.shape[1]] = myoii_crop + (outline_crop + text_crop)*255
                
        # Append all_data list                        
        cell_data = {
            'cell_id' : cell_id,
            'time_range' : time_range,
            'area' : area,
            'ctrd_x' : ctrd_x,
            'ctrd_y' : ctrd_y,
            'myoii_mean' : myoii_mean,
            'myoii_intden' : myoii_intden,
            'cell_crop' : cell_crop
            }  
                    
        return cell_data
    
    # -------------------------------------------------------------------------
    
    if parallel:
        
        start = time.time()
        print('get_cell_data (parallel)')
    
        # Run _get_cell_data (parallel)
        cell_data = Parallel(n_jobs=-1)(
            delayed(_get_cell_data)(
                cell_id
                )
            for cell_id in all_id
            )
        
        end = time.time()
        print(f'  {(end - start):5.3f} s')
        
    else:
        
        start = time.time()
        print('get_cell_data')
        
        # Run _get_cell_data
        cell_data = [_get_cell_data(
                cell_id
                )
            for cell_id in all_id
            ]
        
        end = time.time()
        print(f'  {(end - start):5.3f} s')
        
    return cell_data