import plotly.graph_objects as go
from neuron import h, gui
import numpy as np
from matplotlib import cm
import os

# Creates one plot for each timestep - instead of updating it.
def morphology_voltage_movie(cell, folder,cmap=cm.cool,tmin=1e5,tmax=1e5):

    fig = go.FigureWidget()
    fig.update_layout(
        title="Membrane Voltage Over Time",
        scene=dict(
            xaxis=dict(title="X"),
            yaxis=dict(title="Y"),
            zaxis=dict(title="Z"),
        )
    )

    # Extract the morphology
    x_coords, y_coords, z_coords, arcs, diams, initial_v = [], [], [], [], [], []
    for sec in cell.all:
        for i in range(sec.n3d()):
            x=sec.x3d(i)
            y=sec.y3d(i)
            z=sec.z3d(i)
            arc=sec.arc3d(i)
            diam=sec.diam3d(i)
            x_coords.append(x)
            y_coords.append(y)
            z_coords.append(z)
            arcs.append(arc)
            diams.append(diam)

    for sec in cell.all:
        for seg in sec:
            initial_v.append(seg.v)

    # Normalize for the colormap
    vmin, vmax = -100, 50  # Adjust based on expected voltage range
    norm = cm.colors.Normalize(vmin=vmin, vmax=vmax)
    colors = [f"rgb{tuple((np.array(cmap(norm(v)))[:3] * 255).astype(int))}" for v in initial_v]

    scatter=go.Scatter3d(
        x=x_coords,
        y=y_coords,
        z=z_coords,
        mode='markers',
        marker=dict(
            size=5,
            color=colors,
            showscale=True,
            colorbar=dict(title="Voltage (mV)"),
            colorscale="Viridis"
        ),
        text=[f"Voltage: {v:.2f} mV" for v in initial_v]
        )
    fig.add_trace(scatter)

    # for sec in cell.all:
    #     for seg in sec:
    #         # x_coords.append(h.x3d(sec.arc3d(seg.x)))
    #         # y_coords.append(h.y3d(sec.arc3d(seg.x)))
    #         # z_coords.append(h.z3d(sec.arc3d(seg.x)))

    #         x_coords.append(seg.x_xtra)
    #         y_coords.append(seg.y_xtra)
    #         z_coords.append(seg.z_xtra)

    #         v_values.append(seg.v)  # Initial voltage

    output_dir="frames"
    out=os.path.join(folder,output_dir)
    os.makedirs(out, exist_ok=True)  # Create directory if it doesn't exist
 
    def update_plot():
        """
        Callback to update the morphology plot with current voltage values.
        """
        # Update voltage values
        current_voltages = []
        for sec in cell.all:
            for seg in sec:
                current_voltages.append(seg.v)

        # Map voltage to colors
        colors = [f"rgb{tuple((np.array(cmap(norm(v)))[:3] * 255).astype(int))}" for v in current_voltages]
        scatter.marker.color = colors
        scatter.text = [f"Voltage: {v:.2f} mV" for v in current_voltages]
          # Save frame to file
        if tmin <= h.t <= tmax:
            filename=f"frame_{h.t:.2f}.png"
            out_file=os.path.join(out,filename)
            fig.write_image(out_file)

    # Register the callback with NEURON
    callback = h.beforestep_callback(cell.soma(0.5))
    callback.set_callback(update_plot)

    return fig, callback


def plot_final(cell,voltage_over_time):
    
     # Normalize for the colormap
    vmin, vmax = -80, 50  # Adjust based on expected voltage range
    norm = cm.colors.Normalize(vmin=vmin, vmax=vmax)

    # Coordinates of segments

    #Option 1 
    x_coords, y_coords, z_coords = [], [], []
    for sec in cell.all:
        for i in range(sec.n3d()):
            x_coords.append(sec.x3d(i))
            y_coords.append(sec.y3d(i))
            z_coords.append(sec.z3d(i))

    # Option 2
    # x_coords = [seg.x_xtra for sec in cell.all for seg in sec]
    # y_coords = [seg.y_xtra for sec in cell.all for seg in sec]
    # z_coords = [seg.z_xtra for sec in cell.all for seg in sec]

    # Use the last recorded voltages to create the plot
    last_voltages = voltage_over_time[-1]
    colors = [f"rgb{tuple((np.array(cm.viridis(norm(v)))[:3] * 255).astype(int))}" for v in last_voltages]

    fig = go.Figure(data=go.Scatter3d(
        x=x_coords,
        y=y_coords,
        z=z_coords,
        mode='markers',
        marker=dict(
            size=5,
            color=colors,
            showscale=True,
            colorbar=dict(title="Voltage (mV)"),
            colorscale="Viridis"
        ),
        text=[f"Voltage: {v:.2f} mV" for v in last_voltages]
    ))

    # Show the final plot in the browser
    fig.show()
    return fig


