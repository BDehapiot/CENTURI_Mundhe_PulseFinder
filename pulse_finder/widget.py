#%% Imports

import napari
import numpy as np
from magicgui import magicgui
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas

#%% 

def show_data_widget(cell_data, all_id, myoii):

    # Define cellViewer class
    class cellViewer(napari.Viewer):
        pass
    
    cellViewer.cell_data = cell_data[0]
    cellViewer.pulse_data = np.zeros((6, len(all_id)), dtype=int)
    
    # Plot cell fig
    cell_fig = plt.figure()
    
    ax1 = cell_fig.add_subplot()
    line1, = ax1.plot(
        cell_data[0]['time_range'], cell_data[0]['myoii_intden'], 
        color='blue', label='MyoII'
        )
    
    ax1.set_xlabel('Time point')
    ax1.set_ylabel('MyoII Int. Den. (A.U.)')
    
    ax2 = ax1.twinx()
    line2, = ax2.plot(
        cell_data[0]['time_range'], cell_data[0]['area'],
        color='gray', linestyle='dashed', label='area'
        ) 
    
    ax2.set_xlabel('Time point')
    ax2.set_ylabel('Cell area (pixels)')  
    
    ax1.set_title('Cell #' + str(1) + ' MyoII & cell area')
    ax1.legend(handles=[line1, line2])
    
    p1_ti = ax1.twinx(); p1_ti.axis('off')
    p1_tf = ax1.twinx(); p1_tf.axis('off')
    p2_ti = ax1.twinx(); p2_ti.axis('off')
    p2_tf = ax1.twinx(); p2_tf.axis('off')
    # p3_ti = ax1.twinx(); p3_ti.axis('off')
    # p3_tf = ax1.twinx(); p3_tf.axis('off')
    
    # -------------------------------------------------------------------------
    
    @magicgui(
        
        auto_call = True,
        
        next_cell = {
            'widget_type': 'PushButton',
            'value': False, 
            'label': 'next cell'
            },
        
        exit_cell = {
            'widget_type': 'PushButton',
            'value': False, 
            'label': 'exit & save'
            },
        
        pulse1_ti = {
            'widget_type': 'Slider', 
            'min': np.min(cellViewer.cell_data['time_range'])-1, 
            'value': np.min(cellViewer.cell_data['time_range'])-1,
            'max': np.max(cellViewer.cell_data['time_range'])
            },
        
        pulse1_tf = {
            'widget_type': 'Slider', 
            'min': np.min(cellViewer.cell_data['time_range'])-1, 
            'value': np.min(cellViewer.cell_data['time_range'])-1,
            'max': np.max(cellViewer.cell_data['time_range'])
            }, 
    
        pulse2_ti = {
            'widget_type': 'Slider', 
            'min': np.min(cellViewer.cell_data['time_range'])-1, 
            'value': np.min(cellViewer.cell_data['time_range'])-1,
            'max': np.max(cellViewer.cell_data['time_range'])
            },
        
        pulse2_tf = {
            'widget_type': 'Slider', 
            'min': np.min(cellViewer.cell_data['time_range'])-1, 
            'value': np.min(cellViewer.cell_data['time_range'])-1,
            'max': np.max(cellViewer.cell_data['time_range'])
            }, 
        
        # pulse3_ti = {
        #     'widget_type': 'Slider', 
        #     'min': np.min(cellViewer.cell_data['time_range'])-1, 
        #     'value': np.min(cellViewer.cell_data['time_range'])-1,
        #     'max': np.max(cellViewer.cell_data['time_range'])
        #     },
        
        # pulse3_tf = {
        #     'widget_type': 'Slider', 
        #     'min': np.min(cellViewer.cell_data['time_range'])-1,
        #     'value': np.min(cellViewer.cell_data['time_range'])-1,
        #     'max': np.max(cellViewer.cell_data['time_range'])
        #     }, 
    
        )
    
    def show_data(
            next_cell: bool,
            exit_cell: bool,
            pulse1_ti: int, pulse1_tf: int,
            pulse2_ti: int, pulse2_tf: int,     
            # pulse3_ti: int, pulse3_tf: int,
            ):        
                  
        # Extract variables    
        cell_id = cellViewer.cell_data['cell_id']
        time_range = cellViewer.cell_data['time_range']
    
        # --- pulse1 ---
        if pulse1_ti >= np.min(time_range): 
            p1_ti.clear()
            p1_ti.axvline(x=pulse1_ti)
            p1_ti.text(pulse1_ti+0.25,0.83,'p1_ti',rotation=90)
            p1_ti.axis('off')
            pulse1_ti = show_data.pulse1_ti.value
        else:
            p1_ti.clear(); p1_ti.axis('off')
        
        if pulse1_tf >= pulse1_ti: 
            p1_tf.clear()
            p1_tf.axvline(x=pulse1_tf)
            p1_ti.text(pulse1_tf+0.25,0.83,'p1_tf',rotation=90)
            p1_tf.axis('off')
            pulse1_tf = show_data.pulse1_tf.value
        else:
            p1_tf.clear(); p1_tf.axis('off')
         
        # --- pulse2 ---   
        if pulse2_ti >= pulse1_tf: 
            p2_ti.clear()
            p2_ti.axvline(x=pulse2_ti)
            p2_ti.text(pulse2_ti+0.25,0.83,'p2_ti',rotation=90)
            p2_ti.axis('off')
            pulse2_ti = show_data.pulse2_ti.value
        else:
            p2_ti.clear(); p2_ti.axis('off') 
        
        if (pulse2_ti >= pulse1_tf) and (
            pulse2_tf >= pulse1_tf) and (
            pulse2_tf >= pulse2_ti):                 
            p2_tf.clear()
            p2_tf.axvline(x=pulse2_tf)
            p2_ti.text(pulse2_tf+0.25,0.83,'p2_tf',rotation=90)
            p2_tf.axis('off')
            pulse2_tf = show_data.pulse2_tf.value
        else:
            p2_tf.clear(); p2_tf.axis('off')    
            
        # --- pulse3 ---   
        # if pulse3_ti >= pulse2_tf: 
        #     p3_ti.clear()
        #     p3_ti.axvline(x=pulse3_ti)
        #     p3_ti.text(pulse3_ti+0.25,0.83,'p3_ti',rotation=90)
        #     p3_ti.axis('off')
        #     pulse3_ti = show_data.pulse3_ti.value
        # else:
        #     p3_ti.clear(); p3_ti.axis('off')
        
        # if (pulse3_ti >= pulse2_tf) and (
        #     pulse3_tf >= pulse2_tf) and (
        #     pulse3_tf >= pulse3_ti):                 
        #     p3_tf.clear()
        #     p3_tf.axvline(x=pulse3_tf)
        #     p3_ti.text(pulse3_tf+0.25,0.83,'p3_tf',rotation=90)
        #     p3_tf.axis('off')
        #     pulse3_tf = show_data.pulse3_tf.value
        # else:
        #     p3_tf.clear(); p3_tf.axis('off') 
           
        # Draw graph  
        cell_fig.canvas.draw()
       
        # Append pulse_data       
        if (pulse1_ti > np.min(time_range)-1) and (
            pulse1_tf > pulse1_ti):
            cellViewer.pulse_data[0,cell_id-1] = pulse1_ti
            cellViewer.pulse_data[1,cell_id-1] = pulse1_tf
        
        if (pulse2_ti > np.min(time_range)-1) and (
            pulse2_ti >= pulse1_tf) and (
            pulse2_ti > pulse2_tf):
            cellViewer.pulse_data[2,cell_id-1] = pulse2_ti
            cellViewer.pulse_data[3,cell_id-1] = pulse2_tf      
            
        # if (pulse3_ti > np.min(time_range)-1) and (
        #     pulse3_ti >= pulse2_tf) and (
        #     pulse3_ti > pulse3_tf):
        #     cellViewer.pulse_data[4,cell_id-1] = pulse3_ti
        #     cellViewer.pulse_data[5,cell_id-1] = pulse3_tf
                
    # -------------------------------------------------------------------------    
    
    @show_data.next_cell.changed.connect  
    def update_show_data():
    
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
    
        # Update sliders
        show_data.pulse1_ti.min = show_data.pulse1_ti.value = np.min(time_range)-1
        show_data.pulse1_tf.min = show_data.pulse1_tf.value = np.min(time_range)-1
        show_data.pulse1_ti.max = show_data.pulse1_tf.max = np.max(time_range)
        
        show_data.pulse2_ti.min = show_data.pulse2_ti.value = np.min(time_range)-1
        show_data.pulse2_tf.min = show_data.pulse2_tf.value = np.min(time_range)-1
        show_data.pulse2_ti.max = show_data.pulse2_tf.max = np.max(time_range)
    
        # show_data.pulse3_ti.min = show_data.pulse3_ti.value = np.min(time_range)-1
        # show_data.pulse3_tf.min = show_data.pulse3_tf.value = np.min(time_range)-1
        # show_data.pulse3_ti.max = show_data.pulse3_tf.max = np.max(time_range)
    
    # -------------------------------------------------------------------------    
    
    @show_data.exit_cell.changed.connect  
    def exit_show_data():
        
        cellViewer.close()
        
        return cellViewer.pulse_data
        
    
    # -------------------------------------------------------------------------
    
    # Set up the viewer
    viewer = cellViewer()
    show_data.native.layout().addWidget(FigureCanvas(cell_fig)) 
    viewer.window.add_dock_widget(show_data, area='bottom', name='widget') 
    viewer.add_image(
        cell_data[0]['display'],
        name='Cell #' + str(1) + ' MyoII',
        contrast_limits = [0, np.quantile(myoii, 0.999)]
        )

    return cellViewer.pulse_data