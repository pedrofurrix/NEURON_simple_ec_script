import pandas as pd
from neuron import h

def savedata(id,t,soma_v,dend_v,v_extracellular,is_xtra,vrec):
    filename=f"run{id}"
    path="./data/"+ filename
    data=pd.DataFrame({"t":t,"soma_v":soma_v,"dend_v":dend_v,"v_extracellular":v_extracellular,"is_xtra":is_xtra,"vrec":vrec})
    data.to_csv(path,index=False)

def saveparams(id,cell):
    filename=f"params{id}.txt"
    path="./data/"+ filename
    with open(path, "w") as file:
    # Write the header
        file.write("x   y   z   rx\n")
        for sec in cell.all:
            if h.ismembrane("xtra"):
                for seg in sec:
                    x = seg.x_xtra
                    y = seg.y_xtra
                    z = seg.z_xtra
                    rx = seg.rx_xtra
                    # Write the values to the file
                    file.write(f"{x} {y} {z} {rx}\n")

