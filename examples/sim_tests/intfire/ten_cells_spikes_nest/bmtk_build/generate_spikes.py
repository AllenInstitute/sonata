import os
from bmtk.utils.io.spike_trains import PoissonSpikesGenerator

psg = PoissonSpikesGenerator(range(5), 10.0, tstop=200.0)
psg.to_hdf5('../input/external_spike_trains.h5')
