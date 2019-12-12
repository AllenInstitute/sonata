set -e

rm -rf output/*

python run_pointnet.py

python plot_spikes.py "NEST via BMTK" &

sleep 2

rm -rf output/*

python run_PyNN.py

python plot_spikes.py "NEST via PyNN" &

sleep 2

rm -rf output/*

./run_pynml.jnmlnrn.sh

python plot_spikes.py "NEURON via pyNeuroML" &

sleep 2



