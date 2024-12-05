from neuron import h
import numpy as np
import os
import csv 
import json 
import matplotlib.pyplot as plt
import plotly
import matplotlib.colors as mcolors
from matplotlib import cm
import plotly.graph_objects as go

def max_shift(cell):

    # Initialize variables for tracking max/min values and corresponding segments
    max_shift=[0 for sec in cell.all for seg in sec]
    max_v=[h.v_init for sec in cell.all for seg in sec]
    min_v=[h.v_init for sec in cell.all for seg in sec]
    

    seg=[seg for sec in cell.all for seg in sec]

    # Callback function to update max/min voltages    
    # Initialize variables for tracking max/min values and corresponding segments
    results = {
        "max_v": 0,
        "min_v": 1e5,
        "max_seg": cell.soma(0.5),  # Default to soma
        "min_seg": cell.soma(0.5),
        "max_sec": cell.soma,  # Default to soma
        "min_sec": cell.soma
    }

    def every_step():
        i=0
        for sec in cell.all:
            for seg in sec:
                v_membrane=seg.v
                if v_membrane >=max_v[i]:
                    max_v[i]=v_membrane
                if v_membrane <=min_v[i]:
                    min_v[i]=v_membrane
                # v_shift=abs(abs(v_membrane)-abs(h.v_init))
                # if abs(v_shift) > max_shift[i]:
                #     max_shift[i]=abs(v_shift)
                i+=1
    for i in range(len(max_shift)):
        pshift=max_v[i]-h.v_init
        nshift=min_v[i]-h.v_init
        if abs(pshift)>= abs(nshift):
            max_shift[i]=pshift
        else:
            max_shift[i]=nshift

    results["max_v"]=max(max_shift)
    results["min_v"]=min(max_shift)
    results["max_seg"]=seg[max_shift.index(results["max_v"])]
    results["min_seg"]=seg[max_shift.index(results["min_v"])]
    results["max_sec"]=results["max_seg"].sec
    results["min_sec"]=results["min_seg"].sec

    
    callback=h.beforestep_callback(cell.soma(0.5))
    callback.set_callback(every_step) 

    return max_shift, callback


def plot_maxshift(max_shift,folder,cell):
    
    i=0
    for sec in cell.all:
        for seg in sec:
            seg.v=max_shift[i]
            i+=1    

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

    def saveplot():
        output_dir="frames"
        out=os.path.join(folder,output_dir)
        os.makedirs(out, exist_ok=True)  # Create directory if it doesn't exist
        file=os.path.join(out,f"max_shift.eps")
        ps.printfile(file)

    fig.show()
    # saveplot()
    
    return fig