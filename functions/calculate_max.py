from neuron import h
import numpy as np
import os
import csv 
import json 
import matplotlib.pyplot as plt
from . import maxv_shplot
import pandas as pd
import pickle 


def calc_max(cell,folder):

    # Initialize variables for tracking max/min values and corresponding segments
    results = {
        "max_v": 0,
        "min_v": 1e5,
        "max_seg": cell.soma(0.5),  # Default to soma
        "min_seg": cell.soma(0.5),
        "max_sec": cell.soma,  # Default to soma
        "min_sec": cell.soma
    }
    
    # Callback function to update max/min voltages
    # Works only for maximum (the min is always gonna be 0 - need to do a max_shift sort of function...)
    # Recover the maximum voltage shift for each segment...     
    # Make this just detect the max v and minimum v...
    
    def every_step():
        for sec in cell.all:
            for seg in sec:
                v_membrane=seg.v
                if v_membrane > results["max_v"]:
                    results["max_v"] = v_membrane
                    results["max_seg"] = seg
                    results["max_sec"] = sec
                elif v_membrane < results["min_v"]:
                    results["min_v"] = v_membrane
                    results["min_seg"] = seg
                    results["min_sec"] = sec
    
    # def save_results_pickle():
    #     path=os.path.join(folder,"results.pkl")
    #     with open(path, 'w') as file:
    #         pickle.dump(results, file)
    #     print(f"Results saved to {file}")

    # save_results_pickle()
    # data=pd.DataFrame(results)
    # data.to_csv(path,index=False)
    # Register the callback to execute at each simulation step
    # callback=h.beforestep_callback(cell.soma(0.5))
    # callback.set_callback(every_step)

    # Return results dictionary and callback for further use
    return results, every_step

def record_voltages(cell,folder):

    path=os.path.join(folder,f"run_voltages.csv")
    file= open(path,'w',newline='')
    writer = csv.writer(file)
    # Write header row with time and segment indexes
    # header = ["t"] + [f"{sec.name()}({i})" for sec in cell.all for i, _ in enumerate(sec)]
    header= ["t"] + [f"{seg}" for sec in cell.all for seg in sec]
    writer.writerow(header)

    def sum_voltages():
        current_voltages = [h.t] + [seg.v for sec in cell.all for seg in sec]
        writer.writerow(current_voltages) # Use writerow for single list
            
    # callback=h.beforestep_callback(cell.soma(0.5))
    # callback.set_callback(sum_voltages)

    return file,sum_voltages



#Making a function that adapts both (can't have multiple callbacks):

def master_callback(cell, folder, run_id,num=0):
    # Get max_shift functionality
    results={}
    results, every_step = calc_max(cell,folder)
    path=os.path.join(folder,f"run{run_id}_max.txt")

    with open(path,'w') as file:
        file.write(json.dumps(str(results)))

    # Get all_voltages functionality
    file, sum_voltages = record_voltages(cell, folder)


    # Master function that combines both callbacks
    if num==0:
        def combined_callback():
            every_step()
            sum_voltages()
    elif num==1:
        def combined_callback():
            every_step()
    elif num==2:
        def combined_callback():
            sum_voltages()



     # Register the combined callback
    callback = h.beforestep_callback(cell.soma(0.5))
    callback.set_callback(combined_callback)

    # Return the results and file object (to close it properly later)
    return results, file, callback


def max_and_current(cell,folder, run_id,chooser=0):
      # Initialize variables for tracking max/min values and corresponding segments
    results = {
        "max_v": h.v_init,
        "min_v": h.v_init,
        "max_seg": cell.soma(0.5),  # Default to soma
        "min_seg": cell.soma(0.5),
        "max_sec": cell.soma,  # Default to soma
        "min_sec": cell.soma
    }

    # Initialize save voltages over simulation
    path=os.path.join(folder,f"run{run_id}_voltages.csv")
    file= open(path,'w',newline='')
    writer = csv.writer(file)
    # Write header row with time and segment indexes
    header = ["t"] + [f"{sec.name()}({i})" for sec in cell.all for i, _ in enumerate(sec)]
    writer.writerow(header)

    # Callback function to update max/min voltages    
    def every_step():
        current_voltages = [h.t]
        for sec in cell.all:
            for seg in sec:
                v_membrane=seg.v
                current_voltages.append(v_membrane)
                if chooser==0:
                    if v_membrane > results["max_v"]:
                        results["max_v"] = v_membrane
                        results["max_seg"] = seg
                        results["max_sec"] = sec
                    elif v_membrane < results["min_v"]:
                        results["min_v"] = v_membrane
                        results["min_seg"] = seg
                        results["min_sec"] = sec
                writer.writerow(current_voltages) # Use writerow for single list

        callback = h.beforestep_callback(cell.soma(0.5))
        callback.set_callback(every_step)


def highlight_max_min_voltage(results,mode=0):
    """
    Highlights the segments with the maximum and minimum voltage on a shape plot.

    Parameters:
    results (dict): Output from the `max_shift` function, containing max/min voltage info.

    Returns:
    ps (h.PlotShape): The modified PlotShape object with highlighted locations.
    """
    if mode==0:
        ps = h.PlotShape(True)  # Create a PlotShape object
         # ps.variable("v")        # Set the variable to visualize (membrane voltage)
        ps.exec_menu("Shape Plot")  # Open the shape plot window
        ps.exec_menu("Show Diam")   # Optionally display diameters
        ps.exec_menu("View = plot")
    else:
        ps=ps = h.PlotShape(False)
        ps.variable("v")
        #ps.plot(plt)
        ps.show(0)
        # Highlight the segment with the maximum voltage
        if "max_seg" and "min_seg" in results:
            max_seg = results["max_seg"]
            min_seg = results["min_seg"]
            ps.plot(plt).mark(max_seg,"o").mark(min_seg,"xk")  # Red circle
            # ps.plot().mark(max_seg.x, max_seg.sec, 2, 6, 1)  # Red circle
            print(f"Max voltage: {results['max_v']} at section {max_seg.sec.name()}, x={max_seg.x}")
            print(f"Min voltage: {results['min_v']} at section {min_seg.sec.name()}, x={min_seg.x}")
        else:
            ps.plot(plt)
        plt.show()

    # # Testing with coloring sections
    # if "max_sec" in results:
    #     max_sec = results["max_sec"]
    #     ps.color(2,sec=max_sec)
    # if "min_sec" in results:
    #     min_sec = results["min_sec"]
    #     ps.color(3,sec=min_sec)

    return ps

