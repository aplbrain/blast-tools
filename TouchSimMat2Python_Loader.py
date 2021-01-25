"""
Christophe J. Brown
August 2020

Copyright 2020 The Johns Hopkins University Applied Physics Laboratory

Licensed under the MIT License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

https://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import numpy as np
from scipy.io import loadmat, matlab
import matplotlib.pyplot as plt
import os

## helper functions
def load_mat(filename):
    """
    This function should be called instead of direct scipy.io.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects
    from https://stackoverflow.com/questions/48970785/complex-matlab-struct-mat-file-read-by-python
    """

    def _check_vars(d):
        """
        Checks if entries in dictionary are mat-objects. If yes
        todict is called to change them to nested dictionaries
        """
        for key in d:
            if isinstance(d[key], matlab.mio5_params.mat_struct):
                d[key] = _todict(d[key])
            elif isinstance(d[key], np.ndarray):
                d[key] = _toarray(d[key])
        return d

    def _todict(matobj):
        """
        A recursive function which constructs from matobjects nested dictionaries
        """
        d = {}
        for strg in matobj._fieldnames:
            elem = matobj.__dict__[strg]
            if isinstance(elem, matlab.mio5_params.mat_struct):
                d[strg] = _todict(elem)
            elif isinstance(elem, np.ndarray):
                d[strg] = _toarray(elem)
            else:
                d[strg] = elem
        return d

    def _toarray(ndarray):
        """
        A recursive function which constructs ndarray from cellarrays
        (which are loaded as numpy ndarrays), recursing into the elements
        if they contain matobjects.
        """
        if ndarray.dtype != 'float64':
            elem_list = []
            for sub_elem in ndarray:
                if isinstance(sub_elem, matlab.mio5_params.mat_struct):
                    elem_list.append(_todict(sub_elem))
                elif isinstance(sub_elem, np.ndarray):
                    elem_list.append(_toarray(sub_elem))
                else:
                    elem_list.append(sub_elem)
            return np.array(elem_list)
        else:
            return ndarray

    data = loadmat(filename, struct_as_record=False, squeeze_me=True)
    return _check_vars(data)

def TouchSimMat2Python(data_dir,file):
    """
    Create a dictionary from a touchsim file that contains the file's spikes and metadata
    """
    print('loading ', file)
    datas = load_mat(str(data_dir + file))
    data_str = datas['r_strs']
    sensor_type = 'trq'
    if 'ftsn' in file:
        data_str = [data_str]  # hack to get single value into list
        sensor_type = 'ftsn'
    # print(data_str)
    # print(len(data_str))
    sensor_data = []
    for sensor in range(len(data_str)):
        data = data_str[sensor]
        affpop = data['affpop']
        responses = data['responses']
        stimulus = data['stimulus']  # doing anything with this?
        rates = data['rate']
        duration = data['duration']

        # generate a spikes array of n neurons x d time where the entries are 1 if a spike occurred at a specific timestamp (column index)
        dt = 1e4  # assume timestamps have 4 decimal places
        # numtimestamps = np.around(duration, decimals=4) * dt
        # numtimestamps = np.ceil(duration*1e5)/1e5*dt
        numtimestamps = np.ceil(duration*dt)+10
        spikes = np.zeros((rates.shape[0], int(numtimestamps)))  # TODO: this may be too big
        activeneuronidx = np.nonzero(rates)
        for activeneuron in activeneuronidx[0]:
            spikestamps = responses[activeneuron]['spikes']
            spikestamps = spikestamps * dt
            if np.isscalar(spikestamps):
                spikestamps = np.array([spikestamps])  # hack to account for 1 spike
            spikestamps = spikestamps.astype(int)
            for spikestamp in spikestamps:
                spikes[activeneuron, spikestamp] = 1
        # print(spikes)

        # generate a dictionary that maps neuron index to metadata (physical position of neuron, finger, neuron type, neuron parameters, etc)
        neuron_metadata = affpop[
            'afferents']  # metadata should conveniently be in afferent population from MATLAB already
        # print(neuron_metadata)

        # for i in range(len(neuron_metadata)):
        #     print(spikes[i, :])
        #     print(neuron_metadata[i])
        #     print(neuron_metadata[i]['class'])
        #     print(neuron_metadata[i]['parameters'])
        #     print(neuron_metadata[i]['location'])
        #     print(neuron_metadata[i]['depth'])
        #     print(neuron_metadata[i]['idx'])
        print('np array and metadata dictionary constructed for ', file, ', now creating dictionary with both')
        neuron_data = {}
        neuron_data['spikes'] = spikes
        neuron_data['metadata'] = neuron_metadata
        neuron_data['stimulus'] = stimulus
        neuron_data['rates'] = rates
        neuron_data['sensor_type'] = sensor_type
        neuron_data['sensor_no'] = sensor
        # neuron_data['spikes_stamps'] = responses['spikes'] # what if no spikes occured?
        sensor_data.append(neuron_data)
    return sensor_data

def TouchSimMatDir2Python(data_dir):
    """
    Create a dictionary from a directory full of touchsim files that uses a file's name as key and returns a
    subdictionary with the file's spikes and metadata as the value
    """
    data_dir_contents = os.listdir(data_dir)
    file_data={}
    for file in data_dir_contents:
        if 'mat' in file: # assume any .mat files are touchsim files for now
            file_data[file] = TouchSimMat2Python(data_dir,file)
        else:
            print('skipping ',file)
    # print(file_data)
    return file_data
