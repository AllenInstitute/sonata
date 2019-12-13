set -e

rm -rf output/*

python build_network.py
python run_bionet.py

python plot_spikes.py "NEURON via BMTK" &

sleep 2

###rm -rf output/*  # script below generates output/comparison_raster.png for easy comparison...

python run_netpyne.py

cp netpyne_spikes.h5 output/spikes.h5

python plot_spikes.py "NEURON via NetPyNE" &



