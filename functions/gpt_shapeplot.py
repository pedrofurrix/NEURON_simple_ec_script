import plotly.graph_objects as go
from neuron import h, gui
import numpy as np
from matplotlib import cm

def morphology_voltage_movie(cell, cmap=cm.cool):
    fig = go.Figure()
    fig.update_layout(
        title="Membrane Voltage Over Time",
        scene=dict(
            xaxis=dict(title="X"),
            yaxis=dict(title="Y"),
            zaxis=dict(title="Z"),
        )
    )

    # Extract the morphology
    x_coords, y_coords, z_coords, v_values = [], [], [], []
    for sec in cell.all:
        for seg in sec:
            # x_coords.append(h.x3d(sec.arc3d(seg.x)))
            # y_coords.append(h.y3d(sec.arc3d(seg.x)))
            # z_coords.append(h.z3d(sec.arc3d(seg.x)))
            x_coords.append(seg.x_xtra)
            y_coords.append(seg.y_xtra)
            z_coords.append(seg.z_xtra)

            v_values.append(seg.v)  # Initial voltage

    # Normalize for the colormap
    vmin, vmax = -80, 50  # Adjust based on expected voltage range
    norm = cm.colors.Normalize(vmin=vmin, vmax=vmax)

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

        # Create a scatter plot for morphology
        fig.data = []  # Clear existing data
        fig.add_trace(go.Scatter3d(
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
            text=[f"Voltage: {v:.2f} mV" for v in current_voltages]
        ))

        fig.show()

    # Register the callback with NEURON
    callback = h.beforestep_callback(cell.soma(0.5))
    callback.set_callback(update_plot)

    return fig, callback



def update_plot(cell):
    
    """
    Collect voltage data during simulation and plot morphology once.
    """
    # Collect voltage data at each step
    voltage_over_time = []

    def record_voltages():
        # current_voltages=[]
        # for sec in cell.all:
        #     for seg in sec:
        #         current_voltages.append(seg.v)
        current_voltages = [seg.v for sec in cell.all for seg in sec]
        voltage_over_time.append(current_voltages)

    callback = h.beforestep_callback(cell.soma(0.5))
    callback.set_callback(record_voltages)
    # Add the callback
    # callback = h.CVode().extra_scatter_gather(record_voltages)

    # Run the simulation
    # h.finitialize(-65)
    # h.continuerun(100)  # Simulate for 100 ms

    return voltage_over_time,callback

def plot_final(cell,voltage_over_time):
    
     # Normalize for the colormap
    vmin, vmax = -80, 50  # Adjust based on expected voltage range
    norm = cm.colors.Normalize(vmin=vmin, vmax=vmax)

    # Coordinates of segments
    x_coords = [seg.x_xtra for sec in cell.all for seg in sec]
    y_coords = [seg.y_xtra for sec in cell.all for seg in sec]
    z_coords = [seg.z_xtra for sec in cell.all for seg in sec]

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