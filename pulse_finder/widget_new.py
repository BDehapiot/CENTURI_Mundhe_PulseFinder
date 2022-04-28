#%% Imports

import napari
import numpy as np
from magicgui import magicgui
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas

#%% 

def show_data_widget(cell_data, all_id, myoii, pulse_data_path):

    # Define cellViewer class
    class cellViewer(napari.Viewer):
        pass
    
    cellViewer.cell_data = cell_data[0]
    cellViewer.pulse_data = np.zeros((6, len(all_id)), dtype=int)
    
    # Plot cell fig
    cell_fig = plt.figure(dpi=150) # Graph resolution
    
    # ---
    
    ax1 = cell_fig.add_subplot()
    line1, = ax1.plot(
        cell_data[0]['time_range'], cell_data[0]['myoii_intden'], 
        color='black', label='MyoII'
        )
    
    ax1.set_xlabel('Time point')
    ax1.set_ylabel('MyoII Int. Den. (A.U.)')
    
    # ---
    
    ax2 = ax1.twinx()
    line2, = ax2.plot(
        cell_data[0]['time_range'], cell_data[0]['area'],
        color='gray', linestyle='dashed', label='area'
        ) 
    
    ax2.set_xlabel('Time point')
    ax2.set_ylabel('Cell area (pixels)')  
    
    # ---
    
    ax3 = ax1.twinx(); 
    ax3.axis('off')
    
    # ---
    
    ax1.set_title('Cell #' + str(1) + ' MyoII & cell area')
    ax1.legend(handles=[line1, line2])

    # -------------------------------------------------------------------------
    
    @magicgui(
        
        auto_call = True,
        
        current_frame = {
            'widget_type': 'PushButton',
            'value': False, 
            'label': 'next cell'
            }
        
        next_cell = {
            'widget_type': 'PushButton',
            'value': False, 
            'label': 'next cell'
            },
        
        exit_cell = {
            'widget_type': 'PushButton',
            'value': False, 
            'label': 'exit and save'
            }    
        
        )
    
    def show_data(
            next_cell: bool,
            exit_cell: bool
            ):    
        
        # 
        current_frame = viewer.dims.current_step[0]
        ax3.axvline(x=current_frame)
                                    
        # Draw graph  
        cell_fig.canvas.draw_idle()

#%%                
    
    @show_data.next_cell.changed.connect  
    def update_show_data():
                
        # Extract variables      
            
        # ---------------------------------------------------------------------
        
        # Update cell data
        cellViewer.cell_data = cell_data[cellViewer.cell_data['cell_id']] 
        cell_id = cellViewer.cell_data['cell_id']
        time_range = cellViewer.cell_data['time_range']
        display = cellViewer.cell_data['display']
    
        # Update display
        viewer.layers.pop(0)
        viewer.add_image(
            display,
            name = 'Cell #' + str(cell_id) + ' MyoII',
            contrast_limits = [0, np.quantile(myoii, 0.999)]
            )
        
        # Update graph
        line1.set_xdata(time_range)
        line1.set_ydata(cellViewer.cell_data['myoii_intden'])
        ax1.relim()
        ax1.autoscale_view()
        
        line2.set_xdata(time_range)
        line2.set_ydata(cellViewer.cell_data['area'])
        ax2.relim()
        ax2.autoscale_view()
        
        ax1.set_title('Cell #' + str(cell_id) + ' MyoII & cell area')

    # -------------------------------------------------------------------------    
    
    # def update_slider(event):
    #     # only trigger if update comes from first axis (optional)
    #     print('inside')
    #         #ind_lambda = viewer.dims.indices[0]
    #     time = cellViewer.dims.current_step[0]
    #     cellViewer.text_overlay.text = f"{time:1.1f} time" 
        
    # -------------------------------------------------------------------------     
    
    @show_data.exit_cell.changed.connect  
    def exit_show_data():
        
        np.savetxt(pulse_data_path, cellViewer.pulse_data, fmt='%i', delimiter=',')
        cellViewer.close(viewer)
        
    # -------------------------------------------------------------------------
    
    # Set up the viewer
    viewer = cellViewer()
    show_data.native.layout().addWidget(FigureCanvas(cell_fig)) 
    viewer.window.add_dock_widget(show_data, area='right', name='widget') 
    viewer.add_image(
        cell_data[0]['display'],
        name='Cell #' + str(1) + ' MyoII',
        contrast_limits = [0, np.quantile(myoii, 0.999)]
        )
    
    return cellViewer.pulse_data