from pyNN.serialization import import_from_sonata, load_sonata_simulation_plan
import pyNN.nest as sim

simulation_plan = load_sonata_simulation_plan("../input/simulation_config.json")
simulation_plan.setup(sim)
net = import_from_sonata("../input/circuit_config.json", sim)

print dir(net)
print net.populations
print net.views
print net.projections

for proj in net.projections:
    print proj
    print proj.describe()


simulation_plan.execute(net)