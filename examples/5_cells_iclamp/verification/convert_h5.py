import os
import json
from pprint import pprint
from xml.etree import ElementTree


def parse_value(val):
    return float(val.split(' ')[0])


def convert(nml_file, output_json):
    params_dict = {'soma': [], 'dend': [], 'apic': [], 'axon': [], 'all': [], 'e_pas': {}}
    soma_ek = None
    soma_ena = None

    nml_root = ElementTree.parse(nml_file).getroot()
    for elem in nml_root.iter():
        attr = elem.attrib
        sec = attr.get('segmentGroup', None)

        if 'channelDensity' in elem.tag:
            name = attr['id']
            mechanism = attr['ionChannel']
            value = parse_value(attr['condDensity'])
            if mechanism == 'pas':
                params_dict[sec].append({'name': 'g_pas', 'value': value})
                params_dict['e_pas'][sec] = parse_value(attr['erev'])
            else:
                params_dict[sec].append({'name': name, 'value': value, 'mechanism': mechanism})

            if attr['ion'] == 'k':
                soma_ek = parse_value(attr['erev'])

            if attr['ion'] == 'na':
                soma_ena = parse_value(attr['erev'])

        elif 'specificCapacitance' in elem.tag:
            value = parse_value(attr['value'])
            params_dict[sec].append({'name': 'cm', 'value': value})

        elif 'resistivity' in elem.tag:
            value = parse_value(attr['value'])
            params_dict[sec].append({'name': 'Ra', 'value': value})

        elif 'concentrationModel' in elem.tag:
            decay = parse_value(attr['decay'])
            gamma = parse_value(attr['gamma'])
            params_dict[sec].append({'name': 'decay_CaDynamics', 'value': decay, 'mechanism': 'CaDynamics'})
            params_dict[sec].append({'name': 'gamma_CaDynamics', 'value': gamma, 'mechanism': 'CaDynamics'})

    for p in params_dict['all']:
        for sec in ['soma', 'dend', 'apic', 'axon']:
            params_dict[sec].append(p)
    del params_dict['all']

    if soma_ek is not None:
        params_dict['soma'].append({'name': 'ek', 'value': soma_ek})

    if soma_ena is not None:
        params_dict['soma'].append({'name': 'ena', 'value': soma_ena})

    # pprint(params_dict)
    with open(output_json, 'w') as json_file:
        json.dump(params_dict, json_file, indent=2)

cells = [
    # [gid, model id, cre-line]
    [0, 472363762, 'Scnn1a'],
    [1, 473863510, 'Rorb'],
    [2, 473863035, 'Nr5a1'],
    [3, 472912177, 'PV1'],
    [4, 473862421, 'PV2']
]

for cell in cells:
    nml_file = os.path.join('../components/biophysical_neuron_templates/nml', 'Cell_{}.cell.nml'.format(cell[1]))
    output_json = 'model_gid{}_{}_{}.json'.format(*cell)
    convert(nml_file, output_json)


