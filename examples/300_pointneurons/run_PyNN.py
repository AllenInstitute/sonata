from pyNN.serialization import import_from_sonata, load_sonata_simulation_plan
import pyNN.nest as sim

simulation_plan = load_sonata_simulation_plan("simulation_config.json")
simulation_plan.setup(sim)
net = import_from_sonata("circuit_config.json", sim)
simulation_plan.execute(net)