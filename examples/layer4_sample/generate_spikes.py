import os
from bmtk.utils.io.spike_trains import PoissonSpikesGenerator

if not os.path.exists('inputs'):
    os.mkdir('inputs')
psg = PoissonSpikesGenerator(range(9000), 15.0, tstop=3000.0)
psg.to_hdf5('inputs/lgn_spike_trains.h5')