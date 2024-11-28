# Import neuron
from neuron import h

# Import Mechanisms
import os
current_directory = os.getcwd()
print(current_directory)
path = os.path.join(current_directory, "mechanisms", "nrnmech.dll")
print(path)
h.nrn_load_dll(path)

# Import utilities 
from neuron.units import ms,mV,um,V,m 
import matplotlib.pyplot as plt 
import numpy as np 
h.load_file("stdrun.hoc")
h.cvode_active(0) #turn off variable time step
# h.load_file("anatscale.hoc")


#Local Field Potential calculation
#h.load_file("./functions/field.hoc")

##### Import cell model
from functions.ballandstick import BallAndStick,BallAndStick_pas
cell=BallAndStick(0,0,0,0,0,0)
print(cell.soma.nseg,cell.dend.nseg)

# Interpolate and set pointers between xtra and extracellular
h.load_file("./functions/interpxyz.hoc")
h.load_file("./functions/setpointers.hoc")



from functions.calcrx import setelec,homogenous,set_uniform_field_between_plates

v_plate=40*V #- potential difference between the plates
distance=1*m #distance
field_orientation=np.array([1,0,0])#along the x axis
ref_point=[0,0,0] #reference point with a 0 e_extracellular

set_uniform_field_between_plates(v_plate,distance,field_orientation,ref_point)


dt=1*ms
simtime=1000*ms
depth=0
modfreq=0
v_init=-65*mV

h.dt=dt
h.v_init=v_init


import functions.stim as stim
ton=20
amp=1000
dur=900
freq=10
depth=1
modfreq=5
times,stim1=stim.ampmodulation_wiki(ton,amp,depth,dt,dur,simtime,freq,modfreq)



t=h.Vector().record(h._ref_t)
is_xtra=h.Vector().record(h._ref_is_xtra)
soma_v=h.Vector().record(cell.soma(0.5)._ref_v)
dend_v=h.Vector().record(cell.dend(0.5)._ref_v)
extracellular_v_soma = h.Vector().record(cell.soma(0.5)._ref_vext[0])



from functions.shapeplot_movie import movie_v

callback=movie_v(cell)

h.load_file("movierun.hoc")

h.movierun()