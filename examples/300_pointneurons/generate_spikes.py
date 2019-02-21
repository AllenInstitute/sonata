import os
from bmtk.utils.io.spike_trains import PoissonSpikesGenerator

if not os.path.exists('inputs'):
    os.mkdir('inputs')
psg = PoissonSpikesGenerator(range(100), 14.0, tstop=3000.0, precision=3)
psg.to_hdf5('inputs/external_spike_trains.h5')