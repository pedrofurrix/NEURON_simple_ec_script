import pandas as pd
import os
import matplotlib.pyplot as plt
import csv 
from neuron import h
import plotly
import matplotlib.colors as mcolors
from matplotlib import cm
import plotly.graph_objects as go
import numpy as np

import sys
sys.path.append(r"C:\Users\Pc\Documents\Charite\NEURON")

import os
current_directory = os.getcwd()
print(current_directory)
path = os.path.join(current_directory,"Extracellular_test","Homogeneous_EField", "mechanisms", "nrnmech.dll")
print(path)
h.nrn_load_dll(path)

from max_minshift import get_folder,cmax_shift
folder=get_folder(0)
max_shift, max_v, min_v, results=cmax_shift(folder)

def load_geometry(folder):
    locfile=os.path.join(folder,"run_locations.csv")
    locations=pd.read_csv(locfile)
    return locations

def load_voltages(folder):
    vfile=os.path.join(folder,"run_voltages.csv")
    voltages=pd.read_csv(vfile)
    return voltages

def plot_voltage_shape(folder,cell,max_v,min_v): # can also just extract these again...
   # locations=load_geometry(folder)
    voltages=load_voltages(folder)
    
    times=voltages["t"].to_list()

    vmin=min(min_v)
    vmax=max(max_v)

 # Create a custom colormap using Matplotlib (cool colormap)
    cmap = cm.cool
    
    # Collect values of the variable from all segments
    # Create a colormap function
    colormap = cm.ScalarMappable(cmap=cmap, norm=mcolors.Normalize(vmin=0, vmax=1)).to_rgba

    # Map the normalized values to a Plotly colorscale as strings
    plotly_colorscale = [[v, f'rgb{tuple(int(255 * c) for c in colormap(v)[:3])}'] for v in np.linspace(0, 1, cmap.N)]

    # Create a separate scatter plot for the colorbar
    colorbar_trace = go.Scatter(
    x=[0],
    y=[0],
    mode='markers',
    marker=dict(
        colorscale=plotly_colorscale,
        cmin=vmin,
        cmax=vmax,
        colorbar=dict(
            title="Max Shift",
            thickness=20  # Adjust the thickness of the colorbar
        ),
        showscale=True
    )
    )

    def saveplot():
            output_dir="frames"
            out=os.path.join(folder,output_dir)
            os.makedirs(out, exist_ok=True)  # Create directory if it doesn't exist
            file=os.path.join(out,f"pshape_t{t}.eps")
            ps.printfile(file)

    for i,t in enumerate(times):
        v_values=voltages.iloc[i,1:].to_list()
        index=0
        for sec in cell.all:
            for seg in sec:
                seg.v=v_values[index]
                index+=1   

        ps = h.PlotShape(False)
        ps.show(0)
        ps.variable("v")  # Associate the PlotShape with the 'v' variable
        ps.scale(vmin, vmax)  # Set the color scale
        fig=ps.plot(plotly, cmap=cm.cool)

        # Add the colorbar trace to the figure
        fig.add_trace(colorbar_trace)
        fig.update_xaxes(showticklabels=False, showgrid=False)
        fig.update_yaxes(showticklabels=False, showgrid=False)
        fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)'
        )
        #fig.show()
        # saveplot()

    
    
    # saveplot()
    
    return fig

def rough_plot_voltage_shape(folder,cell,max_shift):
    locations=load_geometry(folder)
    voltages=load_voltages(folder)
    
    def saveplot():
            output_dir="frames"
            out=os.path.join(folder,output_dir)
            os.makedirs(out, exist_ok=True)  # Create directory if it doesn't exist
            file=os.path.join(out,f"pshape_t{t}.eps")
            ps.printfile(file)
            
    for i,t in enumerate(voltages["t"]):
        v_values=voltages.iloc[i,1:]
        index=0
        for sec in cell.all:
            for seg in sec:
                seg.v=v_values[index]
                index+=1    

        ps = h.PlotShape(False)
        vmin=min(max_shift)
        vmax=max(max_shift)

        ps.show(0)
        ps.variable("v")  # Associate the PlotShape with the 'v' variable
        ps.scale(vmin, vmax)  # Set the color scale
        fig=ps.plot(plotly, cmap=cm.cool)

        # Create a custom colormap using Matplotlib (cool colormap)
        cmap = cm.cool

        # Collect values of the variable from all segments
        # Create a colormap function
        colormap = cm.ScalarMappable(cmap=cmap, norm=mcolors.Normalize(vmin=0, vmax=1)).to_rgba

        # Map the normalized values to a Plotly colorscale as strings
        plotly_colorscale = [[v, f'rgb{tuple(int(255 * c) for c in colormap(v)[:3])}'] for v in np.linspace(0, 1, cmap.N)]

        # Create a separate scatter plot for the colorbar
        colorbar_trace = go.Scatter(
        x=[0],
        y=[0],
        mode='markers',
        marker=dict(
            colorscale=plotly_colorscale,
            cmin=vmin,
            cmax=vmax,
            colorbar=dict(
                title="Max Shift",
                thickness=20  # Adjust the thickness of the colorbar
            ),
            showscale=True
        )
        )

        # Add the colorbar trace to the figure
        fig.add_trace(colorbar_trace)
        fig.update_xaxes(showticklabels=False, showgrid=False)
        fig.update_yaxes(showticklabels=False, showgrid=False)
        fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)'
        )
        # saveplot()
  
    

    # fig.show()
    # saveplot()
    
    return fig

def plot_voltage_no_cell(folder,max_v=None,min_v=None): # can also just extract these again...
    locations=load_geometry(folder)
    voltages=load_voltages(folder)

    if max_v:
        vmin=min(min_v)
        vmax=max(max_v)
    else:
        vmin=voltages.drop(columns=["t"]).min().min()
        vmax=voltages.drop(columns=["t"]).max().max()
    print(vmin,vmax)

    # Extract the morphology
    x_coords=locations["x"].to_list()
    y_coords=locations["y"].to_list()
    z_coords = locations["z"].to_list()
    arcs = locations["arc"].to_list()
    diams = locations["diam"].to_list()

    # Create a custom colormap using Matplotlib (cool colormap)
    cmap = cm.cool
    # Normalize for the colormap
    norm = mcolors.Normalize(vmin=0, vmax=1)
    colormap = cm.ScalarMappable(cmap=cmap, norm=norm).to_rgba
    plotly_colorscale = [[v, f'rgb{tuple(int(255 * c) for c in colormap(v)[:3])}'] for v in np.linspace(0, 1, cmap.N)]


    # Create the base figure
    fig = go.Figure()
    fig.update_layout(
        title="Membrane Voltage Over Time",
        scene=dict(
            xaxis=dict(title="X"),
            yaxis=dict(title="Y"),
            zaxis=dict(title="Z"),
        ),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            buttons=[
                dict(label="Play",
                     method="animate",
                     args=[None, dict(frame=dict(duration=100, redraw=True), fromcurrent=True)]),
                dict(label="Pause",
                     method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")])
            ]
        )]
    )
    
    # Add scatter traces for each time point (hidden initially)
    frames = []
    norm2 = cm.colors.Normalize(vmin=vmin, vmax=vmax)    
    for i, t in enumerate(voltages["t"]):
        frame_voltages = voltages.iloc[i, 1:].tolist()  # Voltages for this time step
        frame_colors = [f'rgb{tuple((np.array(cmap(norm2(v)))[:3] * 255).astype(int))}' for v in frame_voltages]

        # Create a frame for the animation
        frames.append(go.Frame(
            data=[go.Scatter3d(
                x=x_coords,
                y=y_coords,
                z=z_coords,
                mode='lines+markers',
                line=dict(width=2, color='red'),
                marker=dict(
                    size=5,
                   color=frame_colors,
                    showscale=True,
                    colorscale=plotly_colorscale,
                    cmin=vmin,
                    cmax=vmax,
                    colorbar=dict(title="Voltage (mV)", thickness=20)
                ),
                text=[f"Voltage: {v:.2f} mV" for v in frame_voltages]
            )],
            name=f"t={t:.2f} ms"
        ))

    # Add the first frame as the initial scatter
    initial_voltages = voltages.iloc[0, 1:].tolist()
    initial_colors = [f'rgb{tuple((np.array(cmap(norm2(v)))[:3] * 255).astype(int))}' for v in initial_voltages]

    fig.add_trace(go.Scatter3d(
    x=x_coords,
    y=y_coords,
    z=z_coords,
    mode='lines+markers',    
    line=dict(width=2, color='red'),
    marker=dict(
        size=5,
        color=initial_colors,
        showscale=True,
        colorscale=plotly_colorscale,
        cmin=vmin,
        cmax=vmax,
        colorbar=dict(title="Voltage (mV)", thickness=20)
    ),
    text=[f"Voltage: {v:.2f} mV" for v in initial_voltages]
    ))
     # Add frames to the figure
    fig.frames = frames

    path= os.path.join(folder,"voltage_animation.html")
    fig.write_html(path)
    return fig


fig=plot_voltage_no_cell(folder)
fig.show()

# from Extracellular_test.Homogeneous_Efield.functions import ballandstick
# cell=ballandstick.BallAndStick2(0,0,0,0,0,0) #doesn't work in regular python...

# plot_voltage_shape(folder,cell,max_v,min_v)