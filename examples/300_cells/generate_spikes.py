import os
from bmtk.utils.reports.spike_trains import PoissonSpikeGenerator

if not os.path.exists('inputs'):
    os.mkdir('inputs')

psg = PoissonSpikeGenerator(population='external')
psg.add(node_ids=range(100), firing_rate=10.0, )
psg.add(node_ids=range(100), firing_rate=10.0, times=(0.0, 3.0))
psg.to_sonata('inputs/external_spike_trains.h5')
