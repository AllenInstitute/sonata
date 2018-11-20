import os

import numpy
import h5py
import pytest

output_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        'output'))

dt = 0.025
tstop = 60.0
stim_start = 20.0
stim_end = 50.0

start_voltage = -80.0
end_voltage = -20.0

# Using as 'raw' code as possible here, so as not to depend on other code
# that could contain errors


def test_soma_voltage():
    """Check soma voltages"""

    soma_voltage_path = os.path.join(output_path, 'membrane_potential.h5')

    assert os.path.exists(soma_voltage_path)

    voltage = h5py.File(soma_voltage_path)['data'].value

    assert len(voltage) == tstop / dt

    time = numpy.arange(0, len(voltage)) * dt

    soma_voltage_path = os.path.join(output_path, 'membrane_potential.h5')

    assert os.path.exists(soma_voltage_path)
    assert voltage[0] == pytest.approx(start_voltage)
    assert numpy.mean(
        voltage[
            numpy.where(time < stim_start)]) == pytest.approx(start_voltage)
    assert start_voltage < numpy.mean(voltage[numpy.where(
        (time >= stim_start) & (time <= stim_end))]) < end_voltage
    assert voltage[-1] == pytest.approx(end_voltage)


def test_spikes():
    """Check spike times"""

    spikes_path = os.path.join(output_path, 'spikes.h5')

    assert os.path.exists(spikes_path)

    spikes = h5py.File(spikes_path)['spikes']['timestamps'].value

    assert len(spikes) == 0
