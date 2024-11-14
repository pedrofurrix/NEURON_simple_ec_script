from neuron import h
from neuron.units import um,mV,ms
class Cell:
    def __init__(self, gid, x, y, z, theta,nseg=0): 
        self._gid = gid
        self._setup_morphology()
        self.all = self.soma.wholetree()
        self._discretize(nseg)
        self._setup_biophysics()
        self.x = self.y = self.z = 0
        h.define_shape()
        self._rotate_z(theta) 
        self._set_position(x, y, z) #x,y,z are in um
        # Spike detector - register the spikes associated with the cell
        # can look to plot them in a scatter plot.
        self._spike_detector = h.NetCon(self.soma(0.5)._ref_v, None, sec=self.soma)
        self.spike_times = h.Vector()
        self._spike_detector.record(self.spike_times)

        self._ncs = []

        self.soma_v = h.Vector().record(self.soma(0.5)._ref_v)

    def _discretize(self,nseg):
        if nseg==0:
            for sec in self.all:
                import dlambda
                dlambda.geom_nseg(self)
             
        else:
            for sec in self.all:
                sec.nseg=nseg

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


class Fast_Spiking(Cell):
   
    # Single-compartment model of "fast-spiking" cortical neurons,
    #     which is the most commonly encountered electrophysiological type
    #     of inhibitory (interneuron) cell in cortex.  The model is based
	# on the presence of two voltage-dependent currents: 
    #     - INa, IK: action potentials
	# (no spike-frequency adaptation in this model)
    '''
        #  Model described in:

        #    Pospischil, M., Toledo-Rodriguez, M., Monier, C., Piwkowska, Z., 
        #    Bal, T., Fregnac, Y., Markram, H. and Destexhe, A.
        #    Minimal Hodgkin-Huxley type models for different classes of
        #    cortical and thalamic neurons.
        #    Biological Cybernetics 99: 427-441, 2008.

        #   The model was taken from a thalamocortical model, described in:

        #    Destexhe, A., Contreras, D. and Steriade, M.
        #    Mechanisms underlying the synchronizing action of corticothalamic
        #    feedback through inhibition of thalamic relay cells.
        #    J. Neurophysiol. 79: 999-1016, 1998.


        #         Alain Destexhe, CNRS, 2009
        # 	http://cns.iaf.cnrs-gif.fr
    '''

    name = "Fast Spiking"
    
    def _setup_morphology(self):
        self.soma = h.Section(name="soma", cell=self)
        # self.dend = h.Section(name="dend", cell=self)
        # self.dend.connect(self.soma)
        self.soma.L = self.soma.diam = 67*um #so area is about 14000 um2
        # self.dend.L = 200*um
        # self.dend.diam = 1*um

    def _setup_biophysics(self):
        for sec in self.all:
            sec.Ra = 100  # Axial resistance in Ohm * cm
            sec.cm = 1  # Membrane capacitance in micro Farads / cm^2
            sec.insert("pas")
            sec.insert("extracellular")
            sec.insert('xtra')
            sec.insert('hh2')
            sec.ek=100*mV
            sec.ena=50*mV
            for seg in sec: 
                seg.hh.gnabar = 0.12 if sec==self.soma else 0 # Sodium conductance in S/cm2
                seg.hh.gkbar = 0.036  if sec==self.soma else 0 # Potassium conductance in S/cm2
                # seg.hh.gl = 0.0003  # Leak conductance in S/cm2
                # seg.hh.el = -54.3  # Reversal potential in mV 
                seg.pas.g =0.00015	  # Passive conductance in S/cm2 #Rin = 48Meg
                # // conversion with McC units: 
                # // g(S/cm2) = g(nS)*1e-9/29000e-8
                # //	    = g(nS) * 3.45e-
                seg.pas.e = -70  # Leak reversal potential mV
                # HH parameters
                seg.hh2.vtraub=-55  # resting Vm, BJ was -55
                seg.hh2.gnabar=0.05 # McCormick=15 muS, thal was 0.09
                # gkbar_hh2 = 0.007	# McCormick=2 muS, thal was 0.01
                # gkbar_hh2 = 0.004
	            seg.hh2.gkbar = 0.01	# spike duration of interneurons

         # NEW: the synapse - definimos a localização da sinapse em cada célula da classe ball and stick
        self.syn = h.ExpSyn(self.dend(0.5))
        self.syn.tau = 2 * ms