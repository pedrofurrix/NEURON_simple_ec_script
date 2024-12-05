import os
from neuron import h
import csv


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
            
    callback=h.beforestep_callback(cell.soma(0.5))
    callback.set_callback(sum_voltages)

    return file,callback