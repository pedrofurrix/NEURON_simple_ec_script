from neuron import h,gui
import os
import pickle

import sys
sys.path.append(r"C:\Users\Pc\Documents\Charite\NEURON")

import os
current_directory = os.getcwd()
print(current_directory)
path = os.path.join(current_directory,"Extracellular_test","Homogeneous_EField", "mechanisms", "nrnmech.dll")
print(path)
h.nrn_load_dll(path)

from Extracellular_test.Homogeneous_Efield.functions import ballandstick
cell=ballandstick.BallAndStick2(0,0,0,0,0,0) #doesn't work in regular python...
def base_shape():
    shape=h.Shape(False)
    shape.show(0) # Show Diameter
    h.load_file("Extracellular_test/Homogeneous_Efield/functions/anatscale.hoc")
    shape.view(-1568.93, -1200, 2837.86, 1700, 607, 93, 530, 320)
    shape.exec_menu("View=plot")
    return shape

def save_plot(shape,folder,run_id):
    savefile=f"run{run_id}_shplot.eps"
    path=os.path.join(folder,savefile)
    shape.printfile(savefile)
# Work with the Shape object from base_shape.py

def load_results(run_id):
    from Extracellular_test.Homogeneous_Efield.functions.post_processing import max_minshift 
    folder=max_minshift.get_folder(run_id)
    file=os.path.join(folder,"results.pkl")
    # Open the pickle file and load the results

    with open(file, "rb") as f:
        results = pickle.load(f)  # Load the results from the file

    print(results)
    return results

def max_min_shape(shape,run_id):
    """
    Highlights the segments with the maximum and minimum voltage on a shape plot.

    Parameters:
    results (dict): Output from the `max_shift` function, containing max/min voltage info.

    """
    # ps=ps = h.PlotShape(False)
    # ps.variable("v")
    # #ps.plot(plt)
    # ps.show(0)
    # Highlight the segment with the maximum voltage
    results=load_results(run_id)

    if "max_seg" and "min_seg" in results:
        max_seg = results["max_seg"]
        min_seg = results["min_seg"]
        mark_max=h.IClamp(max_seg)
        mark_min=h.IClamp(min_seg)
        shape.point_mark(mark_max,1,"S",5)
        shape.point_mark(mark_min,2,"T",5)
        shape.exec_menu("View=plot")
        # ps.plot().mark(max_seg.x, max_seg.sec, 2, 6, 1)  # Red circle
        print(f"Max shift: {results['max_v']} at section {max_seg.sec.name()}, x={max_seg.x}")
        print(f"Min shift: {results['min_v']} at section {min_seg.sec.name()}, x={min_seg.x}")
        shape.label("Max and Min voltage segments")

    # # Testing with coloring sections
    # if "max_sec" in results:
    #     max_sec = results["max_sec"]
    #     ps.color(2,sec=max_sec)
    # if "min_sec" in results:
    #     min_sec = results["min_sec"]
    #     ps.color(3,sec=min_sec)

    return mark_max, mark_min

shape=base_shape()

mark_max, mark_min=max_min_shape(shape,0)

a=input()