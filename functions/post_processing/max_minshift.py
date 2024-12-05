from neuron import h
import numpy as np
import csv
import pandas as pd
import os
import matplotlib.pyplot as plt
import plotly
import matplotlib.colors as mcolors
from matplotlib import cm
import plotly.graph_objects as go
import pickle
import json

def load_voltages(folder):
    vfile=os.path.join(folder,"run_voltages.csv")
    voltages=pd.read_csv(vfile)
    return voltages

def load_params(bot_dir): #Load paramsssssssss (get them into a format where I can easily extract them.., ) - json
    filename="params.json"
    path = os.path.join(bot_dir, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"The parameters file does not exist at {path}")
    # Load the JSON file
    with open(path, "r") as file:
        params = json.load(file)
    # Extract simulation and stimulation parameters
    simparams = params["Simulation Parameters"]
    stimparams = params["Stimulation Parameters"]

    # Return the parameters
    return simparams, stimparams

def cmax_shift(bot_dir,top_dir, cell=None):
    voltages=load_voltages(bot_dir)
    headers=voltages.drop(columns=["t"]).columns.tolist()
    simparams, stimparams=load_params(bot_dir)

    # params=load_params(folder)
    v_init=-65

    num_seg=len(voltages.iloc[0,1:]) #remove column that has the time

    if cell:
        # Initialize variables for tracking max/min values and corresponding segments
        max_shift=[0 for sec in cell.all for seg in sec] #alternatively, h.allsec() #Change also when obtaining the values...
        max_v=[h.v_init for sec in cell.all for seg in sec]
        min_v=[h.v_init for sec in cell.all for seg in sec]
        seg=[seg for sec in cell.all for seg in sec]
        pshift=[0 for sec in cell.all for seg in sec]
        nshift=[0 for sec in cell.all for seg in sec]
    else:
        max_shift=[0 for seg in range(num_seg)] #alternatively, h.allsec() #Change also when obtaining the values...
        max_v=[v_init for seg in range(num_seg)]
        min_v=[v_init for seg in range(num_seg)]
        seg=[seg for seg in range(num_seg)]
        pshift=[0 for seg in range(num_seg)]
        nshift=[0 for seg in range(num_seg)]

    # Initialize variables for tracking max/min values and corresponding segments
    results = {
        "EValue": stimparams["E"],
        "CFreq": stimparams["Carrier Frequency"],
        "max_shiftp": -1e5,
        "min_shiftp": 1e5,
        "max_shiftn": 0,
        "min_shiftn": 0,
        "maxp_seg": None, 
        "minp_seg": None,
        "maxn_seg": None,  
        "minn_seg": None,
        "maxp_sec": None,  
        "minp_sec": None,
        "maxn_sec": None,  
        "minn_sec": None
    }

    # i=0
    # for sec in cell.all: #alternatively, h.allsec() #Change also when obtaining the values...
    #     for seg in sec:

    for i in range(num_seg):
            v_seg=voltages.iloc[:,i+1] # Returns the membrane potential over time for each segment
            for v in v_seg:
                if v >=max_v[i]:
                    max_v[i]=v
                if v <=min_v[i]:
                    min_v[i]=v
    
    
    for i in range(len(max_shift)):
        pshift[i]=max_v[i]-v_init
        nshift[i]=min_v[i]-v_init
        if abs(pshift)>= abs(nshift):
            max_shift[i]=pshift
        else:
            max_shift[i]=nshift

              #This has to change if they have different values...
    # In case they are different, h.v_init can be replaced by voltages.iloc[0,i] - initial voltage...
    # 
    results["max_shiftp"]=max(pshift)
    results["min_shiftp"]=min(pshift)
    results["max_shiftn"]=max(nshift,key=abs)
    results["min_shiftn"]=min(nshift,key=abs)
    results["maxp_index"]=next((i for i, val in enumerate(pshift) if abs(val) == abs(results["max_shiftp"])))
    results["minp_index"]=next((i for i, val in enumerate(pshift) if abs(val) == abs(results["min_shiftp"])))
    results["maxn_index"]=next((i for i, val in enumerate(nshift) if abs(val) == abs(results["max_shiftn"])))
    results["minn_index"]=next((i for i, val in enumerate(nshift) if abs(val) == abs(results["min_shiftn"])))
    results["maxp_seg"] = voltages.columns[results["maxp_index"]+1] # +1 is to account for time being the first column # could also just drop that column
    results["minp_seg"] = voltages.columns[results["minp_index"]+1]
    results["maxn_seg"] = voltages.columns[results["maxn_index"]+1] # +1 is to account for time being the first column # could also just drop that column
    results["minn_seg"] = voltages.columns[results["minn_index"]+1]   

    if cell:
        results["maxp_seg"]=seg[results["maxp_index"]]
        results["minp_seg"]=seg[results["minp_index"]]
        results["maxn_seg"]=seg[results["maxn_index"]]
        results["minn_seg"]=seg[results["minn_index"]]
        results["maxp_sec"]=results["maxp_seg"].sec
        results["minp_sec"]=results["minp_seg"].sec
        results["maxn_sec"]=results["maxn_seg"].sec
        results["minn_sec"]=results["minn_seg"].sec

    # Save the results obtained into files.
    def save_max():
        data={
            "seg" : headers,
            "max_v" : max_v,
            "min_v" : min_v,
            "max_shift" : max_shift,
            "pshift" : pshift,
            "nshift" : nshift
        }
        # Save the data
        out_file=os.path.join(bot_dir,"max_shift_data.csv")
        data_pd=pd.DataFrame([data])
        data_pd.to_csv(out_file,index=False)

        top_file=os.path.join(top_dir, "results_summary.csv")
        results_df = pd.DataFrame([results])

        if os.path.exists(top_file):
            # If file exists, append the new results without writing the header
            results_df.to_csv(top_file, mode='a', index=False, header=False)
        else:
            # If file does not exist, write the results with the header
            results_df.to_csv(top_file, index=False, header=True)
        
    save_max()

    return max_shift, max_v, min_v, results

def plot_voltage(folder,results):
    voltages=load_voltages(folder)

    v_max_index=results["max_index"]
    v_min_index=results["min_index"]
    vmax=voltages.iloc[:,v_max_index+1]
    vmin=voltages.iloc[:,v_min_index+1]
    
    segmax=results["max_seg"]
    segmin=results["min_seg"]

    t=voltages.iloc[:,0]
    fig,ax=plt.subplots()
    ax.plot(t, vmax,label=f"max_shift_{segmax}")
    ax.plot(t, vmin,label=f"min_shift_{segmin}")
   
    ax.set_xlabel("time (ms)")  # Correct method to set labels
    ax.set_ylabel("Membrane potential (mV)")
    ax.legend()
    ax.set_title("Membrane potential over time")  # Optional: add title to the plot
    plt.show()


def get_folder(run_id):
    currdir=os.getcwd()
    print(currdir)
    dir=os.path.join(currdir,f"Extracellular_test\\Homogeneous_Efield\\data\\run{run_id}")
    path=""
    print(dir)
    return dir



# folder=get_folder(0)


# max_shift, max_v, min_v, results=cmax_shift(folder)
# plot_voltage(folder,results)
# print(results)
# print(max_shift)
# print(max_v)
# print(min_v)
