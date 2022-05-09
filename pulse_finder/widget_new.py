#%% Imports

import napari
import numpy as np
from scipy import signal
from magicgui import magicgui
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas

#%% Initialize CellViewer

def display_cell_data(cell_data, all_id, myoii, pulse_data_path):

    # Define CellViewer class & attributes
    class CellViewer(napari.Viewer):
        pass

    # Initialize CellViewer attributes
    CellViewer.cell_data = cell_data[0]
    CellViewer.pulse_idx = 0
    CellViewer.pulse_time = []
    CellViewer.pulse_string = []
    CellViewer.pulse_data = [] #[None]*len(cell_data) 

#%% Initialize graph
    
    graph = plt.figure(dpi=100) # Graph resolution
    
    # ax1 cell area    
    ax1 = graph.add_subplot()
    line1, = ax1.plot(
        cell_data[0]['time_range'], cell_data[0]['area'],
        color='0.75', label='area'
        ) 
    
    ax1.set_xlabel('Time point')
    ax1.set_ylabel('Cell area (pixels)')  
    
    # ax2 myoii intden    
    myoii_intden = cell_data[0]['myoii_intden']
    sos = signal.butter(2, 0.3, 'low', output='sos') # lowpass IIR
    myoii_intden_filt = signal.sosfiltfilt(sos, myoii_intden)
    
    ax2 = ax1.twinx()
    
    line2, = ax2.plot(
        cell_data[0]['time_range'], myoii_intden, 
        color=('#2378BE'), linewidth=2, label='MyoII'
        )
    
    line2_filt, = ax2.plot(
        cell_data[0]['time_range'], myoii_intden_filt,
        color='black', linestyle='dotted', label='MyoII filt'
        )
    
    ax2.set_xlabel('Time point')
    ax2.set_ylabel('MyoII Int. Den. (A.U.)')
    
    # ax3 current frame    
    t0 = np.min(cell_data[0]['time_range'])
    current_frame = len(cell_data[0]['time_range'])//2
    
    ax3 = ax1.twinx(); 
    ax3.clear()
    ax3.axvline(x=current_frame + t0, color='black', linewidth=1)
    ax3.text(current_frame + t0 + 0.5, 0.95, f'{current_frame + t0}')
    ax3.axis('off') 
    
    # ax4 pulse ti&tf
    ax4 = ax1.twinx(); 
    ax4.clear()
    ax4.axis('off')
    
    # title, legend and layout    
    ax1.set_title('Cell #' + str(1) + ' MyoII & cell area')
    # ax1.legend(handles=[line1, line2, line2_filt])
    graph.tight_layout()  
    

#%% Initialize widgets
    
    @magicgui(
        
        auto_call = True,
               
        current_frame = {
            'widget_type': 'Slider', 
            'label': 'current frame',
            'readout': False,
            'min': 0, 
            'value': len(CellViewer.cell_data['time_range'])//2,
            'max': len(CellViewer.cell_data['time_range'])-1
            },
        
        critical_freq = {
            'widget_type': 'FloatSpinBox',    
            'label': 'lowpass freq.',
            'value': 0.3, 
            'min': 0.05,
            'max': 0.95,
            'step': 0.05
            },

        next_cell = {
            'widget_type': 'PushButton',
            'label': 'next cell',
            'value': False, 
            },
        
        exit_cell = {
            'widget_type': 'PushButton',
            'label': 'exit and save',
            'value': False, 
            },
        
        pulse_info = {
            'widget_type': 'TextEdit', 
            'label': 'pulse info'
            }
        
        )
    
#%% Display
    
    def display(
            current_frame: int,
            critical_freq: float,
            next_cell: bool,
            exit_cell: bool,
            pulse_info: str
            ):    
        
        # Extract t0
        t0 = np.min(CellViewer.cell_data['time_range'])
        
        # Draw current_frame vertical line
        ax3.clear()
        ax3.axvline(x=current_frame + t0, color='black', linewidth=1)
        ax3.text(current_frame + t0 + 0.5, 0.95, f'{current_frame + t0}')
        ax3.axis('off') 
        
        # Draw graph  
        graph.canvas.draw_idle()
        
#%% Callbacks           

    @display.current_frame.changed.connect 
    def callback_current_frame():

        viewer.dims.set_point(0, display.current_frame.value)
    
    @display.critical_freq.changed.connect 
    def callback_critical_freq():

        # Extract variables  
        myoii_intden = CellViewer.cell_data['myoii_intden']
        time_range = CellViewer.cell_data['time_range']        
        
        # Update graph
        sos = signal.butter(2, display.critical_freq.value, 'low', output='sos') # lowpass IIR
        myoii_intden_filt = signal.sosfiltfilt(sos, myoii_intden)        
        line2_filt.set_xdata(time_range)
        line2_filt.set_ydata(myoii_intden_filt)
        ax2.relim()
        ax2.autoscale_view()        
        
    @display.next_cell.changed.connect  
    def callback_next_cell():  
        
        # Update cell_data
        CellViewer.cell_data = cell_data[CellViewer.cell_data['cell_id']] 
        
        # Extract variables   
        cell_id = CellViewer.cell_data['cell_id']
        time_range = CellViewer.cell_data['time_range']
        cell_crop = CellViewer.cell_data['cell_crop']
    
        # Update cell_crop
        viewer.layers.pop(0)
        viewer.add_image(
            cell_crop,
            name = 'Cell #' + str(cell_id) + ' MyoII',
            contrast_limits = [0, np.quantile(myoii, 0.999)]
            )
        
        # Update graph
        
        # ax1 cell area       
        line1.set_xdata(time_range)
        line1.set_ydata(CellViewer.cell_data['area'])
        ax1.relim()
        ax1.autoscale_view()
        
        # ax2 myoii intden
        myoii_intden = CellViewer.cell_data['myoii_intden']
        sos = signal.butter(2, display.critical_freq.value, 'low', output='sos') # lowpass IIR
        myoii_intden_filt = signal.sosfiltfilt(sos, myoii_intden) 
        
        line2.set_xdata(time_range)
        line2.set_ydata(myoii_intden)
        ax2.relim()
        ax2.autoscale_view()

        line2_filt.set_xdata(time_range)
        line2_filt.set_ydata(myoii_intden_filt)
        ax2.relim()
        ax2.autoscale_view()
        
        # title
        ax1.set_title('Cell #' + str(cell_id) + ' MyoII & cell area')
  
        # # Extract pulse_data
        # split_string = display.pulse_info.value.split('\n')
        # for line_string in split_string:
        #     if len(line_string) == 25:
        #         cell_id = cell_id-1
        #         pulse_number = int(line_string[7:9])
        #         pulse_ti = int(line_string[14:17])
        #         pulse_tf = int(line_string[22:25])               
        #         CellViewer.pulse_data.append((
        #             cell_id, pulse_number, pulse_ti, pulse_tf
        #             ))
        
        # Update variables
        display.current_frame.value = len(CellViewer.cell_data['time_range'])//2
        display.current_frame.max = len(CellViewer.cell_data['time_range'])-1   
        display.pulse_info.value = ''                
        CellViewer.pulse_idx = 0
        CellViewer.pulse_string = []
    
    @display.exit_cell.changed.connect  
    def callback_exit_cell():

        # np.savetxt(pulse_data_path, CellViewer.pulse_data, fmt='%i', delimiter=',')
        CellViewer.close(viewer)

#%% Set up viewer

    viewer = CellViewer()
    display.native.layout().addWidget(FigureCanvas(graph)) 
    viewer.window.add_dock_widget(display, area='right', name='widget') 
    viewer.add_image(
        cell_data[0]['cell_crop'],
        name='Cell #' + str(1) + ' MyoII',
        contrast_limits = [0, np.quantile(myoii, 0.999)]
        )

#%% Set up shortcuts
    
    @viewer.bind_key('Enter')
    def add_pulse_info(viewer):
        
        # Extract variables
        cell_id = CellViewer.cell_data['cell_id']
        t0 = np.min(CellViewer.cell_data['time_range'])
        pulse_idx = CellViewer.pulse_idx + 1      
        pulse_number = np.ceil(pulse_idx/2).astype(int)
        current_frame = display.current_frame.value + t0
        
        if (pulse_idx % 2) != 0:
            pulse_string = f'pulse #{int(pulse_number):02}: ti={current_frame:03}'
        else:
            pulse_string = f'; tf={current_frame:03}'

        print('print' + pulse_string) 

        # Update variables   
        CellViewer.pulse_idx = pulse_idx
        CellViewer.pulse_time.append(current_frame) 
        CellViewer.pulse_string.append(pulse_string) 
        
        print(CellViewer.pulse_time)

        # Get full_string
        for i, string in enumerate(CellViewer.pulse_string):

            if (i % 2) == 0:
                line_string = string
            else:
                line_string += string
                
            if i < 2:
                full_string = line_string
            else: 
                            
                if ((i % 2) != 0):
                    full_string = (full_string + '\n' + line_string)
                    
                if ((i % 2) == 0) and (i == len(CellViewer.pulse_string)-1):
                    full_string = (full_string + '\n' + line_string)   

        display.pulse_info.value = full_string
        
        # Add vertical lines
        ax4.clear()
        ax4.vlines(
            x=CellViewer.pulse_time, ymin=0, ymax=1,
            color='gray', linestyle='dashed', linewidth=1)
        ax4.set_ylim([0, 1])
        ax4.axis('off')       

        # Add rectangles
        from matplotlib.patches import Rectangle
        
        if CellViewer.pulse_time:
            
            for i in range(len(CellViewer.pulse_time)):

                if (i % 2) == 0:
                    ti = CellViewer.pulse_time[i-1]
                    tf = CellViewer.pulse_time[i]
                    ax4.add_patch(Rectangle((ti, 0), tf-ti, 1, facecolor='black', alpha=0.05))
                else:
                    pass
                
        # CellViewer.pulse_data[cell_id-1] = display.pulse_info.value ###

    @viewer.bind_key('Backspace')
    def remove_pulse_info(viewer):
        
        if CellViewer.pulse_idx > 0:
        
            # Extract variables
            cell_id = CellViewer.cell_data['cell_id']    
            
            print('erase' + CellViewer.pulse_string[-1]) 

            # Update variables   
            CellViewer.pulse_idx -= 1
            CellViewer.pulse_string.pop()
            
            # Get full_string
            if CellViewer.pulse_string:
                
                for i, string in enumerate(CellViewer.pulse_string):
        
                    if (i % 2) == 0:
                        line_string = string
                    else:
                        line_string += string
                        
                    if i < 2:
                        full_string = line_string
                    else: 
                                    
                        if ((i % 2) != 0):
                            full_string = (full_string + '\n' + line_string)
                            
                        if ((i % 2) == 0) and (i == len(CellViewer.pulse_string)-1):
                            full_string = (full_string + '\n' + line_string)   
                            
                display.pulse_info.value = full_string
                
            else: 
                
                display.pulse_info.value = ''
            
            #
            # CellViewer.pulse_data[cell_id-1] = display.pulse_info.value ###

    return CellViewer.pulse_data


    
