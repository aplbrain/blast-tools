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
import numpy as np
import scipy.stats as ss
from matplotlib import pyplot as plt
from TouchSimMat2Python_Loader import *


def calculate_magnitude(neuron_x, neuron_y, center_x=0, center_y=0):
    return np.sqrt((neuron_x - center_x) ** 2 + (neuron_y - center_y) ** 2)


def flatten_arrays(arrays):
    """
    Function flattens a list of numpy arrays
    Accepts a single tuple of numpy arrays
    """
    data = np.array(())

    for array in arrays:  # sa ra pc
        for neuron in array:  # 0 1 2 3 in list
            data = np.hstack((data, neuron))

    return data


def get_afferent_ranges(afferent_stats):
    """
    Function gets the neuron IDs that correspond to SA, RA, and PC neurons
    (caluated in calculate_afferet_isi_stats())
    """
    sa_range = afferent_stats['sa']['id_range']
    ra_range = afferent_stats['ra']['id_range']
    pc_range = afferent_stats['pc']['id_range']

    return sa_range, ra_range, pc_range


def get_afferent_type(neuron_id, afferent_stats):
    """
    Function retrieves the type of afferent for a given neuron within a set of afferent_stats
    """
    sa_range, ra_range, pc_range = get_afferent_ranges(afferent_stats)

    if neuron_id in sa_range:
        afferent_type = 'sa'
    elif neuron_id in ra_range:
        afferent_type = 'ra'
    elif neuron_id in pc_range:
        afferent_type = 'pc'
    else:
        print('Error - neuron_id does not correspond to SA, RA, or PC neuron.')

    return afferent_type


def get_neuron_counts(afferent_stats):
    """
    Function gets the total number of neurons per afferent type
    """
    sa_total = afferent_stats['sa']['neuron_count']
    ra_total = afferent_stats['ra']['neuron_count']
    pc_total = afferent_stats['pc']['neuron_count']

    return sa_total, ra_total, pc_total


def get_spike_deltas(afferent_stats):
    """
    Function returns 1D array for each type of afferent.
    The returned array represents the times in between neuron spikes
    """
    sa_deltas = afferent_stats['sa']['spike_deltas']
    ra_deltas = afferent_stats['ra']['spike_deltas']
    pc_deltas = afferent_stats['pc']['spike_deltas']

    return sa_deltas, ra_deltas, pc_deltas


def calculate_spike_deltas(neuron_fire_count, spike_times):
    """
    Function accepts a list of spike times and computes the inter-spike time deltas
    and returns them as a list
    """
    time_deltas_for_neuron_k = []

    for k in range(1, neuron_fire_count):  # Start at idx=1 to compute index k-1=0
        inter_spike_delta = spike_times[k] - spike_times[k - 1]
        time_deltas_for_neuron_k.append(inter_spike_delta)

    return time_deltas_for_neuron_k


def neuron_spiked(i, afferent_stats):
    """
    Function checks if a neuron had > 0 ISIs. Returns true if there was at least one spike delta
    :param i:
    :param afferent_stats:
    :return:
    """
    afferent_type = get_afferent_type(i, afferent_stats)
    spike_deltas = afferent_stats[afferent_type]['spike_deltas']
    spiked = len(spike_deltas[i]) > 0
    # print(f'i={i}. Length = {len(spike_deltas[i])}. Spiked? {spiked} ')

    return spiked


def load_isi_stats(data_dir, file):
    """
    Function accepts a data_dir directory to search for a file to convert from matlab to python data types
    :param data_dir: directory to search from (nesting is allowed by caller function,
    see trial_isi_probability_distribution().)
    :param file:
    :return:
    """
    file_data = TouchSimMat2Python(data_dir, file)

    sensors = []

    for sensor in file_data:  # parse all sensors in case of trq file
        afferent_stats = calculate_afferet_isi_stats(sensor['spikes'],
                                                     sensor['metadata'],
                                                     sensor['sensor_no'])
        sensors.append(afferent_stats)

    return sensors


def calculate_afferet_isi_stats(spikes, metadata, sensor_no):
    """
    Function accepts matlab data [i.e. TouchSimMat2Python()]
    and produces a nested dictionary containing the following (each for SA, RA, and PC afferents):
    :param id_range:     Range of neuron IDs corresponding to the afferent type; list
    :param isi:          Average ISI for each type of afferent neuron; {neuron_id, int}
    :param fire_count:   The firing count of each neuron (organized by afferent type); {neuron_id, int}
    :param spike_deltas: All inter-spike times for a neuron that fired; {neuron_id, list}
    :param neuron_count: Amount of neurons of this afferent type (i.e. the length of id_range); int
    """

    neuron_count = spikes.shape[0]

    # print(f'neuron count = {neuron_count}')

    afferent_stats = {}
    afferent_stats['sa'] = {}
    afferent_stats['sa']['id_range'] = []  # Store what neuron ID range corresponds to an afferent
    afferent_stats['sa']['isi'] = {}  # Average ISI for each neuron {id, avg_isi}
    afferent_stats['sa']['fire_count'] = {}  # Total quanitiy of nerve firings per neuron {id, firings}
    afferent_stats['sa']['spike_deltas'] = [0] * neuron_count  # Lists of the time deltas between neuron spikes
    afferent_stats['sa']['neuron_count'] = 0  # Number of afferent neurons (length of id_range)
    afferent_stats['sa']['locations'] = np.zeros((neuron_count, 2))  # Array of the neuron coordinates

    afferent_stats['ra'] = {}
    afferent_stats['ra']['id_range'] = []
    afferent_stats['ra']['isi'] = {}
    afferent_stats['ra']['fire_count'] = {}
    afferent_stats['ra']['spike_deltas'] = [0] * neuron_count
    afferent_stats['ra']['neuron_count'] = 0
    afferent_stats['ra']['locations'] = np.zeros((neuron_count, 2))

    afferent_stats['pc'] = {}
    afferent_stats['pc']['id_range'] = []
    afferent_stats['pc']['isi'] = {}
    afferent_stats['pc']['fire_count'] = {}
    afferent_stats['pc']['spike_deltas'] = [0] * neuron_count
    afferent_stats['pc']['neuron_count'] = 0
    afferent_stats['pc']['locations'] = np.zeros((neuron_count, 2))

    for i in range(neuron_count):  # iterate over every neuron
        nonzero_spikes = np.nonzero(spikes[i, :])[0]  # Remove indices where neuron didn't spike
        spike_times = nonzero_spikes / 1e4  # Convert array to spike timestamps
        neuron_fire_count = spike_times.shape[0]  # Get a quantity for how many times each nerve fired
        average_ISI = np.zeros(spikes.shape[0], )

        if (neuron_fire_count < 2):  # This must be a neuron that fired at least twice (so a delta exists)
            spike_deltas = []
            average_ISI[i] = 0
        else:
            spike_deltas = calculate_spike_deltas(neuron_fire_count, spike_times)
            average_ISI[i] = sum(spike_deltas) / len(spike_deltas)

        if metadata[i]['iSA1'] == 1:
            afferent_stats['sa']['id_range'].append(i)
            afferent_stats['sa']['isi'][i] = average_ISI[i]
            afferent_stats['sa']['fire_count'][i] = neuron_fire_count
            afferent_stats['sa']['spike_deltas'][i] = np.array(spike_deltas)
            afferent_stats['sa']['locations'][i] = metadata[i]['location']

        elif metadata[i]['iRA'] == 1:
            afferent_stats['ra']['id_range'].append(i)
            afferent_stats['ra']['isi'][i] = average_ISI[i]
            afferent_stats['ra']['fire_count'][i] = neuron_fire_count
            afferent_stats['ra']['spike_deltas'][i] = np.array(spike_deltas)
            afferent_stats['ra']['locations'][i] = metadata[i]['location']

        elif metadata[i]['iPC'] == 1:
            afferent_stats['pc']['id_range'].append(i)
            afferent_stats['pc']['isi'][i] = average_ISI[i]
            afferent_stats['pc']['fire_count'][i] = neuron_fire_count
            afferent_stats['pc']['spike_deltas'][i] = np.array(spike_deltas)
            afferent_stats['pc']['locations'][i] = metadata[i]['location']

    afferent_stats['sa']['neuron_count'] = len(afferent_stats['sa']['id_range'])
    afferent_stats['ra']['neuron_count'] = len(afferent_stats['ra']['id_range'])
    afferent_stats['pc']['neuron_count'] = len(afferent_stats['pc']['id_range'])

    return afferent_stats


def plot_spikes(afferent_stats=None, metric='isi', ylabel='', title_addendum=''):
    """
    Function expects dictionaries where keys are the neuron ID and values are a metric
    User can specify what the y-axis data is with 'metric' keyword
    'isi' for ISI, 'fire_count' for number of firings
    Additional Parameters are for labeling axis and title of plot
    """

    width = 1
    y_axis_limit = 5

    plt.bar(afferent_stats['sa'][metric].keys(), afferent_stats['sa'][metric].values(), width, color='g', label='SA')
    plt.bar(afferent_stats['ra'][metric].keys(), afferent_stats['ra'][metric].values(), width, color='b', label='RA')
    plt.bar(afferent_stats['pc'][metric].keys(), afferent_stats['pc'][metric].values(), width, color='orange',
            label='PC')
    plt.legend(loc="upper left")
    plt.xlabel('Neuron ID')
    plt.ylabel(ylabel)
    if metric == 'isi':  # For mass/sweep plotting, keep the y-axis limit consistent
        plt.ylim(top=y_axis_limit)
    plt.title(f'{ylabel} vs. Neuron ID {title_addendum}')
    plt.show()


def plot_isi_count_histogram(neuron_id, afferent_stats, n_bins=20):
    """
    Function plots a histogram of an individual neuron's ISI.
    (Checks the id for the type of afferent first)
    """

    afferent_type = None
    sa_range, ra_range, pc_range = get_afferent_ranges(afferent_stats)

    afferent_type = get_afferent_type(neuron_id, afferent_stats)

    if neuron_id in sa_range:
        plt.hist(afferent_stats[afferent_type]['spike_deltas'][neuron_id], bins=n_bins, color='g')
    elif neuron_id in ra_range:
        plt.hist(afferent_stats[afferent_type]['spike_deltas'][neuron_id], bins=n_bins, color='b')
    elif neuron_id in pc_range:
        plt.hist(afferent_stats[afferent_type]['spike_deltas'][neuron_id], bins=n_bins, color='orange')
    else:
        print('Error - neuron_id does not correspond to SA, RA, or PC neuron.')

    plt.title(f"Neuron #{neuron_id} ({afferent_type}) ISI Histogram with {n_bins} bins")
    plt.xlabel('ISI Time (sec)')
    plt.ylabel('ISI Count')
    plt.show()


def plot_noise_sweep(dir_to_sweep, trial_filenames, trq_sensor_no=0):
    '''
    Function plots noise sweep data for a trial; accepts a directory to parse
    *To parse a directory, provide a "sweep_dir" folder
    *Use nested=True if the trial .mat file is nested (i.e. such as the noise sweep directories)
    :param trial_filenames: custom list of filenames the user would like to specifically pull from (optional)
    :param trq_sensor_no: if using trq sensor data, select the sensor to use (0-2) (optional)

    *Function uses regular expression to find noise values in the title of nested directories
    '''

    import os
    import re

    for subdir, dirs, files in os.walk(dir_to_sweep):
        for file in files:
            if file in trial_filenames:  # Matches the trial we want
                noise_profile = ''

                if "trq" in file:
                    afferent_stats = load_isi_stats(str(subdir + '/'), file)[trq_sensor_no]
                    noise_profile = f'(sensor #{trq_sensor_no})'
                elif "ftsn" in file:
                    afferent_stats = load_isi_stats(str(subdir + '/'), file)[0]

                regex_negative = re.search('minus(\d+)', subdir)
                regex_positive = re.search('noise_(\d+)', subdir)
                if regex_negative:
                    noise_profile = str('-' + regex_negative.group(1) + 'dB noise ' + noise_profile)
                elif regex_positive:
                    noise_profile = str(regex_positive.group(1) + 'dB noise ' + noise_profile)

                plot_spikes(afferent_stats, ylabel='Average ISI (sec)', title_addendum=noise_profile)


def probability_distribution(data, n_bins=10, plotted_data='', show_bins=False, y_axis_limit=1, x_axis_limit=0,
                             plot_title='ISI Probability Distribution', xlabel='Inter-Spike Time (sec)'):
    """
    :param xlabel: desired x label for when not plotting ISI
    :param plot_title: desired title for when not plotting ISI
    :param data: a 1D array of aggregated spike_deltas (across neurons, afferent type, noise profile, etc.)
    :param n_bins: preferred bin count, or ranges for bins. see https://numpy.org/doc/stable/reference/generated/numpy.histogram.html
    :param plotted_data: appends to the plot title to explicity show what was plotted
    :param show_bins: prints out the bins calculated for plotting
    :param y_axis_limit: sets the upper limit of the y-axis on plots, defaults to 1, set to 0 to scale with data (optional)
    :param x_axis_limit: sets the upper limit of the x-axis on plots, defaults to 0 which scales the axis with the data
    :return: heights of probability distribution
    """

    #  If the values in data exceed the upper n_bins limit, an error will be thrown.
    if type(n_bins).__module__ == np.__name__:
        if (len(data[data < n_bins[-1]])) == 0:
            print('WARNING: All values read from data exceed the upper n_bins limit. Switching to default (n_bins=10).')
            n_bins = 10

    heights, bins = np.histogram(data, bins=n_bins)

    heights = heights / sum(heights)
    if (np.isnan(np.sum(heights))):
        print(f'NaN detected in calculation. This most likely means some neurons did not fire. Removing NaNs.')
        heights = heights[~np.isnan(heights)]

    plt.bar(bins[:-1], heights, width=(max(bins) - min(bins)) / len(bins), alpha=0.5)
    plt.title(f'{plot_title} {plotted_data}')
    plt.xlabel(xlabel)
    plt.ylabel('Probability of Spiking')
    if x_axis_limit > 0:
        plt.xlim(right=x_axis_limit)
    if y_axis_limit == 0:
        plt.ylim(top=np.max(heights) * 1.10)  # Set the y-limit to a little above the highest height
    else:
        plt.ylim(top=y_axis_limit)
    plt.show()
    if show_bins == True:
        print(bins)

    return heights


def neuron_probability_distribution(afferent_stats, neuron_id=0, n_bins=20, show_plot=True, show_bins=False,
                                    y_axis_limit=1, x_axis_limit=0):
    """
    Function computes and plots the probability distribution for ISIs for a single neuron
    :param afferent_stats: dictionary with keys/values per calculate_afferet_isi_stats() documentation
    :param neuron_id: ID for the neuron being analyzed
    :param n_bins: desired number of bins for histogramming
    :param show_plot: boolean to determine if plot is shown
    :param show_bins: boolean to determine if bins are printed after running
    :param y_axis_limit: sets the upper limit of the y-axis on plots, defaults to 1, set to 0 to scale with data (optional)
    :param x_axis_limit: sets the upper limit of the x-axis on plots, defaults to 0 which scales the axis with the data
    :return: heights of probability distribution
    """

    total_isi_time = 0
    colors = {'sa': 'b', 'ra': 'g', 'pc': 'orange'}

    #  Record the afferent type (and corresponding color) for this neuron (referenced with ID)
    afferent_type = None
    color = None

    #  Retrieve ranges for afferent type to determine the neuron's afferent type

    afferent_type = get_afferent_type(neuron_id, afferent_stats)
    color = colors[afferent_type]

    heights, bins = np.histogram(afferent_stats[afferent_type]['spike_deltas'][neuron_id], bins=n_bins)
    heights = heights / sum(heights)
    if (np.isnan(np.sum(heights))):
        print(f'NaN detected in calculation for neuron {neuron_id}. This most likely means this neuron did not fire.')
        return

    if show_plot == True:
        plt.bar(bins[:-1], heights, width=(max(bins) - min(bins)) / len(bins), color=color, alpha=0.5)
        plt.title(f'ISI Probability Distribution for neuron #{neuron_id} ({afferent_type})')
        plt.xlabel('Inter-Spike Time (sec)')
        plt.ylabel('Probability')
        if x_axis_limit > 0:
            plt.xlim(right=x_axis_limit)
        plt.ylim(top=y_axis_limit)
        plt.show()
    if show_bins == True:
        print(bins)
    return heights


def trial_isi_probability_distribution(n_bins, data_dir, trial_filenames=[], trq_sensor_no=0, neuron_id=None,
                                       afferent_type=None,
                                       y_axis_limit=1, x_axis_limit=0):
    """
    Function creates isi probability distribtions across several trials.
    :param n_bins:          - number of histogram bins
    :param data_dir:        - directory with .mat trial files
    :param trial_filenames: - custom list of filenames the user would like to specifically pull from (optional)
    :param trq_sensor_no:   - if using trq sensor data, select the sensor to use (0-2) (optional)
    :param neuron_id:       - selects this neuron_id across all trials (optional)
    :param afferent_type:   - selects this afferent type (sa, ra, pc) to compare across trials (optional)
    :param y_axis_limit:    - sets the upper limit of the y-axis on plots, defaults to 1, set to 0 to scale with data (optional)
    """

    plotted_data = ''
    data = np.array(())
    heights = None

    #  If an empty list is passed for trial_filenames, then all .mat files within data_dir will be used
    if len(trial_filenames) == 0:
        for subdir, dirs, files in os.walk(data_dir):
            for file in files:
                if file.endswith(".mat"):
                    trial_filenames.append(file)

    #  Walk through all nested directories and and aggregate/process data from files found in trial_filenames
    for subdir, dirs, files in os.walk(data_dir):
        for file in files:
            if file in trial_filenames:
                if "trq" in file:
                    sensor_stats = load_isi_stats(str(subdir + '/'), file)
                    afferent_stats = sensor_stats[trq_sensor_no]
                    plotted_data = f' | (sensor #{trq_sensor_no})'
                elif "ftsn" in file:
                    afferent_stats = load_isi_stats(str(subdir + '/'), file)[0]
                    plotted_data = ''
                else:
                    # If neither ftsn nor trq is in the .mat file, default to ftsn behavior
                    afferent_stats = load_isi_stats(str(subdir + '/'), file)[0]
                    plotted_data = ''

                if (afferent_type is not None) and (neuron_id is not None):
                    print(f'afferent_type = {afferent_type}')
                    print(f'neuron_id = {neuron_id}')
                    print(
                        f'Error: Cannot aggregate data using both neuron_id and afferent_type. '
                        f'Expecting at least one to be set to None.')
                    return None

                #  Afferent Mode - Aggregates data from one afferent type across all data ('sa', 'ra', 'pc')
                elif (afferent_type is not None) and (neuron_id is None):
                    afferent_spike_deltas = afferent_stats[afferent_type]['spike_deltas']

                    #  afferent_spike_deltas still has indices for ALL afferent types. Truncate it to the ones we want:
                    #  properly-written indices in the list for this afferent will be numpy arrays, others will be int
                    afferent_spike_deltas = [spike for spike in afferent_spike_deltas if not isinstance(spike, int)]

                    flat_spike_deltas = flatten_arrays([afferent_spike_deltas])
                    data = np.hstack((data, flat_spike_deltas))

                    plotted_data = f'[{afferent_type} neurons] | spikes = {data.shape[0]}' + plotted_data

                # Neuron Mode - Aggregates data from a single neuron across several trials
                elif (neuron_id is not None) and (afferent_type is None):
                    afferent_type = get_afferent_type(neuron_id, afferent_stats)
                    neuron_spike_deltas = afferent_stats[afferent_type]['spike_deltas'][neuron_id]
                    data = np.hstack((data, neuron_spike_deltas))
                    plotted_data = f'[ID = {neuron_id}] | spikes = {data.shape[0]}' + plotted_data
                    afferent_type = None  # Set to None to avoid a warning later in execution

                # General Mode - Takes all data from across all trials neuron_spike_deltas
                elif (afferent_type is None) and (neuron_id is None):
                    sa_range, ra_range, pc_range = get_afferent_ranges(afferent_stats)

                    sa_spike_deltas = afferent_stats['sa']['spike_deltas'][min(sa_range):max(sa_range) + 1]
                    ra_spike_deltas = afferent_stats['ra']['spike_deltas'][min(ra_range):max(ra_range) + 1]
                    pc_spike_deltas = afferent_stats['pc']['spike_deltas'][min(pc_range):max(pc_range) + 1]

                    flat_spike_deltas = flatten_arrays((sa_spike_deltas, ra_spike_deltas, pc_spike_deltas))

                    data = np.hstack((data, flat_spike_deltas))
                    plotted_data = f'[All afferent types | spikes = {data.shape[0]}]' + plotted_data

                # Sensor Mode - Aggregates data across different sensors (trq only)
                # Not built at this time, but would repeat the above mode(s) for each sensor

                #  Debug to make sure we our data contains information from ONLY neurons that did spike
                # print(f'Data concatenated from {file}')
                # print('Spike count: ', data.shape)
                # print('Zero count: ', len(np.argwhere(data == 0)))
                # print('Nonzero count: ', len(np.argwhere(data != 0)))
                # data = data[np.where(data != 0)]

    heights = probability_distribution(data, n_bins=n_bins, plotted_data=plotted_data,
                                       y_axis_limit=y_axis_limit, x_axis_limit=x_axis_limit)

    return heights


def trial_distance_probabilty_distribution(data_dir, trial_filenames, n_bins, reference_point=(0, 0), trq_sensor_no=0,
                                           neuron_id=None,
                                           afferent_type=None, y_axis_limit=1):
    """
        Function creates probability distributions for distance from stimulus across several trials.
        :param n_bins:          - number of histogram bins to group data into
        :param reference_point: - tuple; representing the coordinates of a stimulus on the hand coordinate system
        :param data_dir:        - directory with .mat trial files
        :param trial_filenames: - custom list of filenames the user would like to specifically pull from (optional)
        :param trq_sensor_no:   - if using trq sensor data, select the sensor to use (0-2) (optional)
        :param neuron_id:       - selects this neuron_id across all trials (optional)
        :param afferent_type:   - selects this afferent type (sa, ra, pc) to compare across trials (optional)
        :param y_axis_limit:    - sets the upper limit of the y-axis on plots, defaults to 1, set to 0 to scale with data (optional)
        """

    plotted_data = ''
    data = np.array(())
    heights = None

    #  If an empty list is passed for trial_filenames, then all .mat files within data_dir will be used
    if len(trial_filenames) == 0:
        for subdir, dirs, files in os.walk(data_dir):
            for file in files:
                if file.endswith(".mat"):
                    trial_filenames.append(file)

    #  Walk through all nested directories and and aggregate/process data from files found in trial_filenames
    for subdir, dirs, files in os.walk(data_dir):
        for file in files:
            if file in trial_filenames:
                if "trq" in file:
                    sensor_stats = load_isi_stats(str(subdir + '/'), file)
                    afferent_stats = sensor_stats[trq_sensor_no]
                    plotted_data = f' | (sensor #{trq_sensor_no})'
                elif "ftsn" in file:
                    afferent_stats = load_isi_stats(str(subdir + '/'), file)[0]
                    plotted_data = ''

                if (afferent_type is not None) and (neuron_id is not None):
                    print(f'afferent_type = {afferent_type}')
                    print(f'neuron_id = {neuron_id}')
                    print(
                        f'Error: Cannot aggregate data using both neuron_id and afferent_type. '
                        f'Expecting at least one to be set to None.')
                    return None

                #  Afferent Mode - Aggregates data from one afferent type across all data ('sa', 'ra', 'pc')
                elif (afferent_type is not None) and (neuron_id is None):
                    afferent_spike_locations = afferent_stats[afferent_type]['locations']

                    sa_range, ra_range, pc_range = get_afferent_ranges(afferent_stats)
                    afferent_range = sa_range if afferent_type == 'sa' else ra_range if afferent_type == 'ra' else pc_range

                    truncated_afferent_range = afferent_spike_locations[min(afferent_range):max(afferent_range) + 1]

                    data = np.zeros((truncated_afferent_range.shape[0],))
                    spiking_neurons = []
                    for i in range(data.shape[0]):
                        spiking_neurons.append(neuron_spiked(afferent_range[i], afferent_stats))  # tracks spikings
                        data[i] = calculate_magnitude(neuron_x=truncated_afferent_range[i][0],
                                                      neuron_y=truncated_afferent_range[i][1],
                                                      center_x=reference_point[0], center_y=reference_point[1])

                    data = data[spiking_neurons]  # Drops the neurons that didn't spike
                    plotted_data = f'[{afferent_type} neurons] | spikes = {data.shape[0]}' + plotted_data

                # Neuron Mode - Aggregates data from a single neuron across several trials
                elif (neuron_id is not None) and (afferent_type is None):
                    if not neuron_spiked(neuron_id, afferent_stats):
                        print(f'Neuron #{neuron_id} did not have an ISI. Returning None.')
                        return None

                    afferent_type = get_afferent_type(neuron_id, afferent_stats)
                    neuron_location = afferent_stats[afferent_type]['locations'][neuron_id]
                    neuron_location = calculate_magnitude(neuron_x=neuron_location[0], neuron_y=neuron_location[1],
                                                          center_x=reference_point[0], center_y=reference_point[1])

                    data = np.hstack((data, neuron_location))

                    plotted_data = f'[ID = {neuron_id}] | spikes = {data.shape[0]}' + plotted_data
                    afferent_type = None  # Set to None to avoid a warning later in execution

                # General Mode - Takes all data from across all trials neuron_spike_deltas
                elif (afferent_type is None) and (neuron_id is None):
                    sa_range, ra_range, pc_range = get_afferent_ranges(afferent_stats)

                    sa_distances = afferent_stats['sa']['locations'][min(sa_range):max(sa_range) + 1]
                    ra_distances = afferent_stats['ra']['locations'][min(ra_range):max(ra_range) + 1]
                    pc_distances = afferent_stats['pc']['locations'][min(pc_range):max(pc_range) + 1]

                    distances = flatten_arrays((sa_distances, ra_distances, pc_distances)).reshape(-1, 2)

                    neuron_locations = np.zeros((distances.shape[0],))
                    spiking_neurons = []
                    for i in range(neuron_locations.shape[0]):
                        spiking_neurons.append(neuron_spiked(i, afferent_stats))  # keeps a list of neurons that spiked
                        x_coordinate = distances[i][0]
                        y_coordinate = distances[i][1]
                        neuron_locations[i] = calculate_magnitude(neuron_x=x_coordinate, neuron_y=y_coordinate,
                                                                  center_x=reference_point[0],
                                                                  center_y=reference_point[1])

                    data = np.hstack((data, neuron_locations[spiking_neurons]))  # Drops the neurons that didn't spike

                    plotted_data = f'[All afferent types | spikes = {data.shape[0]}]' + plotted_data

    heights = probability_distribution(data, n_bins=n_bins, plotted_data=plotted_data,
                                       y_axis_limit=y_axis_limit, plot_title='Distance Metric',
                                       xlabel=f'Distance from point {str(reference_point)}')

    return heights


def kl_divergence(p, q):
    p[p == 0] = 1e-10
    q[q == 0] = 1e-10

    kl_div_pq = np.sum(np.multiply(p, np.log(p) - np.log(q)))
    kl_div_qp = np.sum(np.multiply(q, np.log(q) - np.log(p)))

    return kl_div_pq + kl_div_qp
