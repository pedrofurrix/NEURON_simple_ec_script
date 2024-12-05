from neuron import h
import matplotlib.pyplot as plt
import os

# Directory to save frames
output_dir = "frames"
def updating_shape(folder,cell,t_min=0,t_max=1e6):

    os.path.join(folder,output_dir)
    os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist

    # Create a Shape object
    shape = h.Shape()
    # shape.variable("v")  # Set the variable to display (membrane voltage)
    shape.show(0)
    # shape.scale(-100, 50)  

    #Optional
    shape.exec_menu("Shape Plot")  # Open a Shape Plot GUI
    shape.exec_menu("Show Diam")   # Enable diameter visualization

    # Function to save a snapshot of the Shape object
    def save_frame(time_step):
        # Set up Matplotlib figure
        fig, ax = plt.subplots(figsize=(8, 6))
        shape.plot(plt)  # Plot the shape into Matplotlib
        ax.set_title(f"Voltage at t = {time_step:.1f} ms")
        plt.axis("off")  # Turn off axes
        frame_path = os.path.join(output_dir, f"frame_{int(time_step*10):04d}.ps")
        plt.savefig(frame_path)  # Save the current frame as a PNG
        plt.close()  # Close the figure to save memory

    # Callback function to update the shape and save frames
    def update_shape():
        current_time = h.t  # Current simulation time
        shape.flush()       # Update the shape with the latest simulation data
        if current_time > t_min and current_time<t_max:
            save_frame(current_time)  # Save the current frame

    # Register the callback
    callback = h.beforestep_callback(cell.soma(0.5))  # Attach to any reference section
    callback.set_callback(update_shape)

    return shape,callback
