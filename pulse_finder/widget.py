#%% Imports

import napari
import numpy as np
from scipy import signal
from magicgui import magicgui
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_qt5agg import FigureCanvas

#%% Initialize CellViewer

def display_cell_data(cell_data, all_id, myoii, pulse_data_path):

    # Define CellViewer class & attributes
    class CellViewer(napari.Viewer):
        pass

    # Initialize CellViewer attributes
    CellViewer.cell_data = cell_data[0]
    CellViewer.t0 = np.min(CellViewer.cell_data['time_range'])
    CellViewer.max_area = 0
    CellViewer.pulse_idx = 0
    CellViewer.pulse_time = []
    CellViewer.pulse_string = []
    CellViewer.pulse_data = []

#%% Initialize graph
    
    graph = plt.figure(dpi=100) # Graph resolution
    
    # Extract variables  
    time_range = CellViewer.cell_data['time_range']
    area = CellViewer.cell_data['area']
    myoii_intden = CellViewer.cell_data['myoii_intden']
    current_frame = len(CellViewer.cell_data['time_range'])//2
    t0 = CellViewer.t0
    
    # ax1 cell area    
    sos = signal.butter(2, 0.1, 'low', output='sos') # lowpass IIR
    area_filt = signal.sosfiltfilt(sos, area)

    ax1 = graph.add_subplot()
    line1, = ax1.plot(
        time_range, area,
        color='0.75', label='area'
        ) 
    
    line1_filt, = ax1.plot(
        time_range, area_filt,
        color='black', linestyle='dotted', label='MyoII filt'
        )
    
    ax1.set_xlabel('Time point')
    ax1.set_ylabel('Cell area (pixels)')  
    
    # ax2 myoii intden        
    sos = signal.butter(2, 0.3, 'low', output='sos') # lowpass IIR
    myoii_intden_filt = signal.sosfiltfilt(sos, myoii_intden)
    
    ax2 = ax1.twinx()
    
    line2, = ax2.plot(
        time_range, myoii_intden, 
        color=('#2378BE'), linewidth=2, label='MyoII'
        )
    
    line2_filt, = ax2.plot(
        time_range, myoii_intden_filt,
        color='black', linestyle='dotted', label='MyoII filt'
        )
    
    ax2.set_xlabel('Time point')
    ax2.set_ylabel('MyoII Int. Den. (A.U.)')
    
    # ax3 current frame        
    ax3 = ax1.twinx(); 
    ax3.clear()
    ax3.axvline(x=current_frame + t0, color='black', linewidth=1)
    ax3.text(current_frame + t0 + 0.5, 0.95, f'{current_frame + t0}')
    ax3.axis('off') 
    
    # ax4 max area
    ax4 = ax1.twinx(); 
    ax4.clear()
    ax4.axvline(x=np.argmax(area_filt) + t0, color='black', linewidth=1)
    ax4.axis('off')   

    # ax5 pulse ti&tf
    ax5 = ax1.twinx(); 
    ax5.clear()
    ax5.axis('off')
    
    # title and layout    
    ax1.set_title('Cell #' + str(1) + ' MyoII & cell area')
    # ax1.legend(handles=[line1, line2, line2_filt])
    graph.tight_layout()  
    
    # Update variables
    CellViewer.cell_data['area_filt'] = area_filt 
    CellViewer.max_area = np.argmax(area_filt) + t0
    CellViewer.cell_data['myoii_intden_filt'] = myoii_intden_filt
    

#%% Initialize widgets
    
    @magicgui(
        
        auto_call = True,
               
        current_frame = {
            'widget_type': 'Slider', 
            'label': 'current frame',
            'readout': False,
            'min': 0, 
            'value': len(CellViewer.cell_data['time_range'])//2,
            'max': len(CellViewer.cell_data['time_range'])-1,
            },
        
        critical_freq_area = {
            'widget_type': 'Slider',    
            'label': 'lowpass freq. area',
            'value': 10, 
            'min': 1,
            'max': 99,
            'step': 1,
            },
        
        critical_freq_myoii = {
            'widget_type': 'Slider',    
            'label': 'lowpass freq. myoii',
            'value': 30, 
            'min': 1,
            'max': 99,
            'step': 1,
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
            'label': 'pulse info',
            }
        
        )
    
#%% Display
    
    def display(
            current_frame: int,
            critical_freq_myoii: float,
            critical_freq_area: float,
            next_cell: bool,
            exit_cell: bool,
            pulse_info: str
            ):    
        
        # Extract t0
        t0 = CellViewer.t0
        
        # Draw current_frame vertical line
        ax3.clear()
        ax3.axvline(x=current_frame + t0, color='black', linewidth=1)
        ax3.text(current_frame + t0 + 0.5, 0.95, f'{current_frame + t0}')
        ax3.axis('off') 
        
        # Draw graph  
        graph.canvas.draw()
        
#%% Callbacks           

    @display.current_frame.changed.connect 
    def callback_current_frame():

        viewer.dims.set_point(0, display.current_frame.value)

    @display.critical_freq_area.changed.connect 
    def callback_critical_freq_area():

        # Extract variables  
        time_range = CellViewer.cell_data['time_range'] 
        area = CellViewer.cell_data['area']
        t0 = CellViewer.t0

        # Update graph
        
        # ax1 cell area  
        sos = signal.butter(2, display.critical_freq_area.value/100, 'low', output='sos') # lowpass IIR
        area_filt = signal.sosfiltfilt(sos, area)        
        line1_filt.set_xdata(time_range)
        line1_filt.set_ydata(area_filt)
        ax1.relim()
        ax1.autoscale_view()
        
        # ax4 max area
        ax4.clear()
        ax4.axvline(x=np.argmax(area_filt) + t0, color='black', linewidth=1)
        ax4.axis('off')
        
        graph.canvas.draw()

        # Update variables 
        CellViewer.cell_data['area_filt'] = area_filt
        CellViewer.max_area = np.argmax(area_filt) + t0

    @display.critical_freq_myoii.changed.connect 
    def callback_critical_freq_myoii():

        # Extract variables  
        time_range = CellViewer.cell_data['time_range'] 
        myoii_intden = CellViewer.cell_data['myoii_intden']
        
        # Update graph
        sos = signal.butter(2, display.critical_freq_myoii.value/100, 'low', output='sos') # lowpass IIR
        myoii_intden_filt = signal.sosfiltfilt(sos, myoii_intden)        
        line2_filt.set_xdata(time_range)
        line2_filt.set_ydata(myoii_intden_filt)
        ax2.relim()
        ax2.autoscale_view()  
                
        graph.canvas.draw()
        
        # Update variables 
        CellViewer.cell_data['myoii_intden_filt'] = myoii_intden_filt
        
    @display.next_cell.changed.connect  
    def callback_next_cell():
        
        # Extract variables
        t0 = CellViewer.t0
        
        # Extract pulse data
        temp_pulse_data = []
        for i in range(len(CellViewer.pulse_time)):
            if (i % 2) != 0:
                
                cell_duration = len(CellViewer.cell_data['time_range'])
                area = CellViewer.cell_data['area']
                cell_tmax_area_real = CellViewer.max_area
                myoii_intden_filt = CellViewer.cell_data['myoii_intden_filt'] 
                furrow_x = CellViewer.cell_data['furrow_x'] 
                ctrd_x = CellViewer.cell_data['ctrd_x']
                myoii_x = CellViewer.cell_data['myoii_x'] 
                # cell_tmax_area = cell_tmax_area_real - t0
                ti_real = CellViewer.pulse_time[i-1]
                tf_real = CellViewer.pulse_time[i]
                ti = ti_real - t0
                tf = tf_real - t0   
                
                tmax_real = np.argmax(myoii_intden_filt[ti:tf]) + ti_real
                tmax = tmax_real - t0
                if tmax_real <= cell_tmax_area_real:
                    valid = 1
                else:
                    valid = 0
                    
                ti_int =  myoii_intden_filt[ti]   
                tf_int =  myoii_intden_filt[tf]  
                tmax_int =  myoii_intden_filt[tmax] 
                on_rate = (tmax_int - ti_int) / (tmax - ti)
                off_rate = (tf_int - tmax_int) / (tf - tmax)
                
                prominence = tmax_int - myoii_intden_filt[ti]               
                duration = tf - ti                
                promdur_ratio = prominence / duration
                
                halfprom = (prominence/2) + ti_int
                temp = myoii_intden_filt[ti:tf].copy()
                temp[temp < halfprom] = 0
                temp[temp >= halfprom] = 1
                halfprom_width = np.sum(temp)
                
                ctrd_furrow_dist = (
                    ctrd_x - furrow_x)[tmax] 
                myoii_furrow_dist = (
                    myoii_x - furrow_x)[tmax] 

                temp_pulse_data.append({
                    'cell_duration': cell_duration, 
                    'cell_tmax_area': cell_tmax_area_real,
                    'pulse_crop': myoii_intden_filt[ti:tf],                    
                    'ti': ti_real,
                    'tf': tf_real,
                    'tmax': tmax_real,
                    'ti_int': ti_int,
                    'tf_int': tf_int,
                    'tmax_int': tmax_int,
                    'on_rate': on_rate,
                    'off_rate': off_rate,
                    'valid': valid, 
                    'prominence': prominence,
                    'duration': duration,
                    'promdur_ratio': promdur_ratio,
                    'halfprom_width': halfprom_width,
                    'ctrd_furrow_dist': ctrd_furrow_dist,
                    'myoii_furrow_dist': myoii_furrow_dist,       
                    }) 
            
        CellViewer.pulse_data.append(temp_pulse_data)
        
        # ---------------------------------------------------------------------
        
        # Update cell_data
        CellViewer.cell_data = cell_data[CellViewer.cell_data['cell_id']] 
        CellViewer.t0 = np.min(CellViewer.cell_data['time_range'])
        CellViewer.pulse_idx = 0
        CellViewer.pulse_time = []
        CellViewer.pulse_string = []
        display.current_frame.max = len(CellViewer.cell_data['time_range'])-1 
        display.current_frame.value = len(CellViewer.cell_data['time_range'])//2
        display.pulse_info.value = ''     
        
        # Extract variables   
        cell_id = CellViewer.cell_data['cell_id']
        cell_crop = CellViewer.cell_data['cell_crop']
        time_range = CellViewer.cell_data['time_range']
        t0 = CellViewer.t0
        area = CellViewer.cell_data['area']
        myoii_intden = CellViewer.cell_data['myoii_intden']

        # Update cell_crop
        viewer.layers.pop(0)
        viewer.add_image(
            cell_crop,
            name = 'Cell #' + str(cell_id) + ' MyoII',
            contrast_limits = [0, np.quantile(myoii, 0.999)]
            )
        
        # Update graph
        
        # ax1 cell area    
        sos = signal.butter(2, display.critical_freq_area.value/100, 'low', output='sos') # lowpass IIR
        area_filt = signal.sosfiltfilt(sos, area)

        line1.set_xdata(time_range)
        line1.set_ydata(CellViewer.cell_data['area'])
        ax1.relim()
        ax1.autoscale_view()
        
        line1_filt.set_xdata(time_range)
        line1_filt.set_ydata(area_filt)
        ax1.relim()
        ax1.autoscale_view()
        
        # ax2 myoii intden
        sos = signal.butter(2, display.critical_freq_myoii.value/100, 'low', output='sos') # lowpass IIR
        myoii_intden_filt = signal.sosfiltfilt(sos, myoii_intden) 

        line2.set_xdata(time_range)
        line2.set_ydata(myoii_intden)
        ax2.relim()
        ax2.autoscale_view()

        line2_filt.set_xdata(time_range)
        line2_filt.set_ydata(myoii_intden_filt)
        ax2.relim()
        ax2.autoscale_view()
        
        # ax4 max area
        ax4.clear()
        ax4.axvline(x=np.argmax(area_filt) + t0, color='black', linewidth=1)
        ax4.axis('off')
        
        # ax5 pulse ti&tf
        ax5.clear()
        ax5.axis('off')
        
        # title
        ax1.set_title('Cell #' + str(cell_id) + ' MyoII & cell area')
        
        graph.canvas.draw() 
        
        # Update variables        
        CellViewer.cell_data['area_filt'] = area_filt 
        CellViewer.max_area = np.argmax(area_filt) + t0
        CellViewer.cell_data['myoii_intden_filt'] = myoii_intden_filt
    
    @display.exit_cell.changed.connect  
    def callback_exit_cell():
        
        # Extract variables
        t0 = CellViewer.t0
        
        # Extract pulse data
        temp_pulse_data = []
        for i in range(len(CellViewer.pulse_time)):
            if (i % 2) != 0:
                
                cell_duration = len(CellViewer.cell_data['time_range'])
                area = CellViewer.cell_data['area']
                cell_tmax_area_real = CellViewer.max_area
                myoii_intden_filt = CellViewer.cell_data['myoii_intden_filt'] 
                furrow_x = CellViewer.cell_data['furrow_x'] 
                ctrd_x = CellViewer.cell_data['ctrd_x']
                myoii_x = CellViewer.cell_data['myoii_x'] 
                # cell_tmax_area = cell_tmax_area_real - t0
                ti_real = CellViewer.pulse_time[i-1]
                tf_real = CellViewer.pulse_time[i]
                ti = ti_real - t0
                tf = tf_real - t0   
                
                tmax_real = np.argmax(myoii_intden_filt[ti:tf]) + ti_real
                tmax = tmax_real - t0
                if tmax_real <= cell_tmax_area_real:
                    valid = 1
                else:
                    valid = 0
                    
                ti_int =  myoii_intden_filt[ti]   
                tf_int =  myoii_intden_filt[tf]  
                tmax_int =  myoii_intden_filt[tmax] 
                on_rate = (tmax_int - ti_int) / (tmax - ti)
                off_rate = (tf_int - tmax_int) / (tf - tmax)
                
                prominence = tmax_int - myoii_intden_filt[ti]               
                duration = tf - ti                
                promdur_ratio = prominence / duration
                
                halfprom = (prominence/2) + ti_int
                temp = myoii_intden_filt[ti:tf].copy()
                temp[temp < halfprom] = 0
                temp[temp >= halfprom] = 1
                halfprom_width = np.sum(temp)
                
                ctrd_furrow_dist = (
                    ctrd_x - furrow_x)[tmax] 
                myoii_furrow_dist = (
                    myoii_x - furrow_x)[tmax] 

                temp_pulse_data.append({
                    'cell_duration': cell_duration, 
                    'cell_tmax_area': cell_tmax_area_real,
                    'pulse_crop': myoii_intden_filt[ti:tf],                    
                    'ti': ti_real,
                    'tf': tf_real,
                    'tmax': tmax_real,
                    'ti_int': ti_int,
                    'tf_int': tf_int,
                    'tmax_int': tmax_int,
                    'on_rate': on_rate,
                    'off_rate': off_rate,
                    'valid': valid, 
                    'prominence': prominence,
                    'duration': duration,
                    'promdur_ratio': promdur_ratio,
                    'halfprom_width': halfprom_width,
                    'ctrd_furrow_dist': ctrd_furrow_dist,
                    'myoii_furrow_dist': myoii_furrow_dist,       
                    }) 
            
        CellViewer.pulse_data.append(temp_pulse_data)
        
        headers = np.array([
            'cell_id',
            'cell_duration',
            'cell_tmax_area',
            'pulse_id', 
            'valid',           
            'ti',
            'tf',
            'tmax',
            'ti_int',
            'tf_int',
            'tmax_int',      
            'on_rate',
            'off_rate', 
            'prominence',
            'duration',
            'promdur_ratio',
            'halfprom_width',
            'ctrd_furrow_dist',
            'myoii_furrow_dist',  
            ])        
        
        pulse_data = headers
        _pulse_data = CellViewer.pulse_data
        
        for cell_id, cell in enumerate(_pulse_data, 1):
            for pulse_id, pulse in enumerate(cell, 1):
                
                temp_data = np.array([
                    cell_id,
                    pulse['cell_duration'],
                    pulse['cell_tmax_area'],
                    pulse_id,
                    pulse['valid'],         
                    pulse['ti'],
                    pulse['tf'],
                    pulse['tmax'],
                    pulse['ti_int'],
                    pulse['tf_int'],
                    pulse['tmax_int'],      
                    pulse['on_rate'],
                    pulse['off_rate'], 
                    pulse['prominence'],
                    pulse['duration'],
                    pulse['promdur_ratio'],
                    pulse['halfprom_width'],
                    pulse['ctrd_furrow_dist'],
                    pulse['myoii_furrow_dist'],  
                    ])
                
                pulse_data = np.vstack([pulse_data, np.around(temp_data, decimals=3)])
                
        np.savetxt(pulse_data_path, pulse_data, fmt='%s', delimiter=',')
        
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
        t0 = np.min(CellViewer.cell_data['time_range'])
        pulse_idx = CellViewer.pulse_idx + 1      
        pulse_number = np.ceil(pulse_idx/2).astype(int)
        current_frame = display.current_frame.value + t0

        if (pulse_idx % 2) != 0:
            pulse_string = f'pulse #{int(pulse_number):02}: ti={current_frame:03}'
        else:
            pulse_string = f'; tf={current_frame:03}'

        # Update variables   
        CellViewer.pulse_idx = pulse_idx
        CellViewer.pulse_time.append(current_frame) 
        CellViewer.pulse_string.append(pulse_string) 
        
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
        
        # Update graph info
        ax5.clear()
        ax5.axis('off')
        
        if CellViewer.pulse_time:
        
            # ti & tf
            ax5.vlines(
                x=CellViewer.pulse_time, ymin=0, ymax=1,
                color='gray', linestyle='dashed', linewidth=1
                )
            ax5.set_ylim([0, 1])
            ax5.axis('off')     
            
            # Rectangles
            for i in range(len(CellViewer.pulse_time)):
                if (i % 2) != 0:
                    
                    ti = CellViewer.pulse_time[i-1]
                    tf = CellViewer.pulse_time[i]
                    ax5.add_patch(Rectangle(
                        (ti, 0), tf-ti, 1, facecolor='black', alpha=0.05
                        )
                    )  
                    
        graph.canvas.draw() 
            
    # -------------------------------------------------------------------------    

    @viewer.bind_key('Backspace')
    def remove_pulse_info(viewer):
        
        if CellViewer.pulse_idx > 0:

            # Update variables   
            CellViewer.pulse_idx -= 1
            CellViewer.pulse_time.pop()
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
            
            # Update graph info
            ax5.clear()           
            ax5.axis('off')

            if CellViewer.pulse_time:
            
                # Vertical lines
                ax5.vlines(
                    x=CellViewer.pulse_time, ymin=0, ymax=1,
                    color='gray', linestyle='dashed', linewidth=1
                    )
                ax5.set_ylim([0, 1])
                ax5.axis('off')  
                
                # Rectangles
                for i in range(len(CellViewer.pulse_time)):
                    if (i % 2) != 0:
                        
                        ti = CellViewer.pulse_time[i-1]
                        tf = CellViewer.pulse_time[i]
                        ax5.add_patch(Rectangle(
                            (ti, 0), tf-ti, 1, facecolor='black', alpha=0.05
                            )
                        )                                                
                
            graph.canvas.draw() 
            
    @viewer.bind_key('Control-Enter')
    def set_max_area(viewer):
        
        # Extract variables
        t0 = np.min(CellViewer.cell_data['time_range'])
        current_frame = display.current_frame.value + t0

        # ax4 max area
        ax4.clear()
        ax4.axvline(x=current_frame , color='black', linewidth=1)
        ax4.axis('off')
        
        graph.canvas.draw()
        
        # Update variables 
        CellViewer.max_area = current_frame

    return CellViewer.pulse_data   
