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

import os
import re
import spiketrainanalysis as sta
import numpy as np


def compare_neuron(data_dir, trials, neuron1, neuron2, n_bins=30, trq_sensor_no=0, y_axis_limit=1, x_axis_limit=0):
    neuron1_dist = sta.trial_isi_probability_distribution(n_bins=n_bins,
                                                          data_dir=data_dir,
                                                          trial_filenames=trials,
                                                          trq_sensor_no=trq_sensor_no,
                                                          neuron_id=neuron1,
                                                          afferent_type=None,
                                                          y_axis_limit=y_axis_limit,
                                                          x_axis_limit=x_axis_limit)

    neuron2_dist = sta.trial_isi_probability_distribution(n_bins=n_bins,
                                                          data_dir=data_dir,
                                                          trial_filenames=trials,
                                                          trq_sensor_no=trq_sensor_no,
                                                          neuron_id=neuron2,
                                                          afferent_type=None,
                                                          y_axis_limit=y_axis_limit,
                                                          x_axis_limit=x_axis_limit)

    kl_divergence = sta.kl_divergence(p=neuron1_dist, q=neuron2_dist)
    return kl_divergence


def compare_afferent(data_dir, trials, afferent1, afferent2, n_bins=30, trq_sensor_no=0, y_axis_limit=1,
                     x_axis_limit=0):
    afferent1_dist = sta.trial_isi_probability_distribution(n_bins=n_bins,
                                                            data_dir=data_dir,
                                                            trial_filenames=trials,
                                                            trq_sensor_no=trq_sensor_no,
                                                            neuron_id=None,
                                                            afferent_type=afferent1,
                                                            y_axis_limit=y_axis_limit,
                                                            x_axis_limit=x_axis_limit)

    afferent2_dist = sta.trial_isi_probability_distribution(n_bins=n_bins,
                                                            data_dir=data_dir,
                                                            trial_filenames=trials,
                                                            trq_sensor_no=trq_sensor_no,
                                                            neuron_id=None,
                                                            afferent_type=afferent2,
                                                            y_axis_limit=y_axis_limit,
                                                            x_axis_limit=x_axis_limit)

    kl_divergence = sta.kl_divergence(p=afferent1_dist, q=afferent2_dist)
    return kl_divergence


def compare_response(data_dir, response_set1=[], response_set2=[], n_bins=30, neuron=None, afferent_type=None,
                     trq_sensor_no=0, y_axis_limit=1, x_axis_limit=0):
    response1_dist = sta.trial_isi_probability_distribution(n_bins=n_bins,
                                                            data_dir=data_dir,
                                                            trial_filenames=response_set1,
                                                            trq_sensor_no=trq_sensor_no,
                                                            neuron_id=neuron,
                                                            afferent_type=afferent_type,
                                                            y_axis_limit=y_axis_limit,
                                                            x_axis_limit=x_axis_limit)

    response2_dist = sta.trial_isi_probability_distribution(n_bins=n_bins,
                                                            data_dir=data_dir,
                                                            trial_filenames=response_set2,
                                                            trq_sensor_no=trq_sensor_no,
                                                            neuron_id=neuron,
                                                            afferent_type=afferent_type,
                                                            y_axis_limit=y_axis_limit,
                                                            x_axis_limit=x_axis_limit)

    kl_divergence = sta.kl_divergence(p=response1_dist, q=response2_dist)
    return kl_divergence


def compare_trial(data_dir, trial_set1=[], trial_set2=[], n_bins=30, neuron=None, afferent_type=None, trq_sensor_no=0,
                  y_axis_limit=1, x_axis_limit=0):
    trial1_dist = sta.trial_isi_probability_distribution(n_bins=n_bins,
                                                         data_dir=data_dir,
                                                         trial_filenames=trial_set1,
                                                         trq_sensor_no=trq_sensor_no,
                                                         neuron_id=neuron,
                                                         afferent_type=afferent_type,
                                                         y_axis_limit=y_axis_limit,
                                                         x_axis_limit=x_axis_limit)

    trial2_dist = sta.trial_isi_probability_distribution(n_bins=n_bins,
                                                         data_dir=data_dir,
                                                         trial_filenames=trial_set2,
                                                         trq_sensor_no=trq_sensor_no,
                                                         neuron_id=neuron,
                                                         afferent_type=afferent_type,
                                                         y_axis_limit=y_axis_limit,
                                                         x_axis_limit=x_axis_limit)

    kl_divergence = sta.kl_divergence(p=trial1_dist, q=trial2_dist)
    return kl_divergence


def compare_noise(noise_dir1, noise_dir2, noise_set1=[], noise_set2=[], n_bins=30, neuron=None, afferent_type=None,
                  trq_sensor_no=0, y_axis_limit=1, x_axis_limit=0):
    noise1_dist = sta.trial_isi_probability_distribution(n_bins=n_bins,
                                                         data_dir=noise_dir1,
                                                         trial_filenames=noise_set1,
                                                         trq_sensor_no=trq_sensor_no,
                                                         neuron_id=neuron,
                                                         afferent_type=afferent_type,
                                                         y_axis_limit=y_axis_limit,
                                                         x_axis_limit=x_axis_limit)

    noise2_dist = sta.trial_isi_probability_distribution(n_bins=n_bins,
                                                         data_dir=noise_dir2,
                                                         trial_filenames=noise_set2,
                                                         trq_sensor_no=trq_sensor_no,
                                                         neuron_id=neuron,
                                                         afferent_type=afferent_type,
                                                         y_axis_limit=y_axis_limit,
                                                         x_axis_limit=x_axis_limit)

    kl_divergence = sta.kl_divergence(p=noise1_dist, q=noise2_dist)
    return kl_divergence


def compare_location(data_dir, location_set=[], ref1=(0, 0), ref2=(0, 0), n_bins=30, neuron=None,
                     afferent_type=None, trq_sensor_no=0, y_axis_limit=1, x_axis_limit=0):
    distance_dist1 = sta.trial_distance_probabilty_distribution(data_dir=data_dir,
                                                                trial_filenames=location_set,
                                                                n_bins=n_bins,
                                                                reference_point=ref1,
                                                                trq_sensor_no=trq_sensor_no,
                                                                neuron_id=neuron,
                                                                afferent_type=afferent_type,
                                                                y_axis_limit=y_axis_limit,
                                                                x_axis_limit=x_axis_limit)

    distance_dist2 = sta.trial_distance_probabilty_distribution(data_dir=data_dir,
                                                                trial_filenames=location_set,
                                                                n_bins=n_bins,
                                                                reference_point=ref2,
                                                                trq_sensor_no=trq_sensor_no,
                                                                neuron_id=neuron,
                                                                afferent_type=afferent_type,
                                                                y_axis_limit=y_axis_limit,
                                                                x_axis_limit=x_axis_limit)

    kl_divergence = sta.kl_divergence(p=distance_dist1, q=distance_dist2)
    return kl_divergence


def trial_select(data_dir, noise=None, sensor=r'\w+', obj=r'\d+', dim=r'\d+', trial=r'\d+'):
    patterns = []
    if sensor is not None:
        [patterns.append(f'spikes_{sensor}')]
    if obj is not None:
        [patterns.append(f'object_{obj}')]
    if dim is not None:
        [patterns.append(f'dim_{dim}')]
    if trial is not None:
        [patterns.append(f'trial_{trial}')]

    trial_list = []
    noise_dir = ''

    if isinstance(noise, int) or isinstance(noise, np.integer):
        if noise < 0:
            noise = 'minus' + str(abs(noise))
        else:
            noise = 'noise_' + str(noise)

        for subdir, dirs, files in os.walk(data_dir):
            if re.search(noise, subdir):
                noise_dir = subdir
                for file in files:
                    if all(re.search(regex, file) for regex in patterns):
                        trial_list.append(file)
    else:
        for subdir, dirs, files in os.walk(data_dir):
            for file in files:
                if all(re.search(regex, file) for regex in patterns):
                    trial_list.append(file)

    return trial_list, noise_dir


"""
1) different neurons or different neuron types in a given file 
2) responses to different objects or dimension for a given neuron 
3) responses to the same object/dimension but different trials for a given neuron 
4) same neuron and experimental conditions but different SNRs
5) different locations for a given neuron type in a given file

"""
