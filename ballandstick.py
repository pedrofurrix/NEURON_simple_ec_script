from neuron import h
from neuron.units import ms, mV

class Cell:
    def __init__(self, gid, x, y, z, theta,nseg):
        self._gid = gid
        self._setup_morphology()
        self.all = self.soma.wholetree()
        self._discretize()
        self._setup_biophysics()
        self.x = self.y = self.z = 0
        h.define_shape()
        self._rotate_z(theta)
        self._set_position(x, y, z)
        # Spike detector - register the spikes associated with the cell
        # can look to plot them in a scatter plot.
        self._spike_detector = h.NetCon(self.soma(0.5)._ref_v, None, sec=self.soma)
        self.spike_times = h.Vector()
        self._spike_detector.record(self.spike_times)

        self._ncs = []

        self.soma_v = h.Vector().record(self.soma(0.5)._ref_v)

    def _discretize(self):
        '''for sec in  self.all:
            sec.nseg=nseg'''
        import dlambda
        dlambda.geom_nseg(self)

    def __repr__(self):
        return "{}[{}]".format(self.name, self._gid)

    def _set_position(self, x, y, z): #this was basically already done before #can try it with this specification of coordinates
        for sec in self.all:
            for i in range(sec.n3d()):
                sec.pt3dchange(
                    i,
                    x - self.x + sec.x3d(i),
                    y - self.y + sec.y3d(i),
                    z - self.z + sec.z3d(i),
                    sec.diam3d(i),
                )
        self.x, self.y, self.z = x, y, z

    def _rotate_z(self, theta):
        """Rotate the cell about the Z axis."""
        for sec in self.all:
            for i in range(sec.n3d()):
                x = sec.x3d(i)
                y = sec.y3d(i)
                c = h.cos(theta)
                s = h.sin(theta)
                xprime = x * c - y * s
                yprime = x * s + y * c
                sec.pt3dchange(i, xprime, yprime, sec.z3d(i), sec.diam3d(i))

class BallAndStick(Cell):
    name = "BallAndStick"

    def _setup_morphology(self):
        self.soma = h.Section(name="soma", cell=self)
        self.dend = h.Section(name="dend", cell=self)
        self.dend.connect(self.soma)
        self.soma.L = self.soma.diam = 12.6157
        self.dend.L = 200
        self.dend.diam = 1


    def _setup_biophysics(self):
        for sec in self.all:
            sec.Ra = 100  # Axial resistance in Ohm * cm
            sec.cm = 1  # Membrane capacitance in micro Farads / cm^2
            sec.insert("hh")
            sec.insert("extracellular")
            sec.insert('xtra')
            for seg in sec:
                seg.hh.gnabar = 0.12 if sec==self.soma else 0 # Sodium conductance in S/cm2
                seg.hh.gkbar = 0.036  if sec==self.soma else 0 # Potassium conductance in S/cm2
               # seg.hh.gl = 0.0003  # Leak conductance in S/cm2
               # seg.hh.el = -54.3  # Reversal potential in mV  #Why did I make these modifications????
                #seg.xtra._ref_im = seg._ref_i_membrane #set pointers #Replaced by setpointers
                #seg.xtra._ref_ex = seg._ref_e_extracellular
        # Insert passive current in the dendrite
        #for seg in self.dend:
           # seg.pas.g = 0.001  # Passive conductance in S/cm2
           # seg.pas.e = -65  # Leak reversal potential mV

        # NEW: the synapse - definimos a localização da sinapse em cada célula da classe ball and stick
        self.syn = h.ExpSyn(self.dend(0.5))
        self.syn.tau = 2 * ms


class BallAndStick_pas(Cell):
    name = "BallAndStick"

    def _setup_morphology(self):
        self.soma = h.Section(name="soma", cell=self)
        self.dend = h.Section(name="dend", cell=self)
        self.dend.connect(self.soma)
        self.soma.L = self.soma.diam = 12.6157
        self.dend.L = 200
        self.dend.diam = 1

    def _setup_biophysics(self):
        for sec in self.all:
            sec.Ra = 100  # Axial resistance in Ohm * cm
            sec.cm = 1  # Membrane capacitance in micro Farads / cm^2
            sec.insert("extracellular")
            sec.insert('xtra')
        self.soma.insert("hh")
        for seg in self.soma:
            seg.hh.gnabar = 0.12  # Sodium conductance in S/cm2
            seg.hh.gkbar = 0.036  # Potassium conductance in S/cm2
            seg.hh.gl = 0.0003  # Leak conductance in S/cm2
            seg.hh.el = -54.3  # Reversal potential in mV
            #seg.xtra._ref_im = seg._ref_i_membrane #set pointers
            #seg.xtra._ref_ex = seg._ref_e_extracellular
        # Insert passive current in the dendrite
        self.dend.insert("pas")
        for seg in self.dend:
            seg.pas.g = 0.0001  # Passive conductance in S/cm2
            seg.pas.e = -65  # Leak reversal potential mV

        # NEW: the synapse - definimos a localização da sinapse em cada célula da classe ball and stick
        self.syn = h.ExpSyn(self.dend(0.5))
        self.syn.tau = 2 * ms
