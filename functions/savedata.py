import pandas as pd
import os
import matplotlib.pyplot as plt
import csv 
from neuron import h


def savedata(folder,id,t,soma_v,dend_v,v_extracellular,is_xtra,vrec):
    filename=f"run{id}.csv"
    path=os.path.join(folder,filename)
    data=pd.DataFrame({"t":t,"soma_v":soma_v,"dend_v":dend_v,"v_extracellular":v_extracellular,"is_xtra":is_xtra,"vrec":vrec})
    data.to_csv(path,index=False)

def saveparams(run_id,cell,simparams,stimparams):
    #Create folder for run
    current_directory = os.getcwd()
    print(current_directory)
    folder_name=f"data\\{stimparams[4]}Hz"
    top_dir = os.path.join(current_directory, folder_name)
    if not os.path.exists(top_dir):
        os.makedirs(top_dir)
    bot_dir = os.path.join(top_dir,f"{stimparams[0]}Vm")
    if not os.path.exists(bot_dir):
        os.makedirs(bot_dir)


    filename="params.json"
    path=os.path.join(bot_dir,filename)
    params = {
        
        "Simulation Parameters": {
            "temperature" : h.celsius(),
            "cell_id" : simparams[2], # cell name
            "cell_name" : 
            "dt": simparams[0],  # in ms
            "simtime": simparams[1],  # in ms
        },
        "Stimulation Parameters": {
            "E": stimparams[0],  # Electric field in V/m
            "Delay": stimparams[1],  # Delay in ms
            "Amplitude": stimparams[2],  # Amplitude multiplier
            "Duration": stimparams[3],  # Duration in ms
            "Carrier Frequency": stimparams[4],  # Frequency in Hz
            "Modulation Depth": stimparams[5],  # Depth (0-1)
            "Modulation Frequency": stimparams[6]  # Modulation frequency in Hz
        }
    }
    locations="locations_xtra.csv"
    path=os.path.join(folder,locations)
    with open(path, "w") as file:
        writer = csv.writer(file)
        header = ["seg", "x", "y", "z", "rx"]  # Column names as a list #[f"{sec.name()}({i})" for sec in cell.all for i, _ in enumerate(sec)]
        writer.writerow(header)
        for sec in cell.all:
            if h.ismembrane("xtra"):
                for seg in sec:
                    segname=seg
                    x = seg.x_xtra
                    y = seg.y_xtra
                    z = seg.z_xtra
                    rx = seg.rx_xtra
                    # Write the values to the file
                    writer.writerow([segname,x,y,z,rx])
    return folder 

def saveplot(folder,title,fig_or_ax):
    filename=f"{title}.png"

    if isinstance(fig_or_ax, plt.Axes):
        # If it's an Axes object, get the Figure from the Axes
        fig = fig_or_ax.get_figure()
    elif isinstance(fig_or_ax, plt.Figure):
        # If it's already a Figure, use it as is
        fig = fig_or_ax
    else:
        raise TypeError("Input must be a matplotlib Figure or Axes object.")
    
    path=os.path.join(folder,filename)
    
    fig.savefig(path)
    print(f"Successfully saved as {filename}")

def savespikes(folder,id,spiketimes):
    filename=f"spikes{id}.csv"
    path=os.path.join(folder,filename)
    
    spike_dict = {}
    for i, spikes in enumerate(spiketimes):
        spike_dict[f"{i}"]= spikes
    
    data=pd.DataFrame(spike_dict)
    data.to_csv(path,index=False)
    
def save_locations(folder,cell):
    path=os.path.join(folder,f"run_locations.csv")
    with open(path,'w',newline='') as file:
        writer = csv.writer(file)
        header =["seg","x","y","z","arc","diam"] #[f"{sec.name()}({i})" for sec in cell.all for i, _ in enumerate(sec)]
        writer.writerow(header)
        for sec in cell.all:
            for i in range(sec.n3d()):
                section_info=f"{sec.name()}({i})"
                x=sec.x3d(i)
                y=sec.y3d(i)
                z=sec.z3d(i)
                arc=sec.arc3d(i)
                diam=sec.diam3d(i)
                location=[section_info,x,y,z,arc,diam]
                writer.writerow(location)
    file.close()