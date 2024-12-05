from neuron import h
import os

def base_shape():
    shape=h.Shape(False)
    shape.show(0) # Show Diameter
    h.load_file("./functions/anatscale.hoc")
    shape.view(-1568.93, -1200, 2837.86, 1700, 607, 93, 530, 320)
    shape.exec_menu("View=plot")

    return shape

def save_plot(shape,folder,run_id):
    savefile=f"run{run_id}_shplot.eps"
    path=os.path.join(folder,savefile)
    shape.printfile(savefile)


