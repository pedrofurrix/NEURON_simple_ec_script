from neuron import h
import numpy as np
import matplotlib.pyplot as plt

gvec = h.Vector(6) # gradient--0 when field off, nonzero when on
tvec = h.Vector(6)
#gvec.play(h._ref_is_xtra, tvec, 1) # interpolated play #basically, the is_xtra variable will get the gvec(index) value at tvec(index)

#ton is starting point
#dur is the duration of the stimulus
#grad is the amplitude

def makestim(ton, dur, grad):
  tvec.from_python([0, ton, ton,      ton+dur,  ton+dur, ton+dur+1])
  # 1e3 ensures that grad = 1 produces potential gradient 1 mv/um
  gvec.from_python([0, 0,   grad, grad, 0,       0])


def stimplay(ton,dur,grad,simtime):
  makestim(ton,dur,grad)
  gvec.play(h._ref_is_xtra, tvec, 1)
  plotvector(gvec,tvec,simtime,grad)

def stimplay2(ton,dur,grad): #two-part stimulation, with part positive and part negative
  gvec.resize(8)
  tvec.resize(8)
  tvec.from_python([0, ton, ton, ton+dur/2, ton+dur/2, ton+dur, ton+dur, ton+dur+1])
  gvec.from_python([0, 0,   grad, grad,-grad,-grad, 0,       0])
  gvec.play(h._ref_is_xtra, tvec, 1)

'''
def setupstims(cell):
  fsquare=h.Fsquare(cell.soma(0.5))
  fzap=h.Fzap(cell.soma(0.5))
  fsquare._ref_x= h._ref_is_xtra
  fzap._ref_x= dummy
  '''



def squarestim(cell,ton,dp,num,amp1,amp2):
  fsquare=h.Fsquare(cell.soma(0.5))
  #fsquare.x= h._ref_is_xtra
  h("setpointer fsquare.x, is_xtra")
  
  #h.setpointer(fsquare._ref_x,h._ref_is_xtra) #chatgpt suggestion - testing 
  #ton  time at which first cycle starts
  #dp   duration of a phase (duration of a half cycle)
  #num  number of cycles
  #amp1 level for first half cycle
  #amp2 level for second half cycle
  id=2
  fsquare.ton=ton
  fsquare.dp=dp
  fsquare.num=num
  fsquare.amp1=amp1
  fsquare.amp2=amp2
  global fsquarex
  fsquarex=h.Vector().record(fsquare._ref_x) #try to record the values of x #is kinda buggy with the other one - can write a plot(x) function
  return(id)

def sinstim(cell,ton,nc,f0,amp):
  fzap=h.Fzap(cell.soma(0.5))
  fzap._ref_x=h._ref_is_xtra #this is the syntax they use in tstpnt1.py
  #h.setpointer(h._ref_is_xtra, 'x',fzap)S
  #h("setpointer fzap.x, is_xtra") #try to use the HOC function they use in 239006

  #tp 	duration of a single phase of square or sine wave
  #nc 	number of full cycles of sine wave
  #f0   initial frequency
  #f1   final frequencys
  #amp  amplitude
  id=1
  tp=1/(f0*2)
  fzap.ton = ton #1
  fzap.dur = tp*nc*2 #TP*2*NC
  fzap.f0 = f0  #1000/2/TP
  fzap.f1 = fzap.f0
  fzap.amp=amp
  #global fzapx
  #fzapx=h.Vector().record(fzap._ref_x) #try to record the values of x #is kinda buggy with the other one - can write a plot(x) function
  #return(id)

def plotx(id,t):
  plt.Figure()
  if id==1:
    plt.plot(t,fzapx)
    plt.xlabel("time(ms)")
    plt.ylabel("fzapx")
  elif id==2:
    plt.plot(t,fsquarex)
    plt.xlabel("time(ms)")
    plt.ylabel("fsquarex")
  plt.show()


  




#amp in A, dt,dur and simtime in ms, freq in Hz
#similar to the method that we see in Mirzakhalili-et-al--CellSystems-2020
def playsin(amp,dt,dur,simtime,freq):
  times=np.arange(0,dur+dt,dt)
  # 1000 is a factor because dt is in ms and freq in Hz
  stim=amp*np.sin(2*np.pi*freq/1000*times)
  #Making the vectors and resizing to ensure that the stimulation is 0 when it ends.
  t=h.Vector(times)
  stim1=h.Vector(stim*1e-3)
  if dur<simtime:
    t.resize(len(times)+1)
    t.x[len(times)]=dur
    stim1.resize(len(stim) + 1)
    stim1.x[len(stim)] = 0  # Set the last value to 0 to ensure it goes to 0 when stimulation ends
  stim1.play(h._ref_is_xtra,t,1)


 #amp in A, dt and tstop in ms, freq in Hz
  #similar to the method that we see in Mirzakhalili-et-al--CellSystems-2020
def simpleplaysin(amp,dt,tstop,freq):
  times=np.arange(0,tstop+dt,dt)
  print("Times array:", times)
  print("Length of times array:", len(times))
  # 1000 is a factor because dt is in ms and freq in Hz
  stim=amp*np.sin(2*np.pi*freq/1000*times)
 # print(stim)
  #Making the vectors and resizing to ensure that the stimulation is 0 when it ends.
  t=h.Vector(times)
  #stim1=h.Vector(stim*1e-3)#see what this factor is for...#prob cause the amp is supposed to be in A/V
  stim1=h.Vector(stim)
  print("Length of NEURON time vector:", t.size())
  print("Length of NEURON stim vector:", stim1.size())
  print(list(t))
  print(list(stim1))
  stim1.play(h._ref_is_xtra,t,0)



def plotvector(vec,tvec,simtime,amp):
  g=h.Graph()
  g.size(0, simtime, -amp, amp) # Set the size of the graph (x-axis min/max, y-axis min/max)
  #g.size(0,10,-1,1)
  vec.plot(g,tvec)
  g.exec_menu("View = plot")
  